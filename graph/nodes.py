"""Noeuds du graphe Agile (R-0 a R-6). Implementation minimale."""
import json
import logging
import os
from pathlib import Path

from graph.state import State

logger = logging.getLogger(__name__)

_ORCH_ROOT = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
_PROJECTS_JSON = Path(os.environ.get("AGILE_PROJECTS_JSON", _ORCH_ROOT / "config" / "projects.json"))
_BASESTORE_STRICT = os.environ.get("AGILE_BASESTORE_STRICT", "true").lower() == "true"


def _load_projects() -> dict:
    """Lit config/projects.json ; retourne {} si absent."""
    if _PROJECTS_JSON.exists():
        try:
            return json.loads(_PROJECTS_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Impossible de lire %s : %s", _PROJECTS_JSON, e)
    return {}


def load_context(state: State) -> dict:
    """
    Charge le contexte depuis config/projects.json et le BaseStore (spec III.8-A).

    Résolution de project_root :
      1. Utilise la valeur déjà dans l'état si elle est non-None.
      2. Sinon, la lit depuis config/projects.json via AGILE_PROJECTS_JSON.
      3. Si le projet est introuvable et AGILE_BASESTORE_STRICT=true → exception.
         Si AGILE_BASESTORE_STRICT=false → WARNING + project_root = répertoire courant.

    Le routing E1/E3/HOTFIX est géré par l'edge conditionnelle dans graph.py,
    pas ici — load_context n'a pas besoin de retourner de signal de routing.
    """
    project_id = state.get("project_id", "")
    project_root = state.get("project_root")

    if project_root is None:
        projects = _load_projects()
        entry = {k: v for k, v in projects.items() if not k.startswith("_")}.get(project_id)
        if entry and entry.get("path"):
            project_root = Path(entry["path"])
        else:
            msg = (
                f"Projet '{project_id}' introuvable dans {_PROJECTS_JSON}. "
                "Vérifier config/projects.json."
            )
            if _BASESTORE_STRICT:
                raise ValueError(msg)
            logger.warning("%s — AGILE_BASESTORE_STRICT=false, project_root=cwd", msg)
            project_root = Path.cwd()

    return {
        "project_id": project_id,
        "project_root": project_root,
        "sprint_number": state.get("sprint_number", 1),
        "adr_counter": state.get("adr_counter", 0),
    }


def node_r0(state: State) -> dict:
    """R-0 Business Analyst. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-0 stub"}]}


def node_r2(state: State) -> dict:
    """R-2 System Architect. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-2 stub"}]}


def node_r3(state: State) -> dict:
    """R-3 Scrum Master. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-3 stub"}]}


def node_r4(state: State) -> dict:
    """R-4 Dev Team. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-4 stub"}]}


def node_r5(state: State) -> dict:
    """R-5 Release Manager. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-5 stub"}]}


def node_r6(state: State) -> dict:
    """R-6 QA et DevOps. Stub."""
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": "R-6 stub"}]}
