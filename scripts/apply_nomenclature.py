#!/usr/bin/env python3
"""Applique la nomenclature R-x, H-x, E-x aux fichiers Markdown.
Usage: python scripts/apply_nomenclature.py specs/simulations/*.md
"""
import sys
from pathlib import Path

REPLACEMENTS = [
    # R-x (ordre important : R-7 avant R-1 pour éviter sous-chaînes)
    # Albert = agent IA ; Nghia = humain (R-1, R-7)
    ("R-0", "R-0 (Albert Business Analyst)"),
    ("R-1", "R-1 (Nghia Product Owner)"),
    ("R-2", "R-2 (Albert System Architect)"),
    ("R-3", "R-3 (Albert Scrum Master)"),
    ("R-4", "R-4 (Albert Dev Team)"),
    ("R-5", "R-5 (Albert Release Manager)"),
    ("R-6", "R-6 (Albert QA & DevOps)"),
    ("R-7", "R-7 (Nghia Stakeholder)"),
    # H-x
    ("H1", "H1 (validation Gros Ticket)"),
    ("H2", "H2 (validation Architecture + DoD)"),
    ("H3", "H3 (validation Sprint Backlog)"),
    ("H4", "H4 (Sprint Review)"),
    ("H5", "H5 (approbation escalade API payante)"),
    ("H6", "H6 (résolution conflit Git)"),
    # E-x
    ("E1", "E1 (idéation)"),
    ("E2", "E2 (architecture)"),
    ("E3", "E3 (Sprint Backlog)"),
    ("E4", "E4 (exécution code)"),
    ("E5", "E5 (tests CI)"),
    ("E6", "E6 (clôture sprint)"),
    ("HOTFIX", "HOTFIX (correctif urgent)"),
]

# Doubles à nettoyer : "X (label) (label)" -> "X (label)"
CLEANUP_PATTERNS = []
for _old, new in REPLACEMENTS:
    if "(" in new:
        label = new.split("(", 1)[1].rstrip(")")
        CLEANUP_PATTERNS.append((f"{new} ({label})", new))

def apply(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    for double, single in CLEANUP_PATTERNS:
        text = text.replace(double, single)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def main():
    files = [Path(p) for p in sys.argv[1:]]
    for f in files:
        if f.suffix == ".md" and f.exists():
            if apply(f):
                print(f"Updated: {f}")

if __name__ == "__main__":
    main()
