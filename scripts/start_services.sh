#!/usr/bin/env bash
# Démarrage unifié pour Roo / LangGraph — spec Stratégie Routage Intelligent
# Lance Presidio, SearXNG (Docker) puis le proxy LiteLLM
#
# Usage: ./scripts/start_services.sh [--no-docker] [--no-litellm]
#   --no-docker   : ne pas lancer Presidio/SearXNG (utiliser si déjà lancés ou non souhaités)
#   --no-litellm  : ne lancer que Docker (LiteLLM à lancer séparément)
#
# Pour Roo : exécuter ce script, puis configurer Roo pour pointer vers http://localhost:4000
# Pour LangGraph : idem + AGILE_USE_LITELLM_PROXY=true

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

[ -f .env ] && set -a && source .env && set +a

DO_DOCKER=true
DO_LITELLM=true
for arg in "$@"; do
  case "$arg" in
    --no-docker)  DO_DOCKER=false ;;
    --no-litellm) DO_LITELLM=false ;;
  esac
done

# --- Docker : Presidio + SearXNG ---
if $DO_DOCKER; then
  if command -v docker &>/dev/null; then
    if docker compose version &>/dev/null 2>&1; then
      echo "[start_services] Lancement Presidio + SearXNG (docker compose)..."
      docker compose up -d presidio-analyzer presidio-anonymizer searxng
    elif command -v docker-compose &>/dev/null; then
      echo "[start_services] Lancement Presidio + SearXNG (docker-compose)..."
      docker-compose up -d presidio-analyzer presidio-anonymizer searxng
    else
      echo "[start_services] Avertissement: docker compose / docker-compose absents. Presidio et SearXNG non démarrés."
      echo "  Pour Presidio: docker run -d -p 5002:5002 mcr.microsoft.com/presidio-analyzer:latest"
      echo "  Pour Presidio: docker run -d -p 5001:5001 mcr.microsoft.com/presidio-anonymizer:latest"
      echo "  Pour SearXNG:  docker run -d -p 8080:8080 -v $ROOT/config/searxng:/etc/searxng:ro searxng/searxng:latest"
    fi
  else
    echo "[start_services] Docker non installé. Presidio et SearXNG ignorés."
  fi
fi

# --- Proxy LiteLLM ---
if $DO_LITELLM; then
  echo "[start_services] Lancement proxy LiteLLM (port 4000)..."
  exec ./scripts/run_litellm_proxy.sh 4000
fi
