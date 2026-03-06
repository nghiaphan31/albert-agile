"""
LLM factory pour la cascade N0→N1→N2 (spec III.5, F8).
Tier 1 (R0, R2): gemma3 → Gemini → Claude Opus
Tier 2 (R3-R6): qwen2.5-coder → Gemini → Claude Sonnet
"""

import os
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Modèles Anthropic (IDs actifs en 2026 — claude-3-opus-20240229 déprécié/404)
CLAUDE_OPUS = os.environ.get("AGILE_CLAUDE_OPUS", "claude-opus-4-6")
CLAUDE_SONNET = os.environ.get("AGILE_CLAUDE_SONNET", "claude-sonnet-4-6")


def _load_prompt(role: str, laws: str) -> str:
    path = _PROMPTS_DIR / f"{role}_system.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").format(laws=laws)
    return f"Rôle {role}.\n{laws}"


def get_system_prompt(role: str, laws: str) -> str:
    """Charge le prompt système pour un rôle avec les lois injectées."""
    return _load_prompt(role, laws)


def get_llms_tier1():
    """Tier 1 : R0 (Business Analyst), R2 (System Architect) — N0 configurable, Gemini, Claude Opus.

    Modèle N0 par défaut : qwen2.5-coder:3b (stable sur Calypso avec structured output).
    gemma3:12b-it-q4_K_M provoque un panic Ollama lors du sampling contraint (with_structured_output).
    Override possible via AGILE_TIER1_N0_MODEL.
    """
    from langchain_ollama import ChatOllama
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_anthropic import ChatAnthropic

    n0_model = os.environ.get("AGILE_TIER1_N0_MODEL", "qwen2.5-coder:3b")
    n0 = ChatOllama(model=n0_model, temperature=0.3)
    n1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash") if os.environ.get("GOOGLE_API_KEY") else None
    n2 = ChatAnthropic(model=CLAUDE_OPUS, temperature=0.3) if os.environ.get("ANTHROPIC_API_KEY") else None
    return n0, n1, n2


def get_llms_tier2():
    """Tier 2 : R3-R6 — N0 coder configurable (qwen2.5-coder:3b par défaut), Gemini, Claude Sonnet."""
    from langchain_ollama import ChatOllama
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_anthropic import ChatAnthropic

    # N0 coder : par défaut qwen2.5-coder:3b (plus stable sur Calypso que la variante 7b).
    # Override possible via AGILE_TIER2_N0_MODEL.
    n0_model = os.environ.get("AGILE_TIER2_N0_MODEL", "qwen2.5-coder:3b")
    n0 = ChatOllama(model=n0_model, temperature=0.3)
    n1 = ChatGoogleGenerativeAI(model="gemini-2.0-flash") if os.environ.get("GOOGLE_API_KEY") else None
    n2 = ChatAnthropic(model=CLAUDE_SONNET, temperature=0.3) if os.environ.get("ANTHROPIC_API_KEY") else None
    return n0, n1, n2
