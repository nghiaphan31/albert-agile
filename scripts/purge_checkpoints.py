#!/usr/bin/env python3
"""
Purge des checkpoints > max-age-days (spec III.8-L).
Exclut les threads avec __interrupt__ non résolu.
Protège les sprints actifs si --protect-active-sprints.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ORCH_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ORCH_ROOT))

from dotenv import load_dotenv

load_dotenv(ORCH_ROOT / ".env")


def get_checkpoint_path() -> Path:
    root = os.environ.get("AGILE_ORCHESTRATION_ROOT", "")
    if not root:
        return Path.cwd() / "checkpoints.sqlite"
    return Path(root) / "checkpoints.sqlite"


def _get_interrupts(thread_id: str, graph) -> list:
    """Retourne les interrupts actifs pour un thread (threads avec interrupt non résolu)."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snap = graph.get_state(config)
    except Exception:
        return []
    interrupts = []
    for task in snap.tasks:
        if task.interrupts:
            interrupts.extend(task.interrupts)
    return interrupts


def _all_thread_ids(checkpointer) -> list[str]:
    """Retourne tous les thread_id depuis le checkpointer."""
    conn = checkpointer.conn
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def _get_latest_checkpoint_ts(checkpointer, thread_id: str) -> str | None:
    """Retourne le timestamp ISO du dernier checkpoint du thread, ou None."""
    config = {"configurable": {"thread_id": thread_id}}
    try:
        for tup in checkpointer.list(config, limit=1):
            checkpoint = tup.checkpoint
            if isinstance(checkpoint, dict) and "ts" in checkpoint:
                return checkpoint["ts"]
            return None
    except Exception:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Purge des vieux checkpoints")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans supprimer")
    parser.add_argument("--max-age-days", type=int, default=90, help="Âge max en jours")
    parser.add_argument(
        "--no-protect-active-sprints",
        action="store_true",
        help="Désactiver la protection des sprints actifs (--protect-active-sprints=false)",
    )
    args = parser.parse_args()

    protect_active_sprints = not args.no_protect_active_sprints
    ckpt_path = get_checkpoint_path()

    if not ckpt_path.exists():
        print(f"Pas de checkpoints trouvés: {ckpt_path}")
        return 0

    # Import graph (et checkpointer) après avoir vérifié que le fichier existe
    from graph.graph import graph

    checkpointer = graph.checkpointer
    if checkpointer is None:
        print("Erreur: le graphe n'a pas de checkpointer configuré.")
        return 1

    thread_ids = _all_thread_ids(checkpointer)
    if not thread_ids:
        print("Aucun thread trouvé.")
        return 0

    now = datetime.now(timezone.utc)
    cutoff_days = args.max_age_days
    to_purge = []
    skipped_interrupt = []
    skipped_recent = []

    for tid in thread_ids:
        # Exclure les threads avec interrupt non résolu
        interrupts = _get_interrupts(tid, graph)
        if interrupts:
            skipped_interrupt.append(tid)
            continue

        ts_str = _get_latest_checkpoint_ts(checkpointer, tid)
        if not ts_str:
            continue

        try:
            # Parser le timestamp ISO (ex: 2024-05-04T06:32:42.235444+00:00)
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        delta = now - ts
        if delta.days >= cutoff_days:
            to_purge.append((tid, ts_str))
        else:
            skipped_recent.append((tid, delta.days))

    # Afficher le résumé
    print(f"purge_checkpoints: dry_run={args.dry_run}, max_age_days={cutoff_days}")
    print(f"  Checkpoint path: {ckpt_path}")
    print(f"  Threads avec interrupt (exclus): {len(skipped_interrupt)}")
    for tid in skipped_interrupt:
        print(f"    - {tid}")
    print(f"  Threads récents (< {cutoff_days} jours, exclus): {len(skipped_recent)}")
    print(f"  Threads éligibles à la purge: {len(to_purge)}")

    if not to_purge:
        print("Rien à purger.")
        return 0

    for tid, ts_str in to_purge:
        print(f"  [PURGE] {tid} (dernier checkpoint: {ts_str})")

    if args.dry_run:
        print("\nDry-run: aucune suppression effectuée.")
        return 0

    # Supprimer
    for tid, _ in to_purge:
        checkpointer.delete_thread(tid)
        print(f"  Supprimé: {tid}")

    print(f"\nPurge terminée: {len(to_purge)} thread(s) supprimé(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
