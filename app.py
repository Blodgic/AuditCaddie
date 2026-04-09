"""
AuditCaddie OSS
===============
Self-hosted compliance scanning for AWS + GitHub.
Single-user. BYOK AI. 10 minutes to running.

Docs:       https://github.com/Blodgic/AuditCaddie
Commercial: https://auditcaddie.com
License:    MIT
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
log = logging.getLogger("auditcaddie")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_DIR   = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
STATIC_DIR = BASE_DIR / "static"
TMPL_DIR   = BASE_DIR / "templates"
DB_PATH    = DATA_DIR / "auditcaddie.db"
DATA_DIR.mkdir(exist_ok=True)

VERSION = "1.0.0"
UPGRADE_URL = "https://auditcaddie.com/pricing"
OSS_FRAMEWORK_LIMIT = 2   # OSS: scan up to 2 frameworks; Enterprise: unlimited

# Enterprise features — OSS shows upgrade notice for these
ENTERPRISE_FEATURES = {
    "multi_user":        "Team Collaboration",
    "fieldguide":        "Fieldguide Integration",
    "sso":               "SSO / SAML Authentication",
    "custom_frameworks": "Custom Framework Builder",
    "auditor_portal":    "Auditor Portal & Shared Workspaces",
    "trust_center":      "White-Label Trust Center",
    "api_ci_cd":         "CI/CD API Access",
    "advanced_ai":       "Advanced AI Evidence Mapping",
    "priority_support":  "Priority Support & SLA",
}

# ── Database ───────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                id          TEXT PRIMARY KEY,
                created_at  TEXT DEFAULT (datetime('now')),
                framework   TEXT,
                scan_name   TEXT,
                status      TEXT DEFAULT 'pending',
                aws_account TEXT,
                github_actor TEXT,
                results     TEXT
            );
            CREATE TABLE IF NOT EXISTS policies (
                id          TEXT PRIMARY KEY,
                created_at  TEXT DEFAULT (datetime('now')),
                scan_id     TEXT,
                control_id  TEXT,
                policy_name TEXT,
                model_used  TEXT,
                content     TEXT
            );
            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
        """)

# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AuditCaddie OSS",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def startup():
    init_db()
    log.info("AuditCaddie OSS %s started — http://localhost:%s", VERSION, os.getenv("PORT", "8080"))

# ── Pydantic Models ────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    framework: str                          # template slug
    scan_name: str = ""
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "us-east-1"
    github_token: str = ""
    github_org: str = ""
    run_aws: bool = True
    run_github: bool = True

class PolicyRequest(BaseModel):
    scan_id: str = ""
    control_id: str = ""
    policy_name: str
    prompt: str
    model: str = ""

class SettingsPayload(BaseModel):
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "us-east-1"
    github_token: str = ""
    github_org: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ai_model: str = "gpt-4o"

# ── Health & Meta ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": VERSION, "product": "AuditCaddie OSS"}


@app.get("/api/config/status")
def config_status():
    """Returns which integrations are currently configured."""
    from ai_generator import check_ai_configured
    ai = check_ai_configured()
    aws_key = os.getenv("AWS_ACCESS_KEY_ID") or _get_setting("aws_access_key")
    gh_token = os.getenv("GITHUB_TOKEN") or _get_setting("github_token")
    return {
        "aws": bool(aws_key),
        "github": bool(gh_token),
        "ai": ai,
        "version": VERSION,
        "upgrade_url": UPGRADE_URL,
    }

# ── Settings ───────────────────────────────────────────────────────────────────

def _get_setting(key: str) -> str:
    with get_db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else ""

def _set_setting(key: str, value: str):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))

@app.post("/api/settings")
def save_settings(payload: SettingsPayload):
    """Save credentials to local SQLite (encrypted at rest by OS filesystem)."""
    fields = payload.dict()
    for key, val in fields.items():
        if val:
            _set_setting(key, val)
            # Also set in process env for immediate effect
            env_map = {
                "aws_access_key": "AWS_ACCESS_KEY_ID",
                "aws_secret_key": "AWS_SECRET_ACCESS_KEY",
                "aws_region": "AWS_DEFAULT_REGION",
                "github_token": "GITHUB_TOKEN",
                "openai_api_key": "OPENAI_API_KEY",
                "anthropic_api_key": "ANTHROPIC_API_KEY",
                "ai_model": "AI_MODEL",
            }
            if key in env_map:
                os.environ[env_map[key]] = val
    return {"ok": True}

@app.get("/api/settings")
def get_settings():
    """Return saved settings (keys masked)."""
    keys = ["aws_access_key", "aws_region", "github_token", "github_org", "ai_model"]
    result = {}
    for key in keys:
        val = _get_setting(key) or os.getenv(key.upper(), "")
        result[key] = ("*" * 8 + val[-4:]) if len(val) > 4 else ("***" if val else "")
    return result

