#!/usr/bin/env python3
"""
Purge des checkpoints > max-age-days (spec III.8-L).
Exclut les threads avec __interrupt__ non résolu.
Protège les sprints actifs si --protect-active-sprints.
"""
import argparse
import os
import sys
from pathlib import Path


def get_checkpoint_path() -> Path:
    root = os.environ.get("AGILE_ORCHESTRATION_ROOT", "")
    if not root:
        return Path.cwd() / "checkpoints.sqlite"
    return Path(root) / "checkpoints.sqlite"


def main() -> int:
    parser = argparse.ArgumentParser(description="Purge des vieux checkpoints")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans supprimer")
    parser.add_argument("--max-age-days", type=int, default=90, help="Âge max en jours")
    parser.add_argument("--protect-active-sprints", action="store_true", default=True)
    args = parser.parse_args()

    ckpt = get_checkpoint_path()
    if not ckpt.exists():
        print(f"Pas de checkpoints trouvés: {ckpt}")
        return 0

    # Stub: implémentation complète nécessite accès SqliteSaver / langgraph-checkpoint
    print(f"purge_checkpoints: dry_run={args.dry_run}, max_age_days={args.max_age_days}")
    print(f"  Checkpoint path: {ckpt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
