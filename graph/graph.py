"""Graphe LangGraph Agile (spec III.5, III.8). Interrupts H1-H4 avec branches rejected."""
import os
import sqlite3
from pathlib import Path

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import State
from graph.nodes import load_context, node_r0, node_r2, node_r3, node_r4, node_r5, node_r6

ROOT = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
CHECKPOINT_PATH = ROOT / "checkpoints.sqlite"


def _route_from_load_context(state: State) -> str:
    """Router conditionnel post-load_context selon start_phase (spec III.8-A)."""
    phase = state.get("start_phase", "E1")
    if phase == "E3":
        return "r3"
    if phase == "HOTFIX":
        return "r4"
    return "r0"  # E1 par défaut


def _route_after_r0(state: State) -> str:
    """H1 : approved -> r2, rejected -> r0."""
    return "r2" if state.get("h1_approved", True) else "r0"


def _route_after_r2(state: State) -> str:
    """H2 : approved -> r3, rejected -> r2."""
    return "r3" if state.get("h2_approved", True) else "r2"


def _route_after_r3(state: State) -> str:
    """H3 : approved -> r4, rejected -> r3."""
    return "r4" if state.get("h3_approved", True) else "r3"


def _route_after_r6(state: State) -> str:
    """H4 : approved -> END. Rejected -> r4 (Self-Healing). h5_rejected -> end."""
    if state.get("h5_rejected", False):
        return "end"
    return "end" if state.get("h4_approved", True) else "r4"


def build_graph():
    builder = StateGraph(State)
    builder.add_node("load_context", load_context)
    builder.add_node("r0", node_r0)
    builder.add_node("r2", node_r2)
    builder.add_node("r3", node_r3)
    builder.add_node("r4", node_r4)
    builder.add_node("r5", node_r5)
    builder.add_node("r6", node_r6)

    builder.add_edge(START, "load_context")
    builder.add_conditional_edges(
        "load_context",
        _route_from_load_context,
        {"r0": "r0", "r3": "r3", "r4": "r4"},
    )
    builder.add_conditional_edges("r0", _route_after_r0, {"r0": "r0", "r2": "r2"})
    builder.add_conditional_edges("r2", _route_after_r2, {"r2": "r2", "r3": "r3"})
    builder.add_conditional_edges("r3", _route_after_r3, {"r3": "r3", "r4": "r4"})
    builder.add_edge("r4", "r5")
    builder.add_edge("r5", "r6")
    builder.add_conditional_edges("r6", _route_after_r6, {"r4": "r4", "end": END})

    conn = sqlite3.connect(str(CHECKPOINT_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return builder.compile(checkpointer=checkpointer)


graph = build_graph()
