#!/bin/bash
# Usage: ./setup_project_hooks.sh --orchestration-root <path> --project-root <path> --project-id <id>

ORCH_ROOT=""
PROJECT_ROOT=""
PROJECT_ID=""

detect_gpu_profile() {
  # Override explicite possible via variable d'env exportée avant l'appel du script
  if [ -n "${AGILE_GPU_PROFILE:-}" ]; then
    echo "$AGILE_GPU_PROFILE"
    return 0
  fi

  if command -v nvidia-smi >/dev/null 2>&1; then
    # memory.total est en MiB (nounits)
    local vram_mib
    vram_mib="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n 1 | tr -d ' ')"
    if [[ "$vram_mib" =~ ^[0-9]+$ ]]; then
      # Seuil approximatif : 16 Go ~= 16384 MiB
      if [ "$vram_mib" -ge 15000 ]; then
        echo "vram_16gb"
        return 0
      fi
      echo "legacy_12gb"
      return 0
    fi
  fi

  # Fallback : profil moderne (VRAM ≥ 16 Go recommandé)
  echo "vram_16gb"
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --orchestration-root) ORCH_ROOT="$2"; shift 2 ;;
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    *) echo "Usage: $0 --orchestration-root <path> --project-root <path> --project-id <id>"; exit 2 ;;
  esac
done

[ -z "$ORCH_ROOT" ] || [ -z "$PROJECT_ROOT" ] || [ -z "$PROJECT_ID" ] && { echo "Missing args"; exit 2; }

GPU_PROFILE="$(detect_gpu_profile)"

DEFER_INDEX="true"
RAG_INCREMENTAL="false"
RAG_FILE_WATCHER="false"

if [ "$GPU_PROFILE" = "vram_16gb" ]; then
  # Par défaut, on garde l'indexation différée (sécurité), mais on autorise l'incrémental.
  RAG_INCREMENTAL="true"
fi

echo "$PROJECT_ID" > "$PROJECT_ROOT/.agile-project-id"
cat > "$PROJECT_ROOT/.agile-env" << EOF
AGILE_ORCHESTRATION_ROOT=$ORCH_ROOT
AGILE_PROJECT_ID=$PROJECT_ID
AGILE_GPU_PROFILE=$GPU_PROFILE
AGILE_DEFER_INDEX=$DEFER_INDEX
AGILE_PROJECTS_JSON=$ORCH_ROOT/config/projects.json
AGILE_RAG_FILE_WATCHER=$RAG_FILE_WATCHER
AGILE_RAG_INCREMENTAL=$RAG_INCREMENTAL
AGILE_BASESTORE_STRICT=true
AGILE_INTERRUPT_TIMEOUT_HOURS=48
SYNC_ARTIFACTS_CRON="0 0 * * 0"
EOF

# Hook Git post-commit (spec III.8-C) : indexation différée ou pending_index.log
HOOK_FILE="$PROJECT_ROOT/.git/hooks/post-commit"
mkdir -p "$PROJECT_ROOT/.git/hooks"
cat > "$HOOK_FILE" << 'HOOK'
#!/bin/bash
ROOT="$(git rev-parse --show-toplevel)"
[ -f "$ROOT/.agile-env" ] && source "$ROOT/.agile-env"
ORCH="${AGILE_ORCHESTRATION_ROOT:-}"
PID="${AGILE_PROJECT_ID:-}"
[ -z "$PID" ] && [ -f "$ROOT/.agile-project-id" ] && PID=$(cat "$ROOT/.agile-project-id")
[ -z "$ORCH" ] || [ -z "$PID" ] && exit 0
mkdir -p "$ORCH/logs"
if [ "${AGILE_DEFER_INDEX:-true}" = "true" ]; then
  echo "$(date -Iseconds) $(git rev-parse HEAD) $PID" >> "$ORCH/logs/pending_index.log"
else
  python "$ORCH/scripts/index_rag.py" --project-root "$ROOT" --project-id "$PID" 2>/dev/null || true
fi
HOOK
chmod +x "$HOOK_FILE"

cd "$PROJECT_ROOT"
git checkout -b develop main 2>/dev/null || true
git push -u origin develop 2>/dev/null || true
