#!/usr/bin/env bash
# Lance le proxy LiteLLM pour le mode automatique (routage par complexité)
# Usage: ./scripts/run_litellm_proxy.sh [port] [config]
#   port: 4000 par défaut
#   config: litellm_config.yaml (défaut) ou litellm_config_cascade_complete.yaml
#   Ou: LITELLM_CONFIG=cascade_complete pour la cascade Coût Zéro (spec §5.1b)
# Prérequis: pip install 'litellm[proxy]'
# Clés: GOOGLE_API_KEY, ANTHROPIC_API_KEY ; pour cascade_complete: GEMINI_FREE_KEY, VERTEX_PROJECT, DEEPSEEK_API_KEY

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Charger .env si présent
[ -f .env ] && set -a && source .env && set +a

PORT="${1:-4000}"
case "${LITELLM_CONFIG:-}" in
  cascade_complete) CONFIG_FILE="config/litellm_config_cascade_complete.yaml" ;;
  *) CONFIG_FILE="config/litellm_config.yaml" ;;
esac
[ -f "$CONFIG_FILE" ] || CONFIG_FILE="config/litellm_config.yaml"
exec litellm --config "$CONFIG_FILE" --port "$PORT"
