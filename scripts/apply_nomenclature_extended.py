#!/usr/bin/env python3
"""Applique la nomenclature étendue (N0-N2, acronymes, CI, F) aux fichiers Markdown.
Évite les remplacements dans les blocs de code (entre ```).
"""
import re
import sys
from pathlib import Path

# (pattern, replacement) - order matters for overlaps
REPLACEMENTS = [
    # N0, N1, N2 - cascade (word boundary to avoid n0_failure)
    (r"\bN0\b", "N0 (local Ollama)"),
    (r"\bN1\b", "N1 (cloud gratuit)"),
    (r"\bN2\b", "N2 (cloud payant)"),
    # CI 1, CI 2 - careful: "CI 1" not "CI 11"
    (r"\bCI 1\b", "CI 1 (feature→develop)"),
    (r"\bCI 2\b", "CI 2 (develop→main)"),
    # Acronyms - avoid double replacement
    (r"\bDoD\b", "DoD (Definition of Done)"),
    (r"\bADR\b", "ADR (Architecture Decision Record)"),
    (r"\bRAG\b", "RAG (recherche sémantique)"),
    (r"\bMCP\b", "MCP (Model Context Protocol)"),
    (r"\bBaseStore\b", "BaseStore (mémoire long terme)"),
    (r"\bCDC\b", "CDC (Cahier des charges)"),
    (r"\bV\.A\.R\.\b", "V.A.R. (Valeur Ajoutée Rétrospective)"),
    # F rules
    (r"\bF1\b", "F1 (sync_artifacts cron)"),
    (r"\bF2\b", "F2 (détection changement architectural)"),
    (r"\bF4\b", "F4 (projet en pause, purge)"),
    (r"\bF5\b", "F5 (notification interrupt > 48h)"),
    (r"\bF6\b", "F6 (status multi-projets)"),
    (r"\bF7\b", "F7 (AGILE_DEFER_INDEX)"),
    (r"\bF8\b", "F8 (cascade échec N0)"),
    (r"\bF9\b", "F9 (write_file atomique)"),
    (r"\bF10\b", "F10 (AGILE_BASESTORE_STRICT)"),
]

# Cleanup doubles: "X (label) (label)" -> "X (label)"
CLEANUP = [
    (r"N0 \(local Ollama\) \(local Ollama\)", "N0 (local Ollama)"),
    (r"N1 \(cloud gratuit\) \(cloud gratuit\)", "N1 (cloud gratuit)"),
    (r"N2 \(cloud payant\) \(cloud payant\)", "N2 (cloud payant)"),
    (r"DoD \(Definition of Done\) \(Definition of Done\)", "DoD (Definition of Done)"),
    (r"ADR \(Architecture Decision Record\) \(Architecture Decision Record\)", "ADR (Architecture Decision Record)"),
    (r"RAG \(recherche sémantique\) \(recherche sémantique\)", "RAG (recherche sémantique)"),
    (r"MCP \(Model Context Protocol\) \(Model Context Protocol\)", "MCP (Model Context Protocol)"),
    (r"BaseStore \(mémoire long terme\) \(mémoire long terme\)", "BaseStore (mémoire long terme)"),
]


def apply_to_text(text: str) -> str:
    """Apply replacements only outside code blocks."""
    parts = re.split(r"(```[^\n]*\n.*?```)", text, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if part.startswith("```"):
            result.append(part)  # Keep code blocks unchanged
        else:
            for pat, repl in REPLACEMENTS:
                part = re.sub(pat, repl, part)
            for pat, repl in CLEANUP:
                part = re.sub(pat, repl, part)
            result.append(part)
    return "".join(result)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text = apply_to_text(text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    paths = [Path(p) for p in sys.argv[1:]]
    for p in paths:
        if p.suffix in (".md", ".plan") and p.exists():
            if process_file(p):
                print(f"Updated: {p}")


if __name__ == "__main__":
    main()
