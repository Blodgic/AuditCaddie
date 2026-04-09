"""
AuditCaddie OSS — AI Policy Document Generator
Generates compliance policy documents using OpenAI or Anthropic.

Supported models:
  - gpt-4o (OpenAI)  → set OPENAI_API_KEY
  - claude-sonnet-4-5 (Anthropic) → set ANTHROPIC_API_KEY

Set AI_MODEL in .env to choose which model to use.
"""

import logging
import os
from typing import Optional

log = logging.getLogger("auditcaddie.ai")

SUPPORTED_MODELS = {
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "claude-sonnet-4-5": "anthropic",
    "claude-haiku-4-5-20251001": "anthropic",
}

SYSTEM_PROMPT = """You are a compliance expert writing formal policy documents for businesses.
Write in clear, professional language. Use standard policy document formatting with numbered sections.
Be practical and specific — avoid generic filler. The document should be usable immediately after
minor customization (company name, dates, owner names).

Format: Use markdown with H2 section headers. Include a document header with fields for
Company Name, Version, Effective Date, and Approved By (leave as placeholders like [COMPANY NAME]).
"""


def get_model() -> tuple[str, str]:
    """Returns (model_id, provider)."""
    model = os.getenv("AI_MODEL", "gpt-4o")
    provider = SUPPORTED_MODELS.get(model)
    if not provider:
        # Default based on which key is available
        if os.getenv("OPENAI_API_KEY"):
            return "gpt-4o", "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "claude-sonnet-4-5", "anthropic"
        return "gpt-4o", "openai"  # Will fail gracefully later
    return model, provider


def check_ai_configured() -> dict:
    """Returns AI configuration status."""
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    model, provider = get_model()
    return {
        "configured": openai_key or anthropic_key,
        "openai": openai_key,
        "anthropic": anthropic_key,
        "active_model": model,
        "active_provider": provider,
    }


def generate_policy_doc(
    prompt: str,
    policy_name: str,
    model: Optional[str] = None,
    max_tokens: int = 4096,
) -> dict:
    """
    Generate a compliance policy document using AI.

    Returns:
        {"ok": True, "content": "...", "model": "...", "tokens": N}
        or
        {"ok": False, "error": "..."}
    """
    active_model, provider = get_model() if not model else (model, SUPPORTED_MODELS.get(model, "openai"))

    full_prompt = f"""Write a complete {policy_name} policy document.

{prompt}

The document should be comprehensive enough for use in a compliance audit.
Include all required sections. End with a document control section."""

    try:
        if provider == "openai":
            return _call_openai(full_prompt, active_model, max_tokens)
        elif provider == "anthropic":
            return _call_anthropic(full_prompt, active_model, max_tokens)
        else:
            return {"ok": False, "error": f"Unknown provider: {provider}"}
    except Exception as e:
        log.error("AI generation failed: %s", e)
        return {"ok": False, "error": str(e)}


def _call_openai(prompt: str, model: str, max_tokens: int) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"ok": False, "error": "OPENAI_API_KEY not set in .env"}

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return {
        "ok": True,
        "content": resp.choices[0].message.content,
        "model": model,
        "tokens": resp.usage.total_tokens if resp.usage else None,
    }


def _call_anthropic(prompt: str, model: str, max_tokens: int) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"ok": False, "error": "ANTHROPIC_API_KEY not set in .env"}

    from anthropic import Anthropic
    client = Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "ok": True,
        "content": msg.content[0].text,
        "model": model,
        "tokens": msg.usage.input_tokens + msg.usage.output_tokens if msg.usage else None,
    }
