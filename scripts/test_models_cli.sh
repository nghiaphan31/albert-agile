#!/usr/bin/env bash
# Tests CLI des modèles recommandés (RTX 5060 Ti 16G)
# Usage: ./scripts/test_models_cli.sh [code|ideation|structured|all]
# Depuis la racine du projet, avec venv activé si structured.

set -e

ROOT="$(cd "$(dirname -- "$0")/.." && pwd)"
PROMPT_C1='Écris une fonction Python def fib(n: int) -> int avec docstring et type hints. Pas de récursif.'
PROMPT_I1='Propose une Epic (titre, problème, solution en 2 phrases) pour une app de suivi de dépenses.'

test_code_cli() {
    local model="$1"
    echo "=== Test CLI code: $model ==="
    if ollama run "$model" "$PROMPT_C1" 2>/dev/null | grep -q 'def fib'; then
        echo "OK: sortie contient def fib"
    else
        echo "WARN: pas de def fib détecté (vérifier manuellement)"
    fi
}

test_ideation_cli() {
    local model="$1"
    echo "=== Test CLI idéation: $model ==="
    ollama run "$model" "$PROMPT_I1" 2>/dev/null | head -20
    echo "..."
}

test_structured() {
    local tier="$1" model="$2" schema="$3"
    local var="AGILE_TIER${tier}_N0_MODEL"
    echo "=== Test structured $schema (${var}=$model) ==="
    export "$var=$model"
    if (cd "$ROOT" && PYTHONPATH="$ROOT" python scripts/test_structured_cli.py "$schema" --tier "tier$tier" -p "Test minimal." 2>/dev/null) | python -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        echo "OK: JSON valide"
    else
        echo "WARN: échec ou JSON invalide"
    fi
}

main() {
    case "${1:-all}" in
        code)
            for m in qwen2.5-coder:14b deepseek-coder-v2:16b; do test_code_cli "$m"; done
            ;;
        ideation)
            test_ideation_cli "qwen2.5:14b"
            ;;
        structured)
            test_structured 2 "qwen2.5-coder:14b" "sprint-backlog"
            test_structured 1 "qwen2.5:14b" "epic"
            ;;
        all)
            test_code_cli "qwen2.5-coder:14b"
            test_code_cli "deepseek-coder-v2:16b"
            test_ideation_cli "qwen2.5:14b"
            test_structured 2 "qwen2.5-coder:14b" "sprint-backlog"
            test_structured 1 "qwen2.5:14b" "epic"
            ;;
        *)
            echo "Usage: $0 [code|ideation|structured|all]"
            exit 1
            ;;
    esac
}

main "$@"
