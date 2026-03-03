"""
Lois Albert Core pour les agents Agile (spec III.5, plan lois §5.1, §5.2).
Chargé par chaque nœud pour injection dans le system prompt.
"""

from dataclasses import dataclass
from typing import Any

# 21 lois universelles (U03) + L21 Doc-as-code
LAWS: list[dict[str, str]] = [
    {"id": "L0", "name": "Auto-application", "principle": "Ces lois s'appliquent à tout projet et à la conception d'Albert."},
    {"id": "L1", "name": "Anti-précipitation", "principle": "Aucun code/spec final tant que l'intention du client n'est pas univoque. Décomposition socratique, Sign-off obligatoire."},
    {"id": "L2", "name": "Traçabilité verticale", "principle": "Chaque exigence vérifiable (tests) et liée explicitement à son parent."},
    {"id": "L3", "name": "Rétrofit permanent", "principle": "Toute découverte technique majeure → d'abord mettre à jour /specs, valider, puis adapter le code."},
    {"id": "L4", "name": "Gabarit CDC", "principle": "Tout projet doit contenir : modélisation visuelle (Mermaid), specs transverses, matrice d'exigences, manuel d'implémentation."},
    {"id": "L5", "name": "Confinement spatial", "principle": "Séparation stricte : dossiers nobles vs opérationnels. Aucun fichier IA directement dans les nobles (quarantaine obligatoire)."},
    {"id": "L6", "name": "V.A.R.", "principle": "Plans exécutables en mode « aveugle » : blocs complets, nomenclature 4D, checkpoints V.A.R., règles A/B/C."},
    {"id": "L7", "name": "Transparence", "principle": "Logs exhaustifs, attribution du modèle IA dans les manifestes."},
    {"id": "L8", "name": "Non-destruction", "principle": "Interdiction de eval, exec, rm -rf hors périmètre."},
    {"id": "L9", "name": "Zéro-hardcode", "principle": "Aucun chemin absolu ni secret en dur. Variables d'environnement ou project.json."},
    {"id": "L10", "name": "Non-collision parent", "principle": "Ne jamais redéfinir une méthode du framework parent."},
    {"id": "L11", "name": "Env explicite", "principle": "load_dotenv() obligatoire AVANT toute utilisation d'API ou os.environ."},
    {"id": "L12", "name": "Structure avant install", "principle": "Structure physique (__init__.py, etc.) créée AVANT poetry install."},
    {"id": "L13", "name": "Env managé", "principle": "Toujours poetry run python, jamais python nu."},
    {"id": "L14", "name": "Signature avant instanciation", "principle": "Vérifier la signature de __init__ avant d'instancier."},
    {"id": "L15", "name": "Intégration E2E", "principle": "Manuel avec >3 phases doit inclure Phase d'intégration + test E2E + diagramme de séquence."},
    {"id": "L16", "name": "Rendu multi-plateforme", "principle": "Tester la doc (Markdown, Mermaid, code fences) dans tous les outils cibles."},
    {"id": "L17", "name": "PROJECT_ROOT programmatique", "principle": "Recherche ascendante de marqueur (pyproject.toml, .git) — pas de .parent hardcodé."},
    {"id": "L18", "name": "Arrêt sur contradiction", "principle": "Si deux specs se contredisent : citer les deux, expliquer l'impact, proposer, attendre Sign-off. Jamais arbitrer silencieusement."},
    {"id": "L19", "name": "Idempotence avant création", "principle": "Avant de créer un fichier : vérifier s'il existe. Si conforme ou supérieur → conserver."},
    {"id": "L20", "name": "Taille max document", "principle": "Fichier .md dans /specs ≤ 800 lignes. Au-delà : split en fichiers partiels."},
    {"id": "L21", "name": "Doc-as-code / Doc-in-code", "principle": "Docstrings obligatoires sur éléments publics ; doc générée (sphinx-build) si API modifiée."},
]

# Loi L-ANON (anonymisation cloud)
LAW_ANON = {"id": "L-ANON", "name": "Anonymisation cloud", "principle": "Aucune donnée personnelle ne quitte Calypso vers le cloud (Gemini, Claude) sans anonymisation préalable."}

# Mapping lois par rôle (R-0 à R-6)
TRANSVERSE_LAW_IDS = {"L0", "L3", "L7", "L8", "L9", "L11", "L18"}

LAWS_BY_ROLE: dict[str, list[str]] = {
    "r0": ["L1", "L4"],       # Albert Business Analyst
    "r2": ["L2", "L5", "L18"],  # Albert System Architect
    "r3": ["L6"],             # Albert Scrum Master
    "r4": ["L8", "L9", "L19", "L21"],  # Albert Dev Team
    "r5": ["L7", "L8"],       # Albert Release Manager
    "r6": ["L15", "L21"],     # Albert QA & DevOps
}

# Règles A, B, C, D
RULES = {
    "A": "Commandes en code fence bash, une par ligne, bouton Copy GitHub.",
    "B": "Tableaux Markdown avec pipes. Backlog, Architecture, Sprint Backlog en tableaux Markdown.",
    "C": "Prompts IA en bloc texte avec frontmatter YAML.",
    "D": "Docstrings obligatoires sur éléments publics ; doc générée si API modifiée.",
}

# Règles Tests
RULES_TESTS = {
    "pipeline_order": "build_docs → unit → intégration → E2E",
    "l21_doc_as_code": "R-6 refuse commit R-4 sans docstrings ou modification API sans mise à jour doc (si BUILD_DOCS_REQUIRED=true).",
    "self_healing_max": "SELF_HEALING_MAX_ITERATIONS=3.",
}


def get_laws_for_role(role: str, include_transverse: bool = True) -> list[dict[str, str]]:
    """
    Retourne la liste des lois applicables à un rôle (r0, r2, r3, r4, r5, r6).
    """
    law_ids = set(LAWS_BY_ROLE.get(role, []))
    if include_transverse:
        law_ids |= TRANSVERSE_LAW_IDS
    result = [law for law in LAWS if law["id"] in law_ids]
    result.append(LAW_ANON)
    return result


def format_laws_for_prompt(role: str) -> str:
    """Formatte les lois du rôle pour injection dans un system prompt."""
    laws = get_laws_for_role(role)
    lines = ["Lois Albert Core applicables :"]
    for law in laws:
        lines.append(f"- {law['id']} {law['name']}: {law['principle']}")
    return "\n".join(lines)
