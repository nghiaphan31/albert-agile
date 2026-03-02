"""Etat TypedDict du graphe Agile (spec III.5bis)."""
from typing import TypedDict
from pathlib import Path


class State(TypedDict, total=False):
    project_root: Path
    project_id: str
    sprint_number: int
    adr_counter: int
    needs_architecture_review: bool
    dod: dict | None
    backlog: dict | None
    architecture: dict | None
    sprint_backlog: dict | None
    messages: list
    start_phase: str
    h1_feedback: str
    hotfix_description: str
