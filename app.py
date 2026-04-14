"""
AuditCaddie Community Edition
==============================
Self-hosted compliance scanning for AWS + GitHub.
Single-user. BYOK AI. 10 minutes to running.

Copyright 2026 BLODGIC Inc.
Licensed under the Apache License, Version 2.0
See LICENSE and NOTICE for full terms, trademark notice,
and community edition scope.

Docs:        https://github.com/Blodgic/AuditCaddie
Enterprise:  https://auditcaddie.com/pricing
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
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
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
            CREATE TABLE IF NOT EXISTS documents (
                id                TEXT PRIMARY KEY,
                created_at        TEXT DEFAULT (datetime('now')),
                original_filename TEXT,
                mime_type         TEXT,
                document_type     TEXT DEFAULT 'evidence',
                framework         TEXT,
                tags              TEXT DEFAULT '[]',
                file_content      BLOB,
                extracted_text    TEXT,
                status            TEXT DEFAULT 'pending',
                suggestions       TEXT,
                confirmed_controls TEXT,
                is_confirmed      INTEGER DEFAULT 0,
                user_overrode     INTEGER DEFAULT 0,
                tokens_used       INTEGER DEFAULT 0,
                error_msg         TEXT
            );
        """)
        # Migrate existing DBs — add tags column if missing
        cols = [r[1] for r in conn.execute("PRAGMA table_info(documents)").fetchall()]
        if "tags" not in cols:
            conn.execute("ALTER TABLE documents ADD COLUMN tags TEXT DEFAULT '[]'")

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
    _load_settings_into_env()
    log.info("AuditCaddie OSS %s started — http://localhost:%s", VERSION, os.getenv("PORT", "8080"))


def _load_settings_into_env():
    """On startup, promote DB-saved credentials into os.environ so they survive container restarts."""
    env_map = {
        "aws_access_key":    "AWS_ACCESS_KEY_ID",
        "aws_secret_key":    "AWS_SECRET_ACCESS_KEY",
        "aws_region":        "AWS_DEFAULT_REGION",
        "github_token":      "GITHUB_TOKEN",
        "github_org":        "GITHUB_ORG",
        "openai_api_key":    "OPENAI_API_KEY",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "ai_model":          "AI_MODEL",
    }
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
        for row in rows:
            env_key = env_map.get(row["key"])
            if env_key and row["value"] and not os.getenv(env_key):
                os.environ[env_key] = row["value"]
    except Exception as e:
        log.warning("Could not load settings from DB: %s", e)

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

class ConfirmPayload(BaseModel):
    control_ids: list[str]
    user_overrode: bool = False

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


# ── AI key verification (live test, cached 5 min) ─────────────────────────────
_ai_verify_cache: dict = {}   # { "openai": {ok, error, ts}, "anthropic": {ok, error, ts} }
_AI_VERIFY_TTL = 300          # seconds

def _verify_openai_key() -> dict:
    import time
    cached = _ai_verify_cache.get("openai", {})
    if cached and time.time() - cached.get("ts", 0) < _AI_VERIFY_TTL:
        return cached
    key = os.getenv("OPENAI_API_KEY") or _get_setting("openai_api_key")
    if not key:
        result = {"ok": False, "error": "No key configured", "ts": time.time()}
    else:
        try:
            from openai import OpenAI
            OpenAI(api_key=key).models.list()
            result = {"ok": True, "error": "", "ts": time.time()}
        except Exception as e:
            msg = str(e)
            if "401" in msg or "invalid_api_key" in msg or "Incorrect API key" in msg:
                msg = "Invalid API key"
            elif "429" in msg or "quota" in msg:
                msg = "Rate limit / quota exceeded"
            elif "billing" in msg:
                msg = "Billing issue — check OpenAI account"
            result = {"ok": False, "error": msg, "ts": time.time()}
    _ai_verify_cache["openai"] = result
    return result

def _verify_anthropic_key() -> dict:
    import time
    cached = _ai_verify_cache.get("anthropic", {})
    if cached and time.time() - cached.get("ts", 0) < _AI_VERIFY_TTL:
        return cached
    key = os.getenv("ANTHROPIC_API_KEY") or _get_setting("anthropic_api_key")
    if not key:
        result = {"ok": False, "error": "No key configured", "ts": time.time()}
    else:
        try:
            from anthropic import Anthropic
            Anthropic(api_key=key).models.list()
            result = {"ok": True, "error": "", "ts": time.time()}
        except Exception as e:
            msg = str(e)
            if "401" in msg or "invalid_x_api_key" in msg or "authentication" in msg.lower():
                msg = "Invalid API key"
            elif "429" in msg or "quota" in msg or "rate_limit" in msg:
                msg = "Rate limit / quota exceeded"
            elif "billing" in msg:
                msg = "Billing issue — check Anthropic account"
            result = {"ok": False, "error": msg, "ts": time.time()}
    _ai_verify_cache["anthropic"] = result
    return result

