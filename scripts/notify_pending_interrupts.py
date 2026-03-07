#!/usr/bin/env python3
"""
Alertes pour interrupts en attente > AGILE_INTERRUPT_TIMEOUT_HOURS (spec F5, III.8-B).
Écrit dans logs/pending_interrupts_alert.log.
Exécute AGILE_NOTIFY_CMD si défini (email, webhook).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ORCH_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ORCH_ROOT))

from dotenv import load_dotenv

load_dotenv(ORCH_ROOT / ".env")


def _get_interrupts(thread_id: str, graph) -> list:
    """Retourne les interrupts actifs pour un thread."""
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


def _all_thread_ids(checkpointer) -> list[str]:
    """Retourne tous les thread_id depuis le checkpointer."""
    conn = checkpointer.conn
    cur = conn.cursor()
    try:
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def _list_pending_with_age(graph, checkpointer) -> list[tuple[str, list, str | None]]:
    """
    Retourne [(thread_id, [Interrupt, ...], last_checkpoint_ts), ...] pour les threads
    en attente d'un interrupt.
    """
    result = []
    for tid in _all_thread_ids(checkpointer):
        intr = _get_interrupts(tid, graph)
        if intr:
            ts = _get_latest_checkpoint_ts(checkpointer, tid)
            result.append((tid, intr, ts))
    return result


def main() -> int:
    root = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", str(ORCH_ROOT)))
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    alert_log = log_dir / "pending_interrupts_alert.log"
    timeout_hours = int(os.environ.get("AGILE_INTERRUPT_TIMEOUT_HOURS", "48"))
    notify_cmd = os.environ.get("AGILE_NOTIFY_CMD")

    from graph.graph import graph

    checkpointer = graph.checkpointer
    if checkpointer is None:
        with open(alert_log, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()} notify_pending_interrupts: no checkpointer\n")
        return 0

    pending = _list_pending_with_age(graph, checkpointer)
    if not pending:
        return 0

    now = datetime.now(timezone.utc)
    timeout_delta = timedelta(hours=timeout_hours)
    stale = []

    for tid, interrupts, ts_str in pending:
        if not ts_str:
            stale.append((tid, None, interrupts))
            continue
        try:
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            stale.append((tid, None, interrupts))
            continue
        if now - ts > timeout_delta:
            stale.append((tid, ts_str, interrupts))

    if not stale:
        return 0

    # Écrire dans le log d'alerte
    lines = [f"{now.isoformat()} ALERT: {len(stale)} interrupt(s) en attente depuis > {timeout_hours}h:\n"]
    for tid, ts_str, interrupts in stale:
        reason = ""
        if interrupts:
            val = interrupts[0].value if hasattr(interrupts[0], "value") else interrupts[0]
            reason = val.get("reason", "") if isinstance(val, dict) else ""
        age_info = f" (depuis {ts_str})" if ts_str else ""
        lines.append(f"  - {tid} [{reason}]{age_info}\n")

    with open(alert_log, "a", encoding="utf-8") as f:
        f.writelines(lines)

    # Exécuter la commande de notification si configurée
    if notify_cmd:
        os.system(notify_cmd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
