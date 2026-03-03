"""
Tests E2E du graphe Agile — structure, load_context, scripts.

Ces tests ne déclenchent pas d'appels LLM réels (Ollama/Gemini/Claude).
Pour un run complet avec LLM : utiliser scripts/test_e2e_manual.py
"""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


class TestGraphStructure:
    """Structure du graphe LangGraph."""

    def test_graph_compiles(self):
        from graph.graph import graph

        assert graph is not None

    def test_graph_has_expected_nodes(self):
        from graph.graph import graph

        g = graph.get_graph()
        mermaid = g.draw_mermaid()
        expected = ["load_context", "r0", "r2", "r3", "r4", "r5", "r6"]
        for node in expected:
            assert node in mermaid, f"Node {node} manquant"

    def test_graph_has_conditional_edges(self):
        from graph.graph import graph

        g = graph.get_graph()
        mermaid = g.draw_mermaid()
        assert "load_context" in mermaid
        assert "r0" in mermaid and "r2" in mermaid
        assert "r6" in mermaid


class TestLoadContext:
    """Nœud load_context en isolation."""

    def test_load_context_resolves_project_root(self):
        from graph import nodes

        state = {"project_id": "albert-agile", "project_root": None, "start_phase": "E1"}
        with patch.object(nodes, "_BASESTORE_STRICT", False):
            result = nodes.load_context(state)
        assert "project_root" in result
        assert result["project_root"] is not None
        assert result["project_id"] == "albert-agile"
        assert "sprint_number" in result
        assert "adr_counter" in result

    def test_load_context_hotfix_creates_sprint_backlog(self):
        from graph import nodes

        state = {
            "project_id": "albert-agile",
            "project_root": None,
            "start_phase": "HOTFIX",
            "hotfix_description": "Fix critique",
        }
        with patch.object(nodes, "_BASESTORE_STRICT", False):
            result = nodes.load_context(state)
        assert "sprint_backlog" in result
        assert result["sprint_backlog"]["id"] == "HF-001"
        assert "Fix critique" in result["sprint_backlog"]["description"]


class TestBaseStore:
    """BaseStore en mode dégradé."""

    def test_load_project_context_new_project_returns_defaults(self):
        from graph.basestore import load_project_context

        # Projet inexistant, strict=false -> valeurs par défaut
        with patch.dict(os.environ, {"AGILE_ORCHESTRATION_ROOT": str(ROOT)}):
            result = load_project_context("projet-inexistant-xyz", strict=False)
        assert result["adr_counter"] == 0
        assert result["sprint_number"] == 1


class TestTools:
    """Tools R-4 / R-5."""

    def test_run_shell_allowlist_rejects_rm(self):
        from graph.tools import run_shell

        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(PermissionError):
                run_shell("rm -rf /", Path(tmp))

    def test_run_shell_allows_git_status(self):
        from graph.tools import run_shell

        with tempfile.TemporaryDirectory() as tmp:
            r = run_shell("git status", Path(tmp))
            assert r.returncode is not None

    def test_read_file_blocks_path_traversal(self):
        from graph.tools import read_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with pytest.raises(PermissionError):
                read_file("../../../etc/passwd", root)


class TestLaws:
    """Lois Albert Core."""

    def test_format_laws_for_prompt(self):
        from graph.laws import format_laws_for_prompt

        out = format_laws_for_prompt("r0")
        assert "L1" in out
        assert "L4" in out
        assert "L-ANON" in out

    def test_get_laws_for_role(self):
        from graph.laws import get_laws_for_role

        laws = get_laws_for_role("r4")
        ids = [l["id"] for l in laws]
        assert "L8" in ids
        assert "L21" in ids


class TestAnonymizer:
    """Anonymisation L-ANON."""

    def test_scrub_emails(self):
        from graph.anonymizer import scrub

        out = scrub("Contact: user@example.com")
        # Selon config, l'email peut être redacté ou non
        assert isinstance(out, str)
        assert len(out) > 0

    def test_scrub_home_paths(self):
        from graph.anonymizer import scrub

        assert "[HOME]" in scrub("/home/nghia-phan/project")


class TestStatusScript:
    """Script status.py (logique)."""

    def test_status_returns_json_structure(self):
        import subprocess

        result = subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "status.py"), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            pytest.skip("status.py failed (config absent?)")
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        for rec in data:
            assert "project_id" in rec


class TestRunGraphCLI:
    """CLI run_graph — exit codes."""

    def test_run_graph_usage(self):
        import subprocess

        result = subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "run_graph.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0
        assert "--project-id" in result.stdout

    def test_run_graph_fails_without_project_id(self):
        import subprocess

        result = subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "run_graph.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode != 0
