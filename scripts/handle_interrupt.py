#!/usr/bin/env python3
"""
Gestion des interrupts H1–H6 (spec III.8-B).
Liste les threads en attente, affiche le payload __interrupt__, demande feedback.
Envoie la résolution via LangServe POST /runs/{thread_id}/resume si disponible.
"""
import argparse
import os
import sys

# LangServe API URL (serve.py doit tourner)
LANGSERVE_BASE = os.environ.get("AGILE_LANGSERVE_URL", "http://localhost:8000")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gérer les interrupts H1–H6")
    parser.add_argument("--thread-id", help="Thread ID spécifique (sinon liste tous)")
    parser.add_argument("--approved", action="store_true", help="Approuver l'interrupt")
    parser.add_argument("--rejected", action="store_true", help="Rejeter l'interrupt")
    parser.add_argument("--feedback", help="Envoyer un feedback texte")
    args = parser.parse_args()

    # Stub : LangServe non déployé → message d'attente
    print("handle_interrupt: À implémenter quand LangServe tourne.")
    print("  Usage prévu: POST {base}/runs/{{thread_id}}/resume avec payload Command(resume=...)")
    print(f"  Base URL: {LANGSERVE_BASE}")
    if args.thread_id:
        print(f"  Thread: {args.thread_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
