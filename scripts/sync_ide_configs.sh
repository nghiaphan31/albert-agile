#!/usr/bin/env bash
# Synchronise les configs IDE (Roo Code) entre les fichiers réels et le dépôt.
# Usage: ./scripts/sync_ide_configs.sh to-repo | to-real
#
# to-repo  : copie ~/.config/roo-code-settings.json → config/reference/
# to-real  : copie config/reference/roo-code-settings.json → ~/.config/

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROO_REAL="$HOME/.config/roo-code-settings.json"
ROO_REF="$ROOT/config/reference/roo-code-settings.json"

case "${1:-}" in
  to-repo)
    if [ ! -f "$ROO_REAL" ]; then
      echo "Erreur: $ROO_REAL n'existe pas" >&2
      exit 1
    fi
    cp "$ROO_REAL" "$ROO_REF"
    echo "Sync to-repo OK: roo-code-settings.json"
    ;;
  to-real)
    if [ ! -f "$ROO_REF" ]; then
      echo "Erreur: $ROO_REF n'existe pas" >&2
      exit 1
    fi
    mkdir -p "$(dirname "$ROO_REAL")"
    cp "$ROO_REF" "$ROO_REAL"
    echo "Sync to-real OK: roo-code-settings.json"
    echo "Pense à recharger VS Code (F1 → Reload Window) pour que Roo importe le fichier."
    ;;
  *)
    echo "Usage: $0 to-repo | to-real" >&2
    exit 1
    ;;
esac
