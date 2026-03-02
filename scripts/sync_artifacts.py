#!/usr/bin/env python3
"""
Compare la structure du code à Architecture.md et génère un rapport de dérive (spec III.8-O, F1).
Lancé par cron hebdomadaire (SYNC_ARTIFACTS_CRON).
"""
import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def get_orchestration_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_actual_structure(project_root: Path) -> set[str]:
    """Retourne les chemins relatifs des dossiers/fichiers principaux (src, scripts, etc.)."""
    exclude = {".git", "__pycache__", "node_modules", ".venv", "venv", "chroma_db"}
    paths = set()
    for p in project_root.rglob("*"):
        if p.is_file() and not any(ex in p.parts for ex in exclude):
            rel = p.relative_to(project_root)
            paths.add(str(rel).replace("\\", "/"))
    return paths


def extract_expected_from_architecture(arch_path: Path) -> set[str]:
    """Extrait les chemins/modules mentionnés dans Architecture.md (heuristique simple)."""
    text = arch_path.read_text(encoding="utf-8", errors="replace")
    # Cherche patterns : src/xxx, scripts/xxx, config/xxx, specs/xxx
    pattern = r"(?:^|\s)((?:src|scripts|config|specs|graph|docs)/[\w/.-]+)"
    found = set()
    for m in re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE):
        p = m.group(1).strip()
        if "*" not in p and "..." not in p:
            found.add(p)
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--project-id", default="default")
    args = parser.parse_args()

    root = get_orchestration_root()
    project_root = args.project_root or root
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"sync_artifacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    lines = []
    arch = project_root / "Architecture.md"
    if not arch.exists():
        lines.append(f"[{datetime.now().isoformat()}] project_id={args.project_id} Architecture.md absent — skip")
        log_file.write_text("\n".join(lines), encoding="utf-8")
        return 0

    actual = get_actual_structure(project_root)
    expected = extract_expected_from_architecture(arch)
    top_dirs_actual = {p.split("/")[0] for p in actual}
    top_dirs_expected = {e.split("/")[0] for e in expected}
    drift = top_dirs_actual - top_dirs_expected

    lines.append(f"[{datetime.now().isoformat()}] project_id={args.project_id} sync_artifacts")
    lines.append(f"  Architecture.md: {arch}")
    lines.append(f"  Fichiers réels: {len(actual)}")
    lines.append(f"  Références Architecture: {len(expected)}")
    if drift:
        lines.append(f"  Dérive: dossiers sans ref dans Architecture.md: {drift}")

    content = "\n".join(lines)
    log_file.write_text(content, encoding="utf-8")
    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
