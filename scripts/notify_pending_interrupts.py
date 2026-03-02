#!/usr/bin/env python3
"""
Alertes pour interrupts en attente > AGILE_INTERRUPT_TIMEOUT_HOURS (spec F5, III.8-B).
Écrit dans logs/pending_interrupts_alert.log.
Exécute AGILE_NOTIFY_CMD si défini (email, webhook).
"""
import os
import sys
from pathlib import Path
from datetime import datetime


def main() -> int:
    root = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    alert_log = log_dir / "pending_interrupts_alert.log"
    timeout_hours = int(os.environ.get("AGILE_INTERRUPT_TIMEOUT_HOURS", "48"))

    # Stub: nécessite accès au checkpointer pour lister les interrupts
    # Pour l'instant, on écrit une entrée de test si le script est appelé
    with open(alert_log, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} notify_pending_interrupts: stub (timeout_hours={timeout_hours})\n")

    notify_cmd = os.environ.get("AGILE_NOTIFY_CMD")
    if notify_cmd:
        os.system(notify_cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
