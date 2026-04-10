"""
AuditCaddie OSS — Document Classifier
Extracts text from uploaded evidence/policy files and uses AI to map
them to framework controls with high / medium / low confidence scoring.
"""

import io
import json
import logging
import os
from pathlib import Path
from typing import Optional

import yaml

log = logging.getLogger("auditcaddie.classifier")

MAX_TEXT_CHARS = 8000   # keep AI costs manageable
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".csv"}
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


# ── Text extraction ────────────────────────────────────────────────────────────

def extract_text(file_content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf(file_content)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_content)
    else:
        return file_content.decode("utf-8", errors="replace")


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        log.warning("PDF extraction failed: %s", e)
        return ""


def _extract_docx(content: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        log.warning("DOCX extraction failed: %s", e)
        return ""


# ── AI classification ──────────────────────────────────────────────────────────

CLASSIFY_SYSTEM = (
    "You are a compliance expert. Your job is to analyze documents and identify "
    "which compliance controls they provide evidence for. Be precise and conservative "
    "with confidence scores — only assign High (≥0.7) when the document directly and "
    "clearly addresses the control. Return valid JSON only."
)


def classify_document(text: str, framework_slug: str, templates_dir: Path) -> dict:
    """
    Classify a document against a framework's controls using AI.

    Returns:
        {
            "ok": True,
            "suggestions": [
                {
                    "rank": 1,
                    "control_id": "CC6.1",
                    "control_name": "Logical Access Controls",
                    "category": "Common Criteria",
                    "confidence": 0.92,
                    "confidence_label": "High",   # "High" | "Medium" | "Low"
                    "reasoning": "..."
                }, ...
            ],
            "tokens": N
        }
        or {"ok": False, "error": "..."}
    """
    tmpl_path = templates_dir / f"{framework_slug}.yaml"
    if not tmpl_path.exists():
        return {"ok": False, "error": f"Framework '{framework_slug}' not found"}

    tmpl = yaml.safe_load(tmpl_path.read_text())
    controls = tmpl.get("controls", [])
    if not controls:
        return {"ok": False, "error": "No controls found in this framework template"}

    controls_list = "\n".join(
        f"- {c['id']}: {c['name']} [{c.get('category', '')}]\n  {(c.get('description') or '')[:180]}"
        for c in controls
    )

    doc_snippet = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        doc_snippet += "\n[... truncated ...]"

    prompt = f"""Analyze the following document and identify the top 3 most relevant compliance controls from the {tmpl.get('name', framework_slug)} framework.

CONTROLS:
{controls_list}

DOCUMENT:
---
{doc_snippet}
---

Return ONLY valid JSON — no markdown, no explanation outside the JSON:
{{
  "suggestions": [
    {{"rank": 1, "control_id": "...", "confidence": 0.0, "reasoning": "1-2 sentences"}},
    {{"rank": 2, "control_id": "...", "confidence": 0.0, "reasoning": "1-2 sentences"}},
    {{"rank": 3, "control_id": "...", "confidence": 0.0, "reasoning": "1-2 sentences"}}
  ]
}}

Confidence scale: 0.9+ = definitive match, 0.7-0.9 = strong match, 0.4-0.7 = partial match, <0.4 = weak/indirect.
Omit a suggestion if fewer than 3 controls are genuinely relevant."""

    raw = _call_ai(prompt)
    if not raw["ok"]:
        return raw

    try:
        content = raw["content"].strip()
        # Strip markdown code fences if model included them
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content.strip())
    except Exception as e:
        log.error("Failed to parse AI response: %s\n%s", e, raw["content"][:500])
        return {"ok": False, "error": "AI returned malformed JSON"}

    control_map = {c["id"]: c for c in controls}
    suggestions = []
    for s in parsed.get("suggestions", [])[:3]:
        cid = s.get("control_id", "")
        ctrl = control_map.get(cid, {})
        conf = max(0.0, min(1.0, float(s.get("confidence", 0))))
        label = "High" if conf >= 0.7 else "Medium" if conf >= 0.4 else "Low"
        suggestions.append({
            "rank": s.get("rank", len(suggestions) + 1),
            "control_id": cid,
            "control_name": ctrl.get("name", cid),
            "category": ctrl.get("category", ""),
            "confidence": round(conf, 3),
            "confidence_label": label,
            "reasoning": s.get("reasoning", ""),
        })

    return {"ok": True, "suggestions": suggestions, "tokens": raw.get("tokens", 0)}


def _call_ai(prompt: str) -> dict:
    """Call whichever AI provider is configured."""
    from ai_generator import get_model, SUPPORTED_MODELS

    model, provider = get_model()

    try:
        if provider == "openai":
            from openai import OpenAI
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                return {"ok": False, "error": "OPENAI_API_KEY not set"}
            client = OpenAI(api_key=key)
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": CLASSIFY_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
                temperature=0.1,
            )
            return {
                "ok": True,
                "content": resp.choices[0].message.content,
                "tokens": resp.usage.total_tokens if resp.usage else 0,
            }

        elif provider == "anthropic":
            from anthropic import Anthropic
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                return {"ok": False, "error": "ANTHROPIC_API_KEY not set"}
            client = Anthropic(api_key=key)
            msg = client.messages.create(
                model=model,
                max_tokens=1024,
                system=CLASSIFY_SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "ok": True,
                "content": msg.content[0].text,
                "tokens": (msg.usage.input_tokens + msg.usage.output_tokens) if msg.usage else 0,
            }

        return {"ok": False, "error": "No AI provider configured — add a key in Settings"}

    except Exception as e:
        log.error("AI classification error: %s", e)
        return {"ok": False, "error": str(e)}
