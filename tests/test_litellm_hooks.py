"""
Tests pour config/litellm_hooks.py :
- Post-call hook Option A (_fix_tool_calls, _repair_ask_followup_tc)
- Injection conditionnelle TOOL_SCHEMA_PROMPT (model==worker)
"""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from config.litellm_hooks import (
    DEFAULT_FOLLOW_UP,
    TOOL_SCHEMA_PROMPT,
    ToolSchemaEnforcer,
    _fix_tool_calls,
    _repair_ask_followup_tc,
)


def _make_tool_call(name: str, arguments: str):
    """Construit un objet factice tool_call avec function.name et function.arguments."""
    fn = SimpleNamespace(name=name, arguments=arguments)
    return SimpleNamespace(function=fn)


def _make_response(tool_calls: list):
    """Construit un objet factice response.choices[0].message avec tool_calls."""
    msg = SimpleNamespace(tool_calls=list(tool_calls))
    choice = SimpleNamespace(message=msg)
    return SimpleNamespace(choices=[choice])


# --- Post-call Option A : _repair_ask_followup_tc ---


class TestRepairAskFollowupTc:
    """Tests de _repair_ask_followup_tc."""

    def test_follow_up_manquant_reparation(self):
        tc = _make_tool_call("ask_followup_question", '{"question": "Continue?"}')
        assert _repair_ask_followup_tc(tc) is True
        args = json.loads(tc.function.arguments)
        assert args["follow_up"] == DEFAULT_FOLLOW_UP
        assert args["question"] == "Continue?"

    def test_follow_up_non_array_reparation(self):
        tc = _make_tool_call("ask_followup_question", '{"question": "Ok?", "follow_up": "Yes"}')
        assert _repair_ask_followup_tc(tc) is True
        args = json.loads(tc.function.arguments)
        assert args["follow_up"] == DEFAULT_FOLLOW_UP

    def test_follow_up_liste_vide_reparation(self):
        tc = _make_tool_call("ask_followup_question", '{"question": "?", "follow_up": []}')
        assert _repair_ask_followup_tc(tc) is True
        args = json.loads(tc.function.arguments)
        assert args["follow_up"] == DEFAULT_FOLLOW_UP

    def test_json_decode_error_force_structure_safe(self):
        tc = _make_tool_call("ask_followup_question", "{invalid json")
        assert _repair_ask_followup_tc(tc) is True
        args = json.loads(tc.function.arguments)
        assert "question" in args
        assert args["follow_up"] == DEFAULT_FOLLOW_UP

    def test_ask_followup_valide_inchange(self):
        valid = '{"question": "Ok?", "follow_up": ["Yes", "No"]}'
        tc = _make_tool_call("ask_followup_question", valid)
        assert _repair_ask_followup_tc(tc) is True
        assert tc.function.arguments == valid

    def test_autre_tool_non_modifie(self):
        tc = _make_tool_call("attempt_completion", '{"result": "done"}')
        assert _repair_ask_followup_tc(tc) is True
        assert tc.function.arguments == '{"result": "done"}'

    def test_function_none_retourne_false(self):
        tc = SimpleNamespace(function=None)
        assert _repair_ask_followup_tc(tc) is False


# --- Post-call Option A : _fix_tool_calls ---


