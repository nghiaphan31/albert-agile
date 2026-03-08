"""
Tests pour graph/cascade.py — Phase 3 (skip Ollama warmup en mode proxy).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def _mock_llm():
    """LLM factice qui retourne une valeur sans appel réseau."""
    llm = MagicMock()
    llm.model = "tier1-n0"
    llm.base_url = "http://localhost:4000/v1"
    llm.invoke.return_value = SimpleNamespace(content="ok")
    llm.with_structured_output.return_value.invoke.return_value = {"title": "Test", "description": "x"}
    return llm


class TestCascadeSkipWarmup:
    """En mode proxy, pas d'appel Ollama warmup (/api/generate)."""

    def test_proxy_mode_skips_ollama_warmup(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value.read.return_value = b'{"models":[]}'
            with patch.dict("os.environ", {"AGILE_USE_LITELLM_PROXY": "true"}, clear=False):
                from graph.cascade import call_with_cascade
                llm = _mock_llm()
                result = call_with_cascade(llm, None, None, "test", schema=None)
        calls = mock_urlopen.call_args_list
        generate_urls = [str(c) for c in calls if len(c[0]) > 0 and "generate" in str(c[0][0])]
        assert len(generate_urls) == 0

    def test_direct_mode_completes(self):
        with patch("urllib.request.urlopen") as mock_urlopen:
            read_mock = MagicMock()
            read_mock.read.return_value = b'{"models":["qwen2.5:14b"]}'
            mock_urlopen.return_value.__enter__.return_value = read_mock
            mock_urlopen.return_value.__exit__.return_value = None
            with patch.dict("os.environ", {"AGILE_USE_LITELLM_PROXY": ""}, clear=False):
                from graph.cascade import call_with_cascade
                llm = _mock_llm()
                llm.model = "qwen2.5:14b"
                result = call_with_cascade(llm, None, None, "test", schema=None)
        assert result is not None
