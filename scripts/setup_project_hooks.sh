#!/bin/bash
# Usage: ./setup_project_hooks.sh --orchestration-root <path> --project-root <path> --project-id <id>

ORCH_ROOT=""
PROJECT_ROOT=""
PROJECT_ID=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --orchestration-root) ORCH_ROOT="$2"; shift 2 ;;
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --project-id) PROJECT_ID="$2"; shift 2 ;;
    *) echo "Usage: $0 --orchestration-root <path> --project-root <path> --project-id <id>"; exit 2 ;;
  esac
done

[ -z "$ORCH_ROOT" ] || [ -z "$PROJECT_ROOT" ] || [ -z "$PROJECT_ID" ] && { echo "Missing args"; exit 2; }

echo "$PROJECT_ID" > "$PROJECT_ROOT/.agile-project-id"
cat > "$PROJECT_ROOT/.agile-env" << EOF
AGILE_ORCHESTRATION_ROOT=$ORCH_ROOT
AGILE_PROJECT_ID=$PROJECT_ID
AGILE_DEFER_INDEX=true
AGILE_PROJECTS_JSON=$ORCH_ROOT/config/projects.json
AGILE_RAG_FILE_WATCHER=false
AGILE_RAG_INCREMENTAL=false
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
