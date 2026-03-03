"""
BaseStore (mémoire long terme) — mode dégradé JSON (spec III.8-A, F10).
Namespaces: project/{id}/adr_counter, project/{id}/sprint_number,
project/{id}/dod/{sprint_number}, project/{id}/architecture, project/{id}/sprints.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_root() -> Path:
    import os
    return Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))


def _get_basestore_dir(project_id: str) -> Path:
    return _get_root() / "data" / "basestore" / project_id.replace("/", "_")


def get(project_id: str, namespace: str, key: str | None = None, default=None):
    """
    Lit une valeur du BaseStore.
    namespace: adr_counter | sprint_number | dod | architecture | sprints
    key: pour dod/sprints = sprint_number (ex. "1") ; omis pour adr_counter/sprint_number/architecture
    """
    root = _get_basestore_dir(project_id)
    if namespace == "adr_counter":
        path = root / "adr_counter.json"
    elif namespace == "sprint_number":
        path = root / "sprint_number.json"
    elif namespace == "dod" and key is not None:
        path = root / "dod" / f"{key}.json"
    elif namespace == "architecture":
        path = root / "architecture.json"
    elif namespace == "sprints" and key is not None:
        path = root / "sprints" / f"{key}.json"
    else:
        return default
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("value", data) if isinstance(data, dict) else data
    except Exception as e:
        logger.warning("BaseStore get %s/%s/%s failed: %s", project_id, namespace, key, e)
        return default


def put(project_id: str, namespace: str, key: str, value):
    """Écrit une valeur dans le BaseStore."""
    root = _get_basestore_dir(project_id)
    if namespace == "adr_counter":
        path = root / "adr_counter.json"
    elif namespace == "sprint_number":
        path = root / "sprint_number.json"
    elif namespace == "dod":
        path = root / "dod" / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
    elif namespace == "architecture":
        path = root / "architecture.json"
    elif namespace == "sprints":
        path = root / "sprints" / f"{key}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise ValueError(f"Unknown namespace: {namespace}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"value": value} if not isinstance(value, (dict, list)) else value
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_project_context(project_id: str, strict: bool) -> dict:
    """
    Charge adr_counter, sprint_number, dod pour un projet.
    strict: AGILE_BASESTORE_STRICT — si True et BaseStore inaccessible → raise;
    si False → valeurs par défaut + WARNING.
    """
    root = _get_basestore_dir(project_id)
    if not root.exists() and strict:
        raise ValueError(
            f"BaseStore inaccessible pour projet '{project_id}'. "
            f"Dossier attendu: {root}. "
            "Créer le projet ou désactiver AGILE_BASESTORE_STRICT."
        )
    if not root.exists():
        logger.warning("BaseStore absent pour %s — valeurs par défaut (AGILE_BASESTORE_STRICT=false)", project_id)
        return {"adr_counter": 0, "sprint_number": 1, "dod": None}

    adr_counter = get(project_id, "adr_counter", default=0)
    sprint_number = get(project_id, "sprint_number", default=1)
    sn = sprint_number if sprint_number is not None else 1
    dod = get(project_id, "dod", key=str(sn), default=None)

    return {
        "adr_counter": adr_counter if adr_counter is not None else 0,
        "sprint_number": sprint_number if sprint_number is not None else 1,
        "dod": dod,
    }
