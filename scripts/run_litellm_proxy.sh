#!/usr/bin/env bash
# Lance le proxy LiteLLM pour le mode automatique (routage par complexité)
# Usage: ./scripts/run_litellm_proxy.sh  [port par défaut: 4000]
# Prérequis: pip install 'litellm[proxy]'
# Clés API: GOOGLE_API_KEY, ANTHROPIC_API_KEY dans .env ou environnement

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Charger .env si présent
[ -f .env ] && set -a && source .env && set +a

PORT="${1:-4000}"
exec litellm --config config/litellm_config.yaml --port "$PORT"
