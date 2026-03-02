"""Graphe LangGraph Agile (spec III.5, III.8)."""
import os
import sqlite3
from pathlib import Path

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver

from graph.state import State
from graph.nodes import load_context, node_r0, node_r2, node_r3, node_r4, node_r5, node_r6

ROOT = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
CHECKPOINT_PATH = ROOT / "checkpoints.sqlite"


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
    builder.add_edge("load_context", "r0")
    builder.add_edge("r0", "r2")
    builder.add_edge("r2", "r3")
    builder.add_edge("r3", "r4")
    builder.add_edge("r4", "r5")
    builder.add_edge("r5", "r6")
    builder.add_edge("r6", END)

    conn = sqlite3.connect(str(CHECKPOINT_PATH), check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return builder.compile(checkpointer=checkpointer)


graph = build_graph()
