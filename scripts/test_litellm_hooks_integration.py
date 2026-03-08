#!/usr/bin/env python3
"""
Script d'aide pour tester les hooks LiteLLM (custom_roo_hook + litellm_hooks)
sans Roo Code.

Envoie une requête HTTP vers localhost:4000/v1/chat/completions et affiche
la réponse. Vérifie que les hooks (routage sémantique, injection, post-call)
fonctionnent.

Prérequis :
  - LiteLLM proxy lancé : ./scripts/run_litellm_proxy.sh
  - Ollama + nomic-embed-text (pour routage sémantique)

Usage :
  python scripts/test_litellm_hooks_integration.py
  python scripts/test_litellm_hooks_integration.py --model worker --prompt "Fix this bug"
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def main():
    parser = argparse.ArgumentParser(description="Tester les hooks LiteLLM via HTTP")
    parser.add_argument(
        "--url",
        default="http://localhost:4000/v1/chat/completions",
        help="URL du proxy LiteLLM",
    )
    parser.add_argument(
        "--model",
        default="worker",
        help="Modèle virtuel (worker, architect, ingest) ou alias",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        default="Refactor the function in utils.py to use type hints",
        help="Prompt utilisateur",
    )
    parser.add_argument("--raw", action="store_true", help="Afficher la réponse brute JSON")
    args = parser.parse_args()

    body = {
        "model": args.model,
        "messages": [{"role": "user", "content": args.prompt}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "ask_followup_question",
                    "description": "Ask the user a follow-up question",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "follow_up": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["question", "follow_up"],
                    },
                },
            },
        ],
        "tool_choice": "auto",
    }

    req = urllib.request.Request(
        args.url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print("Erreur connexion au proxy LiteLLM (port 4000?) :", e, file=sys.stderr)
        sys.exit(1)

    if args.raw:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    choices = data.get("choices", [])
    if not choices:
        print("Aucune réponse reçue")
        sys.exit(1)

    msg = choices[0].get("message", {})
    content = msg.get("content") or ""
    tool_calls = msg.get("tool_calls") or []

    print("--- Réponse ---")
    if content:
        print("Content:", content[:500] + ("..." if len(content) > 500 else ""))
    for tc in tool_calls:
        fn = tc.get("function", {})
        print("Tool:", fn.get("name"), "- args:", fn.get("arguments", "")[:200])
    print("--- Fin ---")


if __name__ == "__main__":
    main()