class TestFixToolCalls:
    """Tests de _fix_tool_calls (Option A : suppression si irrécupérable)."""

    def test_follow_up_manquant_reparation(self):
        tc = _make_tool_call("ask_followup_question", '{"question": "?"}')
        resp = _make_response([tc])
        _fix_tool_calls(resp)
        args = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
        assert args["follow_up"] == DEFAULT_FOLLOW_UP

    def test_json_invalide_reparation(self):
        tc = _make_tool_call("ask_followup_question", "{bad")
        resp = _make_response([tc])
        _fix_tool_calls(resp)
        assert len(resp.choices[0].message.tool_calls) == 1
        args = json.loads(resp.choices[0].message.tool_calls[0].function.arguments)
        assert "question" in args and "follow_up" in args

    def test_exception_lors_reparation_supprime_tool_call(self):
        tc = _make_tool_call("ask_followup_question", '{"question": "?"}')
        with patch(
            "config.litellm_hooks._repair_ask_followup_tc",
            side_effect=RuntimeError("crash"),
        ) as mock_repair:
            resp = _make_response([tc])
            _fix_tool_calls(resp)
            mock_repair.assert_called_once()
        assert len(resp.choices[0].message.tool_calls) == 0

    def test_tous_invalides_tool_calls_vide(self):
        tc1 = _make_tool_call("ask_followup_question", '{"question": "?"}')
        with patch(
            "config.litellm_hooks._repair_ask_followup_tc",
            side_effect=RuntimeError("crash"),
        ):
            resp = _make_response([tc1])
            _fix_tool_calls(resp)
        assert resp.choices[0].message.tool_calls == []

    def test_attempt_completion_non_modifie(self):
        tc = _make_tool_call("attempt_completion", '{"result": "done"}')
        resp = _make_response([tc])
        _fix_tool_calls(resp)
        assert len(resp.choices[0].message.tool_calls) == 1
        assert tc.function.arguments == '{"result": "done"}'

    def test_melange_valide_invalide_garde_valides(self):
        tc_ok = _make_tool_call("attempt_completion", '{"result": "ok"}')
        tc_rep = _make_tool_call("ask_followup_question", '{"question": "?"}')
        resp = _make_response([tc_ok, tc_rep])
        _fix_tool_calls(resp)
        tcs = resp.choices[0].message.tool_calls
        assert len(tcs) == 2
        assert tcs[0].function.name == "attempt_completion"
        assert tcs[1].function.name == "ask_followup_question"
        assert json.loads(tcs[1].function.arguments)["follow_up"] == DEFAULT_FOLLOW_UP

    def test_response_sans_tool_calls_inchange(self):
        msg = SimpleNamespace(tool_calls=[])
        choice = SimpleNamespace(message=msg)
        resp = SimpleNamespace(choices=[choice])
        _fix_tool_calls(resp)
        assert resp.choices[0].message.tool_calls == []


# --- Injection conditionnelle : ToolSchemaEnforcer.async_pre_call_hook ---


def _run_async(coro):
    return asyncio.run(coro)


class TestToolSchemaEnforcerInjection:
    """Injection de TOOL_SCHEMA_PROMPT uniquement si model==worker."""

    def test_model_worker_injecte_prompt(self):
        enforcer = ToolSchemaEnforcer()
        data = {
            "model": "worker",
            "tools": [{"type": "function", "function": {"name": "ask_followup_question"}}],
            "messages": [{"role": "user", "content": "Fix this bug"}],
        }
        out = _run_async(enforcer.async_pre_call_hook(None, None, data, "completion"))
        assert TOOL_SCHEMA_PROMPT in out["messages"][0]["content"]
        assert "Fix this bug" in str(out["messages"][1]["content"])

    def test_model_worker_avec_system_prepend(self):
        enforcer = ToolSchemaEnforcer()
        data = {
            "model": "worker",
            "tools": [{}],
            "messages": [{"role": "system", "content": "Base system"}, {"role": "user", "content": "Fix bug"}],
        }
        out = _run_async(enforcer.async_pre_call_hook(None, None, data, "completion"))
        assert TOOL_SCHEMA_PROMPT in out["messages"][0]["content"]
        assert "Base system" in out["messages"][0]["content"]

    def test_model_architect_pas_injection(self):
        enforcer = ToolSchemaEnforcer()
        data = {
            "model": "architect",
            "tools": [{}],
            "messages": [{"role": "user", "content": "Design the architecture"}],
        }
        out = _run_async(enforcer.async_pre_call_hook(None, None, data, "completion"))
        assert out["messages"][0].get("content") == "Design the architecture"
        assert TOOL_SCHEMA_PROMPT not in str(out.get("messages", []))

    def test_model_ingest_pas_injection(self):
        enforcer = ToolSchemaEnforcer()
        data = {
            "model": "ingest",
            "tools": [{}],
            "messages": [{"role": "user", "content": "Scan the repo"}],
        }
        out = _run_async(enforcer.async_pre_call_hook(None, None, data, "completion"))
        assert TOOL_SCHEMA_PROMPT not in str(out.get("messages", []))

    def test_tools_absent_pas_injection(self):
        enforcer = ToolSchemaEnforcer()
        data = {
            "model": "worker",
            "messages": [{"role": "user", "content": "Fix"}],
        }
        out = _run_async(enforcer.async_pre_call_hook(None, None, data, "completion"))
        assert out["messages"][0]["content"] == "Fix"
        assert TOOL_SCHEMA_PROMPT not in str(out.get("messages", []))
