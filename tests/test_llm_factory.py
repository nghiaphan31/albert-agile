"""
Tests pour graph/llm_factory.py — Phase 3 (LangGraph via LiteLLM).
Vérifie le mode proxy (AGILE_USE_LITELLM_PROXY) vs mode direct.
"""
from __future__ import annotations

import importlib
import sys
from unittest.mock import patch

import pytest


def _get_llm_factory_module():
    """Réimporte llm_factory pour récupérer les valeurs env actuelles."""
    import graph.llm_factory as m
    importlib.reload(m)
    return m


class TestLlmFactoryProxyMode:
    """Mode proxy : ChatOpenAI avec base_url et tier1-n0 / tier2-n0."""

    def test_proxy_tier1_returns_chatopenai(self):
        with patch.dict(
            "os.environ",
            {"AGILE_USE_LITELLM_PROXY": "true", "OPENAI_API_KEY": "dummy"},
            clear=False,
        ):
            mod = _get_llm_factory_module()
            n0, n1, n2 = mod.get_llms_tier1()
        from langchain_openai import ChatOpenAI
        assert isinstance(n0, ChatOpenAI)
        assert n0.model == "tier1-n0"
        base = getattr(n0, "openai_api_base", None) or getattr(n0, "base_url", None) or ""
        assert "localhost:4000" in str(base)
        assert n1 is None
        assert n2 is None

    def test_proxy_tier2_returns_chatopenai(self):
        with patch.dict(
            "os.environ",
            {"AGILE_USE_LITELLM_PROXY": "1", "OPENAI_API_KEY": "dummy"},
            clear=False,
        ):
            mod = _get_llm_factory_module()
            n0, n1, n2 = mod.get_llms_tier2()
        from langchain_openai import ChatOpenAI
        assert isinstance(n0, ChatOpenAI)
        assert n0.model == "tier2-n0"
        assert n1 is None
        assert n2 is None

    def test_proxy_base_url_override(self):
        with patch.dict(
            "os.environ",
            {
                "AGILE_USE_LITELLM_PROXY": "true",
                "AGILE_LITELLM_BASE_URL": "http://proxy:5000/v1",
                "OPENAI_API_KEY": "dummy",
            },
            clear=False,
        ):
            mod = _get_llm_factory_module()
            n0, _, _ = mod.get_llms_tier1()
        base = getattr(n0, "openai_api_base", None) or getattr(n0, "base_url", None) or ""
        assert "proxy:5000" in str(base)


class TestLlmFactoryDirectMode:
    """Mode direct : ChatOllama, pas de ChatOpenAI."""

    def test_direct_tier1_returns_chatollama(self):
        with patch.dict("os.environ", {"AGILE_USE_LITELLM_PROXY": ""}, clear=False):
            mod = _get_llm_factory_module()
            n0, n1, n2 = mod.get_llms_tier1()
        from langchain_ollama import ChatOllama
        assert isinstance(n0, ChatOllama)
        assert n0.model == "qwen2.5:14b"
