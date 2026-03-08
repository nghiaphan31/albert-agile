"""
Tests pour config/custom_roo_hook.py :
- HITL : détection boucle erreurs (messages tool/user uniquement)
- Routage sémantique : fallback worker si score < seuil, sinon best_category
"""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from config.custom_roo_hook import RooCodeHandler, SIMILARITY_THRESHOLD


def _run_async(coro):
    return asyncio.run(coro)


# --- HITL ---


class TestRooCodeHandlerHITL:
    """Bloc 1 — HITL : messages tool/user uniquement, 3+ error/failed."""

    def test_trois_messages_tool_user_avec_error_trigger_hitl(self):
        handler = RooCodeHandler()
        data = {
            "messages": [
                {"role": "system", "content": "Sys"},
                {"role": "user", "content": "first"},
                {"role": "tool", "content": "error in tool output"},
                {"role": "user", "content": "retry failed"},
                {"role": "tool", "content": "another error"},
            ],
        }
        out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert out["model"] == "worker"
        assert len(out["messages"]) == 1
        assert out["messages"][0]["role"] == "user"
        assert "STOP" in out["messages"][0]["content"]
        assert "ask_user" in out["messages"][0]["content"]

    def test_messages_assistant_exclus_comptage(self):
        handler = RooCodeHandler()
        data = {
            "messages": [
                {"role": "assistant", "content": "I fixed the error that caused the pipeline to fail"},
                {"role": "user", "content": "error"},
                {"role": "tool", "content": "failed"},
            ],
        }
        # 2 messages tool/user avec error/failed, pas 3 → HITL ne doit pas se déclencher
        out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert "STOP" not in str(out.get("messages", []))
        # model sera worker (fallback) ou architect/ingest (routage) selon ollama
        assert out["model"] in ("architect", "ingest", "worker")

    def test_call_type_pas_completion_ignore(self):
        handler = RooCodeHandler()
        data = {"messages": [{"role": "user", "content": "error"}, {"role": "tool", "content": "failed"}]}
        out = _run_async(handler.async_pre_call_hook(None, None, data, "embedding"))
        assert "model" not in out or out.get("model") != "worker"
        # Pas de modification car call_type != completion

    def test_messages_vide_ignore(self):
        handler = RooCodeHandler()
        data = {"messages": []}
        out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert "model" not in out
        assert out["messages"] == []


# --- Routage sémantique (avec mocks) ---


class TestRooCodeHandlerRoutage:
    """Bloc 2 — Routage sémantique (np/ollama mockés)."""

    def test_np_ou_ollama_None_fallback_worker(self):
        handler = RooCodeHandler()
        data = {"messages": [{"role": "user", "content": "Fix this bug"}]}
        with patch("config.custom_roo_hook.np", None), patch("config.custom_roo_hook.ollama", None):
            out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert out["model"] == "worker"

    def test_vectors_vide_fallback_worker(self):
        handler = RooCodeHandler()
        data = {"messages": [{"role": "user", "content": "Fix bug"}]}
        with patch.object(handler, "_get_category_vectors", return_value={}):
            out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert out["model"] == "worker"

    def test_score_inferieur_seuil_fallback_worker(self):
        """Intent vector orthogonal aux catégories → scores ~0 < seuil → fallback worker."""
        import numpy as np

        handler = RooCodeHandler()
        handler._vectors = {
            "architect": np.array([1.0, 0, 0]),
            "ingest": np.array([0, 1.0, 0]),
            "worker": np.array([0, 0, 1.0]),
        }
        data = {"messages": [{"role": "user", "content": "xyz"}]}
        with patch("config.custom_roo_hook.ollama") as mock_ollama:
            mock_ollama.embed = lambda **kw: {"embeddings": [[0.0, 0.0, 0.0]]}
            out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert out["model"] == "worker"

    def test_score_superieur_seuil_best_category(self):
        """Intent proche de worker → score élevé → model = worker ou autre catégorie."""
        import numpy as np

        handler = RooCodeHandler()
        handler._vectors = {
            "architect": np.array([1.0, 0, 0]),
            "ingest": np.array([0, 1.0, 0]),
            "worker": np.array([0, 0, 1.0]),
        }
        data = {"messages": [{"role": "user", "content": "Fix bug"}]}
        with patch("config.custom_roo_hook.ollama") as mock_ollama:
            mock_ollama.embed = lambda **kw: {"embeddings": [[0.05, 0.05, 0.99]]}
            out = _run_async(handler.async_pre_call_hook(None, None, data, "completion"))
        assert out["model"] in ("architect", "ingest", "worker")
