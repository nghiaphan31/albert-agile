#!/usr/bin/env bash
# Lance le proxy LiteLLM pour le mode automatique (routage par complexité)
# Usage: ./scripts/run_litellm_proxy.sh [port] [config]
#   port: 4000 par défaut
#   config: litellm_config.yaml (défaut, spec §5.1b) ou litellm_config_cascade_complete.yaml
# Prérequis: pip install 'litellm[proxy]'
# Clés: GOOGLE_API_KEY ou GEMINI_FREE_KEY, ANTHROPIC_API_KEY ; optionnel: VERTEX_PROJECT, DEEPSEEK_API_KEY, GEMINI_PAYANT_KEY

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Permettre l'import de config.* (custom_roo_hook, litellm_hooks)
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Charger .env si présent
[ -f .env ] && set -a && source .env && set +a
# Fallback GEMINI_FREE_KEY <- GOOGLE_API_KEY (spec §5.1b)
[ -z "$GEMINI_FREE_KEY" ] && [ -n "$GOOGLE_API_KEY" ] && export GEMINI_FREE_KEY="$GOOGLE_API_KEY"

PORT="${1:-4000}"
case "${LITELLM_CONFIG:-}" in
  cascade_complete) CONFIG_FILE="config/litellm_config_cascade_complete.yaml" ;;
  *) CONFIG_FILE="config/litellm_config.yaml" ;;
esac
[ -f "$CONFIG_FILE" ] || CONFIG_FILE="config/litellm_config.yaml"

# Utiliser le venv du projet si disponible
VENV_LITELLM="$ROOT/.venv/bin/litellm"
if [ -x "$VENV_LITELLM" ]; then
  exec "$VENV_LITELLM" --config "$CONFIG_FILE" --port "$PORT"
else
  exec litellm --config "$CONFIG_FILE" --port "$PORT"
fi