# ── Templates ──────────────────────────────────────────────────────────────────

@app.get("/api/templates")
def list_templates():
    templates = []
    for path in sorted(TMPL_DIR.glob("*.yaml")):
        try:
            data = yaml.safe_load(path.read_text())
            templates.append({
                "slug": data.get("slug", path.stem),
                "name": data.get("name", path.stem),
                "framework": data.get("framework", ""),
                "framework_version": data.get("framework_version", ""),
                "target_audience": data.get("target_audience", ""),
                "estimated_hours_manual": data.get("estimated_hours_manual"),
                "estimated_hours_with_caddie": data.get("estimated_hours_with_caddie"),
                "control_count": len(data.get("controls", [])),
                "description": (data.get("description") or "")[:200],
            })
        except Exception as e:
            log.warning("Could not parse template %s: %s", path.name, e)
    return templates


@app.get("/api/templates/{slug}")
def get_template(slug: str):
    path = TMPL_DIR / f"{slug}.yaml"
    if not path.exists():
        raise HTTPException(404, f"Template '{slug}' not found")
    return yaml.safe_load(path.read_text())

# ── Scans ──────────────────────────────────────────────────────────────────────

def _resolve_creds(req_val: str, env_key: str, db_key: str) -> str:
    return req_val or os.getenv(env_key, "") or _get_setting(db_key)

def _run_scan_task(scan_id: str, req: ScanRequest):
    """Background task: runs all scanners and stores results."""
    from scanner.aws_checks import run_aws_scan
    from scanner.github_checks import run_github_scan

    # Load template to get required checks
    tmpl_path = TMPL_DIR / f"{req.framework}.yaml"
    if tmpl_path.exists():
        tmpl = yaml.safe_load(tmpl_path.read_text())
        aws_checks = tmpl.get("aws_checks", [])
    else:
        aws_checks = []

    combined: dict = {"aws": None, "github": None, "framework": req.framework}

    if req.run_aws:
        aws_key = _resolve_creds(req.aws_access_key, "AWS_ACCESS_KEY_ID", "aws_access_key")
        aws_secret = _resolve_creds(req.aws_secret_key, "AWS_SECRET_ACCESS_KEY", "aws_secret_key")
        region = req.aws_region or _get_setting("aws_region") or "us-east-1"
        combined["aws"] = run_aws_scan(aws_checks, aws_key or None, aws_secret or None, region)

    if req.run_github:
        gh_token = _resolve_creds(req.github_token, "GITHUB_TOKEN", "github_token")
        gh_org = req.github_org or _get_setting("github_org") or None
        combined["github"] = run_github_scan(gh_token, gh_org)

    with get_db() as conn:
        conn.execute(
            "UPDATE scans SET status=?, results=?, aws_account=?, github_actor=? WHERE id=?",
            (
                "complete",
                json.dumps(combined),
                combined.get("aws", {}).get("account_id", "") if combined.get("aws") else "",
                combined.get("github", {}).get("actor", "") if combined.get("github") else "",
                scan_id,
            ),
        )
    log.info("Scan %s complete", scan_id)


