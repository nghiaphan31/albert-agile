#!/usr/bin/env python3
"""Tableau de bord multi-projets (spec III.8-P, F6). Affiche project_id, phase, interrupts, indexation."""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", help="Filtrer par projet")
    parser.add_argument("--json", action="store_true", help="Sortie JSON")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    projects_json = root / "config" / "projects.json"
    if not projects_json.exists():
        print("config/projects.json introuvable")
        return 1

    data = json.loads(projects_json.read_text(encoding="utf-8"))
    projects = {k: v for k, v in data.items() if not k.startswith("_")}
    if args.project_id:
        projects = {k: v for k, v in projects.items() if k == args.project_id}

    out = []
    for pid, cfg in projects.items():
        rec = {
            "project_id": pid,
            "path": cfg.get("path", ""),
            "phase_courante": "N/A",
            "interrupts_en_attente": 0,
            "derniere_indexation_rag": "N/A",
            "pending_index": 0,
            "alertes": [],
        }
        log_dir = root / "logs"
        if log_dir.exists():
            rag_logs = list(log_dir.glob("index_rag_*.log"))
            if rag_logs:
                rec["derniere_indexation_rag"] = max(rag_logs, key=lambda p: p.stat().st_mtime).name
            pend = log_dir / "pending_index.log"
            if pend.exists():
                rec["pending_index"] = sum(1 for _ in pend.read_text().strip().splitlines() if _.strip())
        out.append(rec)

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for r in out:
            print(f"{r['project_id']}: phase={r['phase_courante']} pending_index={r['pending_index']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
