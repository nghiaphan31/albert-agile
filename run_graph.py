#!/usr/bin/env python3
"""CLI pour lancer le graphe Agile (spec III.8)."""
import argparse
import socket
import os
import sys

# Charger .env avant les imports
from dotenv import load_dotenv

load_dotenv()

from graph.graph import graph


def _is_litellm_reachable(host: str = "localhost", port: int = 4000, timeout: float = 2.0) -> bool:
    """Vérifie si le proxy LiteLLM est accessible."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.error, OSError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--start-phase", choices=["E1", "E3", "HOTFIX"], default="E1")
    parser.add_argument("--thread-id", default=None)
    parser.add_argument("--hotfix-description", default="")
    args = parser.parse_args()

    thread_id = args.thread_id or f"{args.project_id}-phase-0"
    config = {"configurable": {"thread_id": thread_id}}

    # Vérifier que le proxy LiteLLM est accessible si AGILE_USE_LITELLM_PROXY est activé
    use_proxy = os.environ.get("AGILE_USE_LITELLM_PROXY", "").lower() in ("1", "true", "yes")
    if use_proxy:
        base = os.environ.get("AGILE_LITELLM_BASE_URL", "http://localhost:4000/v1")
        try:
            if base.startswith("http://"):
                host = base.split("//")[1].split(":")[0]
                port = int(base.split(":")[-1].split("/")[0])
            elif base.startswith("https://"):
                host = base.split("//")[1].split(":")[0]
                port = int(base.split(":")[-1].split("/")[0]) if ":" in base.split("//")[1] else 443
            else:
                host, port = "localhost", 4000
        except (IndexError, ValueError):
            host, port = "localhost", 4000
        if not _is_litellm_reachable(host, port):
            print(
                "Erreur: AGILE_USE_LITELLM_PROXY est activé mais le proxy LiteLLM n'est pas accessible.",
                file=sys.stderr,
            )
            print(f"  Vérifiez que {host}:{port} répond.", file=sys.stderr)
            print("  Lancez d'abord: ./scripts/start_services.sh", file=sys.stderr)
            return 1

    initial = {
        "project_id": args.project_id,
        "project_root": None,
        "start_phase": args.start_phase,
        "hotfix_description": args.hotfix_description if args.start_phase == "HOTFIX" else "",
    }

    try:
        result = graph.invoke(initial, config=config)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        return 1

    if "__interrupt__" in result:
        interrupts = result["__interrupt__"]
        print(f"\nGraphe suspendu — {len(interrupts)} interrupt(s) en attente:")
        for i, intr in enumerate(interrupts, 1):
            val = intr.value if hasattr(intr, "value") else intr
            print(f"  [{i}] {val}")
        print(f"\nPour valider ou rejeter:")
        print(f"  python scripts/handle_interrupt.py --thread-id {thread_id}")
        return 0

    print("\nRun terminé. État final:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
