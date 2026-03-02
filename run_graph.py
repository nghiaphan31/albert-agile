#!/usr/bin/env python3
"""CLI pour lancer le graphe Agile (spec III.8)."""
import argparse
import os
import sys

# Charger .env avant les imports
from dotenv import load_dotenv

load_dotenv()

from graph.graph import graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--start-phase", choices=["E1", "E3", "HOTFIX"], default="E1")
    parser.add_argument("--thread-id", default=None)
    parser.add_argument("--hotfix-description", default="")
    args = parser.parse_args()

    thread_id = args.thread_id or f"{args.project_id}-phase-0"
    config = {"configurable": {"thread_id": thread_id}}

    initial = {
        "project_id": args.project_id,
        "project_root": None,
        "start_phase": args.start_phase,
        "hotfix_description": args.hotfix_description if args.start_phase == "HOTFIX" else "",
    }

    try:
        for chunk in graph.invoke(initial, config=config, stream_mode="values"):
            print(chunk)
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
