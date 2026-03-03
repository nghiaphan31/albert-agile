"""
Gateway anonymisation cloud (L-ANON).
Applique les règles avant envoi vers Gemini/Claude.
"""

import re
import os
from pathlib import Path

logger = __import__("logging").getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "anonymisation.yaml"


def _load_rules() -> list[dict]:
    """Charge les règles depuis config/anonymisation.yaml."""
    if not _CONFIG_PATH.exists():
        return _default_rules()
    try:
        import yaml
        data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
        return data.get("patterns", _default_rules())
    except Exception as e:
        logger.warning("anonymisation.yaml load failed: %s, using defaults", e)
        return _default_rules()


def _default_rules() -> list[dict]:
    """Règles par défaut si pas de YAML."""
    return [
        {"name": "email", "regex": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "replacement": "[EMAIL_REDACTED]"},
        {"name": "unix_home", "regex": r"/home/[^/]+/", "replacement": "[HOME]/"},
        {"name": "username", "regex": r"nghia-phan", "replacement": "[USER]"},
        {"name": "ip", "regex": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "replacement": "[IP_REDACTED]"},
        {"name": "sk_key", "regex": r"sk-[a-zA-Z0-9]{20,}", "replacement": "[API_KEY_REDACTED]"},
        {"name": "google_key", "regex": r"AIza[a-zA-Z0-9_-]{35}", "replacement": "[GOOGLE_KEY_REDACTED]"},
    ]


_rules_cache: list[tuple[re.Pattern, str]] | None = None


def _get_compiled_rules():
    global _rules_cache
    if _rules_cache is None:
        rules = _load_rules()
        _rules_cache = []
        for r in rules:
            try:
                pat = re.compile(r["regex"])
                _rules_cache.append((pat, r.get("replacement", "[REDACTED]")))
            except re.error:
                logger.warning("Invalid regex %s: %s", r.get("name"), r.get("regex"))
    return _rules_cache


def scrub(text: str) -> str:
    """Applique les règles d'anonymisation sur un texte."""
    if not text or not isinstance(text, str):
        return text
    out = text
    for pat, repl in _get_compiled_rules():
        out = pat.sub(repl, out)
    return out


def apply_rules(messages: list) -> list:
    """
    Anonymise system prompt, messages utilisateur, contexte RAG.
    messages: liste de dict avec 'role' et 'content' ou objets BaseMessage.
    """
    result = []
    for m in messages:
        if hasattr(m, "content"):
            content = m.content
        elif isinstance(m, dict):
            content = m.get("content", m.get("text", ""))
        else:
            result.append(m)
            continue
        if isinstance(content, str):
            content = scrub(content)
        elif isinstance(content, list):
            content = [_scrub_part(p) for p in content]
        if hasattr(m, "content"):
            m_copy = type(m)(content=content)
            result.append(m_copy)
        elif isinstance(m, dict):
            result.append({**m, "content": content})
        else:
            result.append(m)
    return result


def _scrub_part(part: dict) -> dict:
    if isinstance(part, dict):
        if "text" in part:
            part = {**part, "text": scrub(part["text"])}
        if "content" in part and isinstance(part["content"], str):
            part = {**part, "content": scrub(part["content"])}
    return part


def should_anonymize() -> bool:
    """True si on doit anonymiser (défaut True sauf AGILE_ALLOW_PERSONAL_CLOUD)."""
    return os.environ.get("AGILE_ALLOW_PERSONAL_CLOUD", "").lower() not in ("true", "1", "yes")