@app.get("/api/config/verify-ai")
def verify_ai():
    """Live-test both AI keys. Cached for 5 minutes to avoid repeated API calls."""
    openai   = _verify_openai_key()
    anthropic = _verify_anthropic_key()
    working = sum(1 for r in [openai, anthropic] if r["ok"])
    return {
        "openai":    {"ok": openai["ok"],    "error": openai["error"]},
        "anthropic": {"ok": anthropic["ok"], "error": anthropic["error"]},
        "working_count": working,
    }

@app.post("/api/config/verify-ai/invalidate")
def invalidate_ai_cache():
    """Clear the AI verification cache (called after saving new keys)."""
    _ai_verify_cache.clear()
    return {"ok": True}

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
    ai_keys_changed = False
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
            if key in ("openai_api_key", "anthropic_api_key"):
                ai_keys_changed = True
    # Bust the verification cache so the next status check re-tests the new keys
    if ai_keys_changed:
        _ai_verify_cache.clear()
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
            "SELECT framework FROM scans WHERE status='complete' GROUP BY framework ORDER BY MIN(created_at)"
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

# ── Framework Controls ─────────────────────────────────────────────────────────

@app.get("/api/frameworks/{slug}/controls")
def list_controls(slug: str):
    """Return all controls for a framework template, grouped by category."""
    path = TMPL_DIR / f"{slug}.yaml"
    if not path.exists():
        raise HTTPException(404, f"Framework '{slug}' not found")
    tmpl = yaml.safe_load(path.read_text())
    controls = tmpl.get("controls", [])
    # Group by category
    by_category: dict = {}
    for c in controls:
        cat = c.get("category", "General")
        by_category.setdefault(cat, []).append({
            "id": c["id"],
            "name": c["name"],
            "category": cat,
            "priority": c.get("priority", ""),
            "description": (c.get("description") or "")[:300],
            "free_templates": c.get("free_templates", []),
        })
    return {"framework": slug, "name": tmpl.get("name", slug), "categories": by_category}


# ── Free Policy Templates ──────────────────────────────────────────────────────

POLICIES_DIR = BASE_DIR / "docs" / "policies"

