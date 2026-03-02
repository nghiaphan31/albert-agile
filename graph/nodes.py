"""Noeuds du graphe Agile (R-0 a R-6). Implementation minimale."""
from graph.state import State


def load_context(state: State) -> dict:
    """Charge le contexte depuis BaseStore (spec III.8-A). Stub."""
    project_id = state.get("project_id", "")
    return {
        "project_id": project_id,
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
