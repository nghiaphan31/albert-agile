#!/bin/bash
# Ajoute une entrée cron pour notify_pending_interrupts (spec F5).
# Usage: ./setup_cron_notify.sh [--orchestration-root <path>]
# Cron: toutes les heures (0 * * * *)

ORCH_ROOT="${AGILE_ORCHESTRATION_ROOT:-}"
while [[ $# -gt 0 ]]; do
  case $1 in
    --orchestration-root) ORCH_ROOT="$2"; shift 2 ;;
    *) echo "Usage: $0 [--orchestration-root <path>]"; exit 2 ;;
  esac
done

if [ -z "$ORCH_ROOT" ]; then
  ORCH_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
  echo "Using AGILE_ORCHESTRATION_ROOT=$ORCH_ROOT"
fi

PYTHON="$ORCH_ROOT/.venv/bin/python"
SCRIPT="$ORCH_ROOT/scripts/notify_pending_interrupts.py"
CRON_LINE="0 * * * * AGILE_ORCHESTRATION_ROOT=$ORCH_ROOT $PYTHON $SCRIPT >> $ORCH_ROOT/logs/notify_cron.log 2>&1"

if ! [ -x "$PYTHON" ]; then
  echo "Erreur: $PYTHON introuvable ou non exécutable."
  exit 1
fi

# Vérifier si l'entrée existe déjà
if crontab -l 2>/dev/null | grep -F "notify_pending_interrupts" >/dev/null; then
  echo "Entrée cron notify_pending_interrupts déjà présente."
  exit 0
fi

# Ajouter l'entrée
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
echo "Cron ajouté: $CRON_LINE"
echo "Vérifier avec: crontab -l"