def _parse_policy_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown policy files (after any leading HTML comment)."""
    import re
    # Strip leading HTML comments (the attribution/license header)
    stripped = re.sub(r'^<!--[\s\S]*?-->\s*\n', '', content.strip())
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', stripped, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except Exception:
            pass
    return {}


@app.get("/api/free-policies/{framework}")
def list_free_policies(framework: str):
    """List all free policy templates for a given framework."""
    policy_dir = POLICIES_DIR / framework
    if not policy_dir.exists():
        raise HTTPException(404, f"No free policies found for framework '{framework}'")
    policies = []
    for path in sorted(policy_dir.glob("*.md")):
        content = path.read_text()
        meta = _parse_policy_frontmatter(content)
        policies.append({
            "filename": path.name,
            "title": meta.get("title", path.stem.replace("-", " ").title()),
            "controls": meta.get("controls", []),
            "framework": meta.get("framework", framework),
            "version": meta.get("version", "1.0"),
            "review_cycle": meta.get("review_cycle", "Annual"),
            "attribution": meta.get("attribution", "Free template provided by AuditCaddie OSS | auditcaddie.com"),
            "download_url": f"/api/free-policies/{framework}/{path.name}",
        })
    return {
        "framework": framework,
        "count": len(policies),
        "policies": policies,
        "attribution": "AuditCaddie OSS | auditcaddie.com | Apache 2.0",
    }


@app.get("/api/free-policies/{framework}/{filename}")
def get_free_policy(framework: str, filename: str):
    """Return the content of a free policy template as markdown."""
    # Sanitize filename to prevent path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(400, "Invalid filename")
    if not filename.endswith(".md"):
        raise HTTPException(400, "Only .md policy files are served here")
    path = POLICIES_DIR / framework / filename
    if not path.exists():
        raise HTTPException(404, f"Policy '{filename}' not found for framework '{framework}'")
    content = path.read_text()
    meta = _parse_policy_frontmatter(content)
    return {
        "filename": filename,
        "title": meta.get("title", filename),
        "controls": meta.get("controls", []),
        "content": content,
        "attribution": "AuditCaddie OSS | auditcaddie.com | Apache 2.0",
    }


@app.get("/api/free-policies/{framework}/{filename}/download")
def download_free_policy(framework: str, filename: str):
    """Download a free policy template as a .md file."""
    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(400, "Invalid filename")
    if not filename.endswith(".md"):
        raise HTTPException(400, "Only .md policy files can be downloaded")
    path = POLICIES_DIR / framework / filename
    if not path.exists():
        raise HTTPException(404, f"Policy '{filename}' not found")
    return Response(
        content=path.read_bytes(),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Security Toolbox ──────────────────────────────────────────────────────────

class ToolboxEnableRequest(BaseModel):
    tool_id: str
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "us-east-1"


def _make_boto3_session(access_key: str = "", secret_key: str = "", region: str = ""):
    """Build a boto3 Session from request params, falling back to env/DB credentials."""
    import boto3 as _boto3
    ak = access_key or os.getenv("AWS_ACCESS_KEY_ID") or _get_setting("aws_access_key")
    sk = secret_key or os.getenv("AWS_SECRET_ACCESS_KEY") or _get_setting("aws_secret_key")
    rg = region or os.getenv("AWS_DEFAULT_REGION") or _get_setting("aws_region") or "us-east-1"
    if ak and sk:
        return _boto3.Session(aws_access_key_id=ak, aws_secret_access_key=sk, region_name=rg)
    return _boto3.Session(region_name=rg)


@app.get("/api/toolbox/check")
def toolbox_check(aws_region: str = ""):
    """
    Non-destructive pre-scan check: which security tools are currently active?
    Called before a scan starts to surface gaps the user can fill in one click.
    No write operations — read-only checks only.
    aws_region is optional — falls back to saved settings or AWS_DEFAULT_REGION env var.
    """
    from scanner.aws_enabler import check_toolbox_status
    try:
        session = _make_boto3_session(region=aws_region)
        tools = check_toolbox_status(session)
        disabled_count = sum(
            1 for t in tools
            if t.get("status") in ("disabled", "warn") and t.get("status") != "error"
        )
        return {
            "tools": tools,
            "disabled_count": disabled_count,
            "all_enabled": disabled_count == 0,
        }
    except Exception as e:
        # Toolbox check is best-effort — scan can always proceed without it
        log.warning("Toolbox check failed: %s", e)
        return {"tools": [], "disabled_count": 0, "all_enabled": True, "error": str(e)}


@app.post("/api/toolbox/enable")
def toolbox_enable(req: ToolboxEnableRequest):
    """
    Enable a specific security tool. ONLY called when the user explicitly clicks 'Enable'.
    Dispatches to the appropriate enabler function via ENABLER_REGISTRY.
    Generates audit evidence on success.
    """
    from scanner.aws_enabler import ENABLER_REGISTRY
    if req.tool_id not in ENABLER_REGISTRY:
        raise HTTPException(400, f"Unknown tool ID: '{req.tool_id}'")
    try:
        session = _make_boto3_session(req.aws_access_key, req.aws_secret_key, req.aws_region)
        result = ENABLER_REGISTRY[req.tool_id](session)
        if not result.get("ok"):
            raise HTTPException(500, result.get("error", "Enable operation failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Documents / Evidence ───────────────────────────────────────────────────────

def _classify_background(doc_id: str, framework: str):
    """Run AI classification in the background and update the document row."""
    from document_classifier import classify_document, extract_text
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT original_filename, file_content FROM documents WHERE id=?", (doc_id,)
            ).fetchone()
        if not row:
            return

        text = extract_text(bytes(row["file_content"]), row["original_filename"])
        result = classify_document(text, framework, TMPL_DIR)

        if result["ok"]:
            with get_db() as conn:
                conn.execute(
                    "UPDATE documents SET status=?, suggestions=?, extracted_text=?, tokens_used=? WHERE id=?",
                    (
                        "classified",
                        json.dumps(result["suggestions"]),
                        text[:20000],
                        result.get("tokens", 0),
                        doc_id,
                    ),
                )
        else:
            with get_db() as conn:
                conn.execute(
                    "UPDATE documents SET status=?, error_msg=? WHERE id=?",
                    ("error", result["error"], doc_id),
                )
    except Exception as e:
        log.error("Classification background task failed for %s: %s", doc_id, e)
        with get_db() as conn:
            conn.execute(
                "UPDATE documents SET status=?, error_msg=? WHERE id=?",
                ("error", str(e), doc_id),
            )


@app.post("/api/documents")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: str = Form("evidence"),
    framework: str = Form(""),
    tags: str = Form(""),
):
    """Upload an evidence or policy document and trigger AI classification."""
    from document_classifier import ALLOWED_EXTENSIONS, MAX_FILE_BYTES

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(400, "File exceeds 10 MB limit")

    # Parse tags — comma-separated string → JSON array
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    tags_json = json.dumps(tag_list)

    doc_id = str(uuid.uuid4())[:12]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO documents
               (id, original_filename, mime_type, document_type, framework, tags, file_content, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (doc_id, file.filename, file.content_type or "", document_type, framework, tags_json,
             content, "classifying" if framework else "pending"),
        )

    if framework:
        background_tasks.add_task(_classify_background, doc_id, framework)

    return {"doc_id": doc_id, "status": "classifying" if framework else "pending", "filename": file.filename}


@app.get("/api/documents")
def list_documents(framework: str = "", limit: int = 50):
    with get_db() as conn:
        if framework:
            rows = conn.execute(
                "SELECT id, created_at, original_filename, document_type, framework, tags, "
                "status, suggestions, confirmed_controls, is_confirmed, tokens_used "
                "FROM documents WHERE framework=? ORDER BY created_at DESC LIMIT ?",
                (framework, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, created_at, original_filename, document_type, framework, tags, "
                "status, suggestions, confirmed_controls, is_confirmed, tokens_used "
                "FROM documents ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d["suggestions"] = json.loads(d["suggestions"]) if d["suggestions"] else []
        d["confirmed_controls"] = json.loads(d["confirmed_controls"]) if d["confirmed_controls"] else []
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        result.append(d)
    return result


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, created_at, original_filename, mime_type, document_type, framework, tags, "
            "status, suggestions, confirmed_controls, is_confirmed, user_overrode, tokens_used, error_msg "
            "FROM documents WHERE id=?", (doc_id,)
        ).fetchone()
    if not row:
        raise HTTPException(404, "Document not found")
    d = dict(row)
    d["suggestions"] = json.loads(d["suggestions"]) if d["suggestions"] else []
    d["confirmed_controls"] = json.loads(d["confirmed_controls"]) if d["confirmed_controls"] else []
    d["tags"] = json.loads(d["tags"]) if d["tags"] else []
    return d


@app.get("/api/documents/{doc_id}/download")
def download_document(doc_id: str):
    with get_db() as conn:
        row = conn.execute(
            "SELECT original_filename, mime_type, file_content FROM documents WHERE id=?", (doc_id,)
        ).fetchone()
    if not row:
        raise HTTPException(404, "Document not found")
    return Response(
        content=bytes(row["file_content"]),
        media_type=row["mime_type"] or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{row["original_filename"]}"'},
    )


@app.post("/api/documents/{doc_id}/classify")
def reclassify_document(doc_id: str, background_tasks: BackgroundTasks):
    """Re-run AI classification on an already-uploaded document."""
    with get_db() as conn:
        row = conn.execute("SELECT framework FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Document not found")
    if not row["framework"]:
        raise HTTPException(400, "Document has no framework assigned — cannot classify")
    with get_db() as conn:
        conn.execute("UPDATE documents SET status=? WHERE id=?", ("classifying", doc_id))
    background_tasks.add_task(_classify_background, doc_id, row["framework"])
    return {"ok": True, "status": "classifying"}


@app.post("/api/documents/{doc_id}/confirm")
def confirm_classification(doc_id: str, payload: ConfirmPayload):
    """User confirms or overrides the AI-suggested control assignments."""
    with get_db() as conn:
        row = conn.execute("SELECT id FROM documents WHERE id=?", (doc_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Document not found")
    with get_db() as conn:
        conn.execute(
            "UPDATE documents SET confirmed_controls=?, is_confirmed=1, user_overrode=? WHERE id=?",
            (json.dumps(payload.control_ids), int(payload.user_overrode), doc_id),
        )
    return {"ok": True, "confirmed_controls": payload.control_ids}


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    return {"ok": True}


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
