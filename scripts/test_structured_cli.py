#!/usr/bin/env python3

"""
Petit utilitaire CLI pour tester les modèles dans le même mode structuré
que le graph (cascade N0→N1→N2 avec `with_structured_output`).

Exemples d'usage :

    # Epic avec Tier 1 (R0 / R2)
    python3 scripts/test_structured_cli.py epic --tier tier1 \
        --prompt "Propose une Epic pour un système de gestion de tâches."

    # Architecture avec prompt pris sur stdin
    echo "Décris l'architecture logique pour une app de notes." | \
        python3 scripts/test_structured_cli.py architecture --tier tier1

    # Sprint Backlog avec Tier 2 (R3-R6)
    python3 scripts/test_structured_cli.py sprint-backlog --tier tier2 \
        --prompt "Prépare un sprint backlog d'une semaine pour livrer une fonctionnalité de recherche."
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable, Dict, Tuple

from graph.cascade import call_with_cascade
from graph.llm_factory import get_llms_tier1, get_llms_tier2
from graph.schemas import ArchitectureOutput, EpicOutput, SprintBacklogOutput


SchemaType = Any
LLMFactory = Callable[[], Tuple[Any, Any, Any]]


SCHEMAS: Dict[str, SchemaType] = {
    "epic": EpicOutput,
    "architecture": ArchitectureOutput,
    "sprint-backlog": SprintBacklogOutput,
}

TIERS: Dict[str, LLMFactory] = {
    "tier1": get_llms_tier1,
    "tier2": get_llms_tier2,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Tester les modèles de la cascade (N0→N1→N2) "
            "avec sorties structurées Pydantic, comme dans le graph."
        )
    )
    parser.add_argument(
        "schema",
        choices=sorted(SCHEMAS.keys()),
        help="Type de sortie structurée à utiliser.",
    )
    parser.add_argument(
        "--tier",
        choices=sorted(TIERS.keys()),
        default="tier1",
        help="Jeu de modèles à utiliser (tier1 pour R0/R2, tier2 pour R3-R6).",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        help=(
            "Prompt à envoyer au modèle. "
            "Si omis, le prompt est lu sur stdin."
        ),
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Afficher la sortie brute (repr) au lieu de JSON formaté.",
    )
    return parser.parse_args()


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    data = sys.stdin.read()
    if not data.strip():
        raise SystemExit(
            "Prompt vide. Fournis un --prompt ou passe le texte via stdin."
        )
    return data


def _to_json_serializable(result: Any) -> Any:
    """Essaie de convertir le résultat en structure JSON-sérialisable."""
    # Cas Pydantic v2
    if hasattr(result, "model_dump"):
        return result.model_dump()

    # Cas Pydantic v1 éventuel
    if hasattr(result, "dict") and callable(getattr(result, "dict")):
        try:
            return result.dict()
        except Exception:
            pass

    # Cas déjà dict / list / primitive
    if isinstance(result, (dict, list, str, int, float, bool)) or result is None:
        return result

    # Fallback : représentation texte
    return repr(result)


def main() -> None:
    args = _parse_args()
    prompt = _read_prompt(args)

    schema = SCHEMAS[args.schema]
    llm_factory = TIERS[args.tier]
    llm_n0, llm_n1, llm_n2 = llm_factory()

    result = call_with_cascade(llm_n0, llm_n1, llm_n2, prompt, schema=schema)

    if args.raw:
        print(result)
        return

    data = _to_json_serializable(result)
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

