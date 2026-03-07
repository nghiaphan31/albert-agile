#!/usr/bin/env python3
"""Tableau de bord multi-projets (spec III.8-P, F6). Affiche project_id, phase, interrupts, indexation."""
import argparse
import json
import sys
from pathlib import Path

ORCH_ROOT = Path(__file__).resolve().parent.parent
if str(ORCH_ROOT) not in sys.path:
    sys.path.insert(0, str(ORCH_ROOT))


def _extract_project_id(thread_id: str) -> str:
    """Extrait project_id du thread_id (convention: {project_id}-phase/sprint/hotfix-...)."""
    for suffix in ("-phase-", "-sprint-", "-hotfix-"):
        if suffix in thread_id:
            return thread_id.split(suffix)[0]
    # Fallback: thread_id peut être project_id ou project_id-suffix (ex: albert-agile-e2e-v2)
    parts = thread_id.split("-")
    if len(parts) >= 2:
        return parts[0] + "-" + parts[1]  # ex: albert-agile
    return thread_id


def _count_pending_interrupts_by_project() -> dict[str, int]:
    """Compte les interrupts en attente par project_id (extrait du thread_id)."""
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location(
            "handle_interrupt", ORCH_ROOT / "scripts" / "handle_interrupt.py"
        )
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pending = mod._list_pending()
    except Exception:
        return {}
    counts: dict[str, int] = {}
    for tid, _ in pending:
        pid = _extract_project_id(tid)
        counts[pid] = counts.get(pid, 0) + 1
    return counts


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

    interrupt_counts = _count_pending_interrupts_by_project()
    out = []
    for pid, cfg in projects.items():
        rec = {
            "project_id": pid,
            "path": cfg.get("path", ""),
            "phase_courante": "N/A",
            "interrupts_en_attente": interrupt_counts.get(pid, 0),
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
            print(f"{r['project_id']}: phase={r['phase_courante']} interrupts={r['interrupts_en_attente']} pending_index={r['pending_index']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