def _get_used_frameworks() -> list[str]:
    """Return distinct frameworks that have completed scans."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT framework FROM scans WHERE status='complete' ORDER BY MIN(created_at)"
        ).fetchall()
    return [r["framework"] for r in rows]


@app.get("/api/frameworks/usage")
def framework_usage():
    """Return which frameworks have been used and how many remain."""
    used = _get_used_frameworks()
    return {
        "used": used,
        "used_count": len(used),
        "limit": OSS_FRAMEWORK_LIMIT,
        "remaining": max(0, OSS_FRAMEWORK_LIMIT - len(used)),
        "upgrade_url": UPGRADE_URL,
    }


@app.post("/api/scan")
def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    # Enforce OSS framework limit
    used = _get_used_frameworks()
    if req.framework not in used and len(used) >= OSS_FRAMEWORK_LIMIT:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "framework_limit_reached",
                "message": f"AuditCaddie OSS includes {OSS_FRAMEWORK_LIMIT} frameworks. "
                           f"You've already used: {', '.join(used)}. "
                           f"Upgrade to Enterprise for all 5 frameworks.",
                "used": used,
                "limit": OSS_FRAMEWORK_LIMIT,
                "upgrade_url": UPGRADE_URL,
            },
        )

    scan_id = str(uuid.uuid4())[:8]
    name = req.scan_name or f"{req.framework} — {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    with get_db() as conn:
        conn.execute(
            "INSERT INTO scans (id, framework, scan_name, status) VALUES (?,?,?,?)",
            (scan_id, req.framework, name, "running"),
        )
    background_tasks.add_task(_run_scan_task, scan_id, req)
    return {"scan_id": scan_id, "status": "running"}


@app.get("/api/scan/{scan_id}")
def get_scan(scan_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Scan not found")
    data = dict(row)
    if data.get("results"):
        data["results"] = json.loads(data["results"])
    return data


@app.get("/api/scans")
def list_scans(limit: int = 20):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, framework, scan_name, status, aws_account, github_actor "
            "FROM scans ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


@app.delete("/api/scan/{scan_id}")
def delete_scan(scan_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM scans WHERE id=?", (scan_id,))
        conn.execute("DELETE FROM policies WHERE scan_id=?", (scan_id,))
    return {"ok": True}

# ── AI Policy Generation ───────────────────────────────────────────────────────

@app.post("/api/generate-policy")
def generate_policy(req: PolicyRequest):
    from ai_generator import generate_policy_doc
    result = generate_policy_doc(req.prompt, req.policy_name, req.model or None)
    if not result["ok"]:
        raise HTTPException(500, result["error"])

    policy_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        conn.execute(
            "INSERT INTO policies (id, scan_id, control_id, policy_name, model_used, content) VALUES (?,?,?,?,?,?)",
            (policy_id, req.scan_id, req.control_id, req.policy_name,
             result.get("model", ""), result.get("content", "")),
        )
    return {
        "policy_id": policy_id,
        "policy_name": req.policy_name,
        "content": result["content"],
        "model": result.get("model"),
        "tokens": result.get("tokens"),
    }


@app.get("/api/policies")
def list_policies(scan_id: str = ""):
    with get_db() as conn:
        if scan_id:
            rows = conn.execute(
                "SELECT id, created_at, scan_id, control_id, policy_name, model_used FROM policies WHERE scan_id=? ORDER BY created_at DESC",
                (scan_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, created_at, scan_id, control_id, policy_name, model_used FROM policies ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
    return [dict(r) for r in rows]


@app.get("/api/policies/{policy_id}")
def get_policy(policy_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM policies WHERE id=?", (policy_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Policy not found")
    return dict(row)

# ── Enterprise Feature Gate ────────────────────────────────────────────────────

@app.get("/api/enterprise/{feature}")
def enterprise_feature(feature: str):
    name = ENTERPRISE_FEATURES.get(feature, feature.replace("_", " ").title())
    return {
        "available": False,
        "feature": feature,
        "name": name,
        "message": f"{name} is available in AuditCaddie Enterprise.",
        "upgrade_url": UPGRADE_URL,
        "plan": "oss",
    }

# ── Report ─────────────────────────────────────────────────────────────────────

@app.get("/api/report/{scan_id}", response_class=HTMLResponse)
def get_report(scan_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM scans WHERE id=?", (scan_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Scan not found")

    scan = dict(row)
    results = json.loads(scan["results"]) if scan.get("results") else {}
    tmpl_path = TMPL_DIR / f"{scan['framework']}.yaml"
    tmpl = yaml.safe_load(tmpl_path.read_text()) if tmpl_path.exists() else {}

    return _render_report(scan, results, tmpl)


def _render_report(scan: dict, results: dict, tmpl: dict) -> str:
    aws_res = results.get("aws", {}) or {}
    gh_res  = results.get("github", {}) or {}

    all_checks = []
    for r in (aws_res.get("results") or []):
        all_checks.append(r)
    for r in (gh_res.get("results") or []):
        all_checks.append(r)

    total = len(all_checks)
    passed = sum(1 for c in all_checks if c["status"] == "pass")
    failed = sum(1 for c in all_checks if c["status"] == "fail")
    score = int((passed / total * 100)) if total else 0

    score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"

    def badge(status):
        colors = {"pass": "#22c55e", "fail": "#ef4444", "warn": "#f59e0b", "error": "#94a3b8"}
        labels = {"pass": "PASS", "fail": "FAIL", "warn": "WARN", "error": "ERR"}
        c = colors.get(status, "#94a3b8")
        l = labels.get(status, status.upper())
        return f'<span style="background:{c};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600">{l}</span>'

    check_rows = "\n".join(
        f"""<tr>
          <td style="padding:10px 12px">{badge(c['status'])}</td>
          <td style="padding:10px 12px;font-weight:500">{c['title']}</td>
          <td style="padding:10px 12px;color:#94a3b8;font-size:13px">{c.get('detail','')}</td>
          <td style="padding:10px 12px;color:#f59e0b;font-size:12px">{c.get('remediation','')}</td>
        </tr>"""
        for c in all_checks
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AuditCaddie Compliance Report — {scan['scan_name']}</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:0}}
  .container{{max-width:1000px;margin:0 auto;padding:40px 24px}}
  .header{{border-bottom:1px solid #1e293b;padding-bottom:24px;margin-bottom:32px}}
  .logo{{font-size:13px;color:#3b82f6;font-weight:600;letter-spacing:.05em;text-transform:uppercase}}
  h1{{font-size:28px;margin:8px 0 4px;color:#f8fafc}}
  .meta{{color:#64748b;font-size:14px}}
  .score-card{{background:#1e293b;border-radius:12px;padding:32px;text-align:center;margin-bottom:32px;border:1px solid #334155}}
  .score-num{{font-size:72px;font-weight:700;color:{score_color};line-height:1}}
  .score-label{{color:#94a3b8;margin-top:8px;font-size:16px}}
  .stats{{display:flex;gap:24px;justify-content:center;margin-top:24px}}
  .stat{{text-align:center}}
  .stat-num{{font-size:28px;font-weight:700}}
  .pass{{color:#22c55e}}.fail{{color:#ef4444}}.warn{{color:#f59e0b}}
  .stat-label{{color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
  table{{width:100%;border-collapse:collapse;background:#1e293b;border-radius:12px;overflow:hidden;border:1px solid #334155}}
  th{{background:#0f172a;padding:12px;text-align:left;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#64748b}}
  tr:nth-child(even){{background:#1a2540}}
  .footer{{text-align:center;margin-top:48px;color:#475569;font-size:12px;padding-top:24px;border-top:1px solid #1e293b}}
  .upgrade{{background:linear-gradient(135deg,#1e3a5f,#1e293b);border:1px solid #3b82f6;border-radius:12px;padding:20px 24px;margin-top:32px;display:flex;align-items:center;gap:16px}}
  .upgrade-text{{flex:1}}
  .upgrade-text h3{{margin:0 0 4px;color:#93c5fd;font-size:15px}}
  .upgrade-text p{{margin:0;color:#64748b;font-size:13px}}
  .upgrade-btn{{background:#3b82f6;color:#fff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;white-space:nowrap}}
  @media print{{body{{background:#fff;color:#000}}.upgrade{{display:none}}}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">AuditCaddie OSS</div>
    <h1>{scan['scan_name']}</h1>
    <div class="meta">
      Framework: {tmpl.get('name', scan['framework'])} &nbsp;·&nbsp;
      Generated: {scan['created_at']} UTC &nbsp;·&nbsp;
      AWS Account: {aws_res.get('account_id','N/A')} &nbsp;·&nbsp;
      GitHub: {gh_res.get('actor','N/A')}
    </div>
  </div>

  <div class="score-card">
    <div class="score-num">{score}%</div>
    <div class="score-label">Readiness Score</div>
    <div class="stats">
      <div class="stat"><div class="stat-num pass">{passed}</div><div class="stat-label">Passed</div></div>
      <div class="stat"><div class="stat-num fail">{failed}</div><div class="stat-label">Failed</div></div>
      <div class="stat"><div class="stat-num warn">{total - passed - failed}</div><div class="stat-label">Warnings</div></div>
      <div class="stat"><div class="stat-num" style="color:#e2e8f0">{total}</div><div class="stat-label">Total Checks</div></div>
    </div>
  </div>

  <table>
    <thead><tr><th>Status</th><th>Control Check</th><th>Finding</th><th>Remediation</th></tr></thead>
    <tbody>{check_rows}</tbody>
  </table>

  <div class="upgrade">
    <div class="upgrade-text">
      <h3>Share this report with your auditor</h3>
      <p>Fieldguide integration, auditor portal, and team collaboration are available in AuditCaddie Enterprise.</p>
    </div>
    <a class="upgrade-btn" href="https://auditcaddie.com/pricing" target="_blank">Upgrade to Enterprise →</a>
  </div>

  <div class="footer">
    Generated by AuditCaddie OSS {VERSION} &nbsp;·&nbsp; auditcaddie.com &nbsp;·&nbsp; github.com/Blodgic/AuditCaddie<br>
    This report covers automated technical checks only. A qualified compliance professional should review before submission to auditors.
  </div>
</div>
</body>
</html>"""

# ── Frontend ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
@app.get("/{path:path}", response_class=HTMLResponse)
def frontend(path: str = ""):
    index = STATIC_DIR / "index.html"
    if index.exists():
        return HTMLResponse(index.read_text())
    return HTMLResponse("<h1>AuditCaddie OSS</h1><p>Static files not found.</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=os.getenv("DEV", "false").lower() == "true",
    )
