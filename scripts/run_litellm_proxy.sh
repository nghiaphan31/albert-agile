#!/usr/bin/env bash
# Lance le proxy LiteLLM pour le mode automatique (routage par complexité)
# Usage: ./scripts/run_litellm_proxy.sh [port] [config]
#   port: 4000 par défaut
#   config: litellm_config.yaml (défaut, spec §5.1b) ou litellm_config_cascade_complete.yaml
# Prérequis: pip install 'litellm[proxy]'
# Clés: GOOGLE_API_KEY ou GEMINI_FREE_KEY, ANTHROPIC_API_KEY ; optionnel: VERTEX_PROJECT, DEEPSEEK_API_KEY, GEMINI_PAYANT_KEY
#
# NOTE Port : LiteLLM change silencieusement le port si 4000 est occupé (proxy_cli.py L861).
# Ce script vérifie avant démarrage pour éviter un port aléatoire (ex. 36795) invisible pour Roo.

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

# Vérifier si le port est libre (LiteLLM bascule silencieusement sur un port aléatoire sinon)
if (echo >/dev/tcp/127.0.0.1/"$PORT") 2>/dev/null; then
  echo "[run_litellm_proxy] ERREUR: Le port $PORT est déjà utilisé." >&2
  echo "  Libre le port (p.ex. arrêter un proxy LiteLLM existant) ou lancez avec un autre port:" >&2
  echo "  ./scripts/run_litellm_proxy.sh 4001" >&2
  exit 1
fi
case "${LITELLM_CONFIG:-}" in
  cascade_complete) CONFIG_FILE="config/litellm_config_cascade_complete.yaml" ;;
  *) CONFIG_FILE="config/litellm_config.yaml" ;;
esac
[ -f "$CONFIG_FILE" ] || CONFIG_FILE="config/litellm_config.yaml"

# Forcer le port pour éviter tout override (LiteLLM lit aussi PORT)
export PORT

# Debug : si ROO_DEBUG_LOG défini, le hook log model_in → model_out
[ -n "$ROO_DEBUG_LOG" ] && echo "[run_litellm_proxy] ROO_DEBUG_LOG=$ROO_DEBUG_LOG (hook tracera le routage)"

# Utiliser le venv du projet si disponible
VENV_LITELLM="$ROOT/.venv/bin/litellm"
EXTRA_ARGS=""
[ -n "$LITELLM_DEBUG" ] && EXTRA_ARGS="--detailed_debug"
if [ -x "$VENV_LITELLM" ]; then
  exec $VENV_LITELLM --config "$CONFIG_FILE" --port "$PORT" $EXTRA_ARGS
else
  exec litellm --config "$CONFIG_FILE" --port "$PORT" $EXTRA_ARGS
fi
