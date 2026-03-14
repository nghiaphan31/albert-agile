#!/usr/bin/env python3
"""
Test rigoureux qwen3:14b + tool calling — 3 couches × 4 scénarios.

Diagnostique les causes des boucles observées dans Roo :
  H1 : _fix_tool_calls absent du chemin stream=true+fake_stream
  H2 : tokens <think> contaminant content ou tool_call arguments
  H3 : finish_reason incorrect dans les chunks fake_stream

Prérequis :
  - Ollama lancé avec qwen3:14b : `ollama pull qwen3:14b && ollama serve`
  - LiteLLM proxy lancé : `./scripts/run_litellm_proxy.sh`

Usage :
  python scripts/test_qwen3_tool_calling.py
  python scripts/test_qwen3_tool_calling.py --layer 0          # Ollama direct seulement
  python scripts/test_qwen3_tool_calling.py --layer 1          # Proxy non-streaming
  python scripts/test_qwen3_tool_calling.py --layer 2          # Proxy fake_stream
  python scripts/test_qwen3_tool_calling.py --scenario 1       # Scénario S1 seulement
  python scripts/test_qwen3_tool_calling.py --repeat 10        # 10 répétitions par test
  python scripts/test_qwen3_tool_calling.py --model worker-local-qwen3:14b
  python scripts/test_qwen3_tool_calling.py --verbose          # Affiche les réponses brutes
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

CFG: dict = {
    "ollama_url": "http://localhost:11434/v1/chat/completions",
    "proxy_url": "http://localhost:4000/v1/chat/completions",
    "ollama_model": "qwen3:14b",
    "proxy_model": "worker-local-qwen3:14b",
}

THINK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
THINK_OPEN_PATTERN = re.compile(r"<think>", re.IGNORECASE)

ROO_SYSTEM_PROMPT = (
    "You are a coding assistant. You MUST always respond by calling one of the provided tools. "
    "Never reply in plain text only. Always use a tool call."
)

# ---------------------------------------------------------------------------
# Tool schemas (subset Roo réaliste)
# ---------------------------------------------------------------------------

TOOL_ATTEMPT_COMPLETION = {
    "type": "function",
    "function": {
        "name": "attempt_completion",
        "description": "Use this when the task is complete. Present the result to the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                    "description": "The final result of the task.",
                },
                "command": {
                    "type": "string",
                    "description": "Optional CLI command to demonstrate the result.",
                },
            },
            "required": ["result"],
        },
    },
}

TOOL_ASK_FOLLOWUP = {
    "type": "function",
    "function": {
        "name": "ask_followup_question",
        "description": "Ask the user a clarifying question when the task is ambiguous.",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to ask."},
                "follow_up": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "2-4 suggested answers (array of strings).",
                },
            },
            "required": ["question", "follow_up"],
        },
    },
}

TOOL_READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["path"],
        },
    },
}

TOOL_WRITE_FILE = {
    "type": "function",
    "function": {
        "name": "write_to_file",
        "description": "Write content to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
}

TOOL_EXECUTE_COMMAND = {
    "type": "function",
    "function": {
        "name": "execute_command",
        "description": "Execute a CLI command.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "requires_approval": {"type": "boolean"},
            },
            "required": ["command"],
        },
    },
}

# ---------------------------------------------------------------------------
# Scénarios
# ---------------------------------------------------------------------------

SCENARIOS = {
    1: {
        "name": "S1 - Tâche simple (→ attempt_completion)",
        "messages": [
            {"role": "system", "content": ROO_SYSTEM_PROMPT},
            {"role": "user", "content": "Write a Python function that reverses a list. Reply using a tool call."},
        ],
        "tools": [TOOL_ATTEMPT_COMPLETION, TOOL_ASK_FOLLOWUP],
        "tool_choice": "required",
        "expect_tool": "attempt_completion",
    },
    2: {
        "name": "S2 - Ambiguïté (→ ask_followup_question + follow_up array)",
        "messages": [
            {"role": "system", "content": ROO_SYSTEM_PROMPT},
            {"role": "user", "content": "Improve the performance. Reply using a tool call."},
        ],
        "tools": [TOOL_ATTEMPT_COMPLETION, TOOL_ASK_FOLLOWUP],
        "tool_choice": "required",
        "expect_tool": "ask_followup_question",
    },
    3: {
        "name": "S3 - Stress test think tokens",
        "messages": [
            {"role": "system", "content": ROO_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Answer briefly. Do NOT include any XML tags in your response. "
                    "Write a one-line Python hello world. Use a tool call."
                ),
            },
        ],
        "tools": [TOOL_ATTEMPT_COMPLETION, TOOL_ASK_FOLLOWUP],
        "tool_choice": "required",
        "expect_tool": "attempt_completion",
    },
    4: {
        "name": "S4 - Suite complète tools Roo",
        "messages": [
            {"role": "system", "content": ROO_SYSTEM_PROMPT},
            {"role": "user", "content": "Read the file utils.py, then fix the bug in line 42. Use a tool call."},
        ],
        "tools": [TOOL_ATTEMPT_COMPLETION, TOOL_ASK_FOLLOWUP, TOOL_READ_FILE, TOOL_WRITE_FILE, TOOL_EXECUTE_COMMAND],
        "tool_choice": "required",
        "expect_tool": None,  # Any tool acceptable
    },
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class TestResult:
    layer: str
    scenario_id: int
    scenario_name: str
    repeat_index: int
    checks: list[CheckResult] = field(default_factory=list)
    raw_response: dict = field(default_factory=dict)
    error: str = ""
    duration_ms: float = 0.0

    @property
    def passed(self) -> bool:
        return not self.error and all(c.passed for c in self.checks)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def _post_json(url: str, body: dict, timeout: int = 90) -> dict:
    """POST JSON, retourne le dict décodé. Lève urllib.error.URLError si erreur."""
    data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk-1234"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _post_streaming(url: str, body: dict, timeout: int = 120) -> list[dict]:
    """POST SSE streaming, retourne la liste des chunks (dicts). Reconstruit aussi la réponse agrégée."""
    body = {**body, "stream": True}
    data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk-1234"},
    )
    chunks = []
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunks.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
    return chunks


def _aggregate_stream_chunks(chunks: list[dict]) -> dict:
    """
    Reconstruit une réponse OpenAI-like depuis les chunks SSE.
    Agrège content, tool_calls et conserve le dernier finish_reason.
    """
    content_parts: list[str] = []
    tool_calls_map: dict[int, dict] = {}
    finish_reason = None
    model = None

    for chunk in chunks:
        model = model or chunk.get("model")
        choices = chunk.get("choices", [])
        if not choices:
            continue
        choice = choices[0]
        finish_reason = choice.get("finish_reason") or finish_reason
        delta = choice.get("delta", {})

        if delta.get("content"):
            content_parts.append(delta["content"])

        for tc in delta.get("tool_calls", []):
            idx = tc.get("index", 0)
            if idx not in tool_calls_map:
                tool_calls_map[idx] = {"id": tc.get("id", ""), "type": "function", "function": {"name": "", "arguments": ""}}
            fn = tc.get("function", {})
            if fn.get("name"):
                tool_calls_map[idx]["function"]["name"] = fn["name"]
            if fn.get("arguments"):
                tool_calls_map[idx]["function"]["arguments"] += fn["arguments"]

    return {
        "model": model,
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {
                    "content": "".join(content_parts) or None,
                    "tool_calls": list(tool_calls_map.values()) if tool_calls_map else [],
                },
            }
        ],
        "_chunks_count": len(chunks),
    }


# ---------------------------------------------------------------------------
# Diagnostic checks (H1, H2, H3)
# ---------------------------------------------------------------------------


def _check_think_tokens(response: dict) -> CheckResult:
    """H2 : Vérifier l'absence de tokens <think> dans content et tool_call arguments."""
    choices = response.get("choices", [])
    if not choices:
        return CheckResult("think_tokens_absent", True, "no choices")

    msg = choices[0].get("message", {})
    content = msg.get("content") or ""
    tool_calls = msg.get("tool_calls") or []

    found_in = []
    if THINK_OPEN_PATTERN.search(content):
        snippet = content[:120].replace("\n", "↵")
        found_in.append(f"content: «{snippet}…»")

    for tc in tool_calls:
        args = (tc.get("function") or {}).get("arguments", "")
        if THINK_OPEN_PATTERN.search(args or ""):
            found_in.append(f"tool_call[{tc.get('function', {}).get('name')}].arguments")

    if found_in:
        return CheckResult("think_tokens_absent", False, "FOUND IN: " + ", ".join(found_in))
    return CheckResult("think_tokens_absent", True)


def _check_tool_calls_json(response: dict) -> CheckResult:
    """C2 : Vérifier que les tool_calls ont des arguments JSON valides."""
    choices = response.get("choices", [])
    if not choices:
        return CheckResult("tool_calls_json_valid", True, "no choices (no tool calls to check)")

    msg = choices[0].get("message", {})
    tool_calls = msg.get("tool_calls") or []

    if not tool_calls:
        content = msg.get("content") or ""
        if content:
            return CheckResult("tool_calls_json_valid", False, f"no tool_calls but content present: «{content[:80]}»")
        return CheckResult("tool_calls_json_valid", False, "no tool_calls and no content")

    errors = []
    for tc in tool_calls:
        fn = tc.get("function") or {}
        name = fn.get("name", "<unnamed>")
        args_str = fn.get("arguments", "")
        try:
            json.loads(args_str)
        except (json.JSONDecodeError, TypeError) as e:
            errors.append(f"{name}: {e} — got «{str(args_str)[:80]}»")

    if errors:
        return CheckResult("tool_calls_json_valid", False, " | ".join(errors))
    return CheckResult("tool_calls_json_valid", True, f"{len(tool_calls)} tool call(s) valid")


def _check_follow_up_array(response: dict) -> CheckResult:
    """C3 : Vérifier que ask_followup_question.follow_up est un array de strings len>=2."""
    choices = response.get("choices", [])
    if not choices:
        return CheckResult("follow_up_array", True, "skipped (no choices)")

    msg = choices[0].get("message", {})
    tool_calls = msg.get("tool_calls") or []

    followup_calls = [tc for tc in tool_calls if (tc.get("function") or {}).get("name") == "ask_followup_question"]
    if not followup_calls:
        return CheckResult("follow_up_array", True, "skipped (no ask_followup_question call)")

    errors = []
    for tc in followup_calls:
        args_str = (tc.get("function") or {}).get("arguments", "{}")
        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            errors.append(f"arguments not parseable: «{args_str[:80]}»")
            continue
        fu = args.get("follow_up")
        if not isinstance(fu, list):
            errors.append(f"follow_up is {type(fu).__name__} not list: «{str(fu)[:80]}»")
        elif len(fu) < 2:
            errors.append(f"follow_up has only {len(fu)} item(s): {fu}")
        else:
            non_str = [x for x in fu if not isinstance(x, str)]
            if non_str:
                errors.append(f"follow_up items not all strings: {non_str[:3]}")

    if errors:
        return CheckResult("follow_up_array", False, " | ".join(errors))
    return CheckResult("follow_up_array", True, f"follow_up valid ({len(followup_calls[0] and json.loads((followup_calls[0].get('function') or {}).get('arguments', '{}') or '{}').get('follow_up', []))} items)")


def _check_finish_reason(response: dict, is_streaming: bool = False) -> CheckResult:
    """H3 / C4 : Vérifier que finish_reason est 'tool_calls' ou 'stop' (pas None)."""
    choices = response.get("choices", [])
    if not choices:
        return CheckResult("finish_reason_valid", False, "no choices")

    fr = choices[0].get("finish_reason")
    if fr in ("tool_calls", "stop", "length"):
        return CheckResult("finish_reason_valid", True, f"finish_reason={fr!r}")
    return CheckResult("finish_reason_valid", False, f"unexpected finish_reason={fr!r}")


def _check_signature(response: dict, is_streaming: bool = False) -> CheckResult:
    """
    C5 : Vérifier que la signature de routage est présente (proxy uniquement).

    Comportement connu :
    - Non-streaming + tool_calls : _append_model_signature ne peut pas injecter dans
      content=None. La signature est absente → bug cosmétique connu, pas une cause de boucle.
    - Streaming (fake_stream) : la signature est injectée dans le dernier chunk delta.content,
      visible dans l'agrégat si content_len > 0.
    """
    choices = response.get("choices", [])
    if not choices:
        return CheckResult("signature_present", False, "no choices")

    msg = choices[0].get("message", {})
    content = msg.get("content") or ""
    tool_calls = msg.get("tool_calls") or []

    sig_marker = "Chemin de routage"
    if sig_marker in content:
        return CheckResult("signature_present", True, "found in content")

    # Non-streaming + tool_calls : content=None → signature non injectable.
    # Ce n'est pas une cause de boucle, on marque WARN (pass avec note).
    if not is_streaming and tool_calls:
        return CheckResult(
            "signature_present",
            True,
            "WARN: non-streaming+tool_calls → content=None, signature not injectable (known limitation, not a loop cause)",
        )

    return CheckResult("signature_present", False, f"not found. content snippet: «{content[:120]}»")


def _check_expected_tool(response: dict, expect_tool: str | None) -> CheckResult:
    """Vérifier que le tool attendu est bien appelé."""
    if expect_tool is None:
        return CheckResult("expected_tool_called", True, "no expectation")

    choices = response.get("choices", [])
    if not choices:
        return CheckResult("expected_tool_called", False, "no choices")

    msg = choices[0].get("message", {})
    tool_calls = msg.get("tool_calls") or []
    names = [(tc.get("function") or {}).get("name") for tc in tool_calls]

    if expect_tool in names:
        return CheckResult("expected_tool_called", True, f"found {expect_tool!r}")
    return CheckResult("expected_tool_called", False, f"expected {expect_tool!r}, got {names}")


# ---------------------------------------------------------------------------
# Test runners per layer
# ---------------------------------------------------------------------------


def _run_checks(response: dict, expect_tool: str | None, is_proxy: bool, is_streaming: bool) -> list[CheckResult]:
    checks = [
        _check_think_tokens(response),
        _check_tool_calls_json(response),
        _check_follow_up_array(response),
        _check_finish_reason(response, is_streaming),
        _check_expected_tool(response, expect_tool),
    ]
    if is_proxy:
        checks.append(_check_signature(response, is_streaming))
    return checks


def run_layer0(scenario_id: int, scenario: dict, repeat: int, verbose: bool) -> list[TestResult]:
    """L0 : Ollama direct, non-streaming (baseline)."""
    results = []
    for i in range(repeat):
        body = {
            "model": CFG["ollama_model"],
            "messages": scenario["messages"],
            "tools": scenario["tools"],
            "tool_choice": scenario.get("tool_choice", "auto"),
            "stream": False,
        }
        t0 = time.monotonic()
        error = ""
        response: dict = {}
        try:
            response = _post_json(CFG["ollama_url"], body)
        except Exception as e:
            error = str(e)
        duration_ms = (time.monotonic() - t0) * 1000

        result = TestResult(
            layer="L0-Ollama-direct",
            scenario_id=scenario_id,
            scenario_name=scenario["name"],
            repeat_index=i + 1,
            raw_response=response,
            error=error,
            duration_ms=duration_ms,
        )
        if not error:
            result.checks = _run_checks(response, scenario.get("expect_tool"), is_proxy=False, is_streaming=False)
        results.append(result)
        if verbose:
            _print_raw(response, f"L0 S{scenario_id} #{i+1}")
    return results


def run_layer1(scenario_id: int, scenario: dict, repeat: int, verbose: bool) -> list[TestResult]:
    """L1 : Proxy LiteLLM, non-streaming (success_hook path — _fix_tool_calls doit s'exécuter)."""
    results = []
    for i in range(repeat):
        body = {
            "model": CFG["proxy_model"],
            "messages": scenario["messages"],
            "tools": scenario["tools"],
            "tool_choice": scenario.get("tool_choice", "auto"),
            "stream": False,
        }
        t0 = time.monotonic()
        error = ""
        response: dict = {}
        try:
            response = _post_json(CFG["proxy_url"], body)
        except Exception as e:
            error = str(e)
        duration_ms = (time.monotonic() - t0) * 1000

        result = TestResult(
            layer="L1-Proxy-NonStream",
            scenario_id=scenario_id,
            scenario_name=scenario["name"],
            repeat_index=i + 1,
            raw_response=response,
            error=error,
            duration_ms=duration_ms,
        )
        if not error:
            result.checks = _run_checks(response, scenario.get("expect_tool"), is_proxy=True, is_streaming=False)
        results.append(result)
        if verbose:
            _print_raw(response, f"L1 S{scenario_id} #{i+1}")
    return results


def run_layer2(scenario_id: int, scenario: dict, repeat: int, verbose: bool) -> list[TestResult]:
    """L2 : Proxy LiteLLM, streaming=True (fake_stream path — H1: _fix_tool_calls absent?)."""
    results = []
    for i in range(repeat):
        body = {
            "model": CFG["proxy_model"],
            "messages": scenario["messages"],
            "tools": scenario["tools"],
            "tool_choice": scenario.get("tool_choice", "auto"),
        }
        t0 = time.monotonic()
        error = ""
        chunks: list[dict] = []
        response: dict = {}
        try:
            chunks = _post_streaming(CFG["proxy_url"], body)
            response = _aggregate_stream_chunks(chunks)
        except Exception as e:
            error = str(e)
        duration_ms = (time.monotonic() - t0) * 1000

        # Diagnostic H3 : chercher les finish_reason dans les chunks bruts
        h3_detail = _diagnose_h3(chunks)

        result = TestResult(
            layer="L2-Proxy-FakeStream",
            scenario_id=scenario_id,
            scenario_name=scenario["name"],
            repeat_index=i + 1,
            raw_response={**response, "_chunks_h3": h3_detail},
            error=error,
            duration_ms=duration_ms,
        )
        if not error:
            result.checks = _run_checks(response, scenario.get("expect_tool"), is_proxy=True, is_streaming=True)
            # Ajouter le diagnostic H3 comme check supplémentaire
            result.checks.append(CheckResult("h3_finish_reason_in_chunks", h3_detail["found"], h3_detail["detail"]))
        results.append(result)
        if verbose:
            _print_raw({"aggregated": response, "chunks_count": len(chunks), "h3": h3_detail}, f"L2 S{scenario_id} #{i+1}")
    return results


def _diagnose_h3(chunks: list[dict]) -> dict:
    """
    H3 : Analyser les chunks pour vérifier que finish_reason apparaît bien
    et sur quel chunk il tombe (last chunk avec content vs chunk vide tool_calls).
    """
    finish_reasons_per_chunk = []
    for idx, chunk in enumerate(chunks):
        choices = chunk.get("choices", [])
        if choices:
            fr = choices[0].get("finish_reason")
            delta = choices[0].get("delta", {})
            content = delta.get("content", "")
            tc_present = bool(delta.get("tool_calls"))
            if fr:
                finish_reasons_per_chunk.append({
                    "chunk_idx": idx,
                    "finish_reason": fr,
                    "delta_content_len": len(content or ""),
                    "delta_has_tool_calls": tc_present,
                    "is_last": idx == len(chunks) - 1,
                })

    if not finish_reasons_per_chunk:
        return {"found": False, "detail": f"No finish_reason found in {len(chunks)} chunks"}

    last = finish_reasons_per_chunk[-1]
    detail = f"{len(finish_reasons_per_chunk)} finish_reason(s) found. Last: chunk#{last['chunk_idx']} fr={last['finish_reason']!r} content_len={last['delta_content_len']} tool_calls={last['delta_has_tool_calls']}"
    return {"found": True, "detail": detail, "all": finish_reasons_per_chunk}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

PASS_MARK = "✓"
FAIL_MARK = "✗"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _print_raw(data: Any, label: str) -> None:
    print(f"\n{YELLOW}--- RAW [{label}] ---{RESET}")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str)[:3000])
    print(f"{YELLOW}---{RESET}")


def _print_result(r: TestResult) -> None:
    status = f"{GREEN}{PASS_MARK} PASS{RESET}" if r.passed else f"{RED}{FAIL_MARK} FAIL{RESET}"
    header = f"{BOLD}[{r.layer}] S{r.scenario_id} #{r.repeat_index:02d}{RESET} — {r.scenario_name[:50]}"
    dur = f"({r.duration_ms:.0f}ms)"
    print(f"  {status} {header} {dur}")
    if r.error:
        print(f"    {RED}ERROR: {r.error}{RESET}")
        return
    for c in r.checks:
        mark = f"{GREEN}{PASS_MARK}{RESET}" if c.passed else f"{RED}{FAIL_MARK}{RESET}"
        detail = f"  → {c.detail}" if c.detail else ""
        print(f"    {mark} {c.name}{detail}")


def _print_summary(all_results: list[TestResult]) -> None:
    print(f"\n{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}RÉSUMÉ{RESET}")
    print(f"{'='*70}")

    # Par layer × scenario
    groups: dict[tuple, list[TestResult]] = {}
    for r in all_results:
        key = (r.layer, r.scenario_id)
        groups.setdefault(key, []).append(r)

    for (layer, sid), results in sorted(groups.items()):
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        pct = passed / total * 100
        color = GREEN if pct >= 90 else (YELLOW if pct >= 70 else RED)
        scenario_name = results[0].scenario_name
        print(f"  {color}{layer} / S{sid} — {scenario_name[:40]}: {passed}/{total} ({pct:.0f}%){RESET}")

        # Détail par check
        check_names = [c.name for c in results[0].checks] if results[0].checks else []
        for cname in check_names:
            c_passed = sum(1 for r in results for c in r.checks if c.name == cname and c.passed)
            c_total = sum(1 for r in results for c in r.checks if c.name == cname)
            c_pct = c_passed / c_total * 100 if c_total else 0
            c_color = GREEN if c_pct >= 90 else (YELLOW if c_pct >= 70 else RED)
            print(f"      {c_color}{cname}: {c_passed}/{c_total} ({c_pct:.0f}%){RESET}")

    # Hypothèses
    print(f"\n{BOLD}HYPOTHÈSES{RESET}")
    _print_hypothesis_summary(all_results)


def _print_hypothesis_summary(all_results: list[TestResult]) -> None:
    """Synthèse des hypothèses H1, H2, H3."""

    # H1 : _fix_tool_calls absent du chemin L2 (streaming)
    # Indicateur : L2 a plus d'échecs sur tool_calls_json_valid ou follow_up_array que L1
    l1 = [r for r in all_results if r.layer == "L1-Proxy-NonStream" and not r.error]
    l2 = [r for r in all_results if r.layer == "L2-Proxy-FakeStream" and not r.error]

    def check_pass_rate(results: list[TestResult], check_name: str) -> float:
        totals = [(c.passed) for r in results for c in r.checks if c.name == check_name]
        return sum(totals) / len(totals) * 100 if totals else -1

    h1_indicators = []
    for cname in ("tool_calls_json_valid", "follow_up_array"):
        l1_rate = check_pass_rate(l1, cname)
        l2_rate = check_pass_rate(l2, cname)
        if l1_rate >= 0 and l2_rate >= 0:
            diff = l1_rate - l2_rate
            h1_indicators.append((cname, l1_rate, l2_rate, diff))

    if h1_indicators:
        max_diff = max(d for _, _, _, d in h1_indicators)
        h1_status = RED + "CONFIRMÉE" if max_diff > 10 else (YELLOW + "INCERTAINE" if max_diff > 0 else GREEN + "INFIRMÉE")
        print(f"  H1 (_fix_tool_calls absent stream): {h1_status}{RESET}")
        for cname, l1r, l2r, diff in h1_indicators:
            print(f"    {cname}: L1={l1r:.0f}% vs L2={l2r:.0f}% (diff={diff:+.0f}%)")
    else:
        print(f"  H1: {YELLOW}non évaluable (données insuffisantes){RESET}")

    # H2 : think tokens
    all_non_error = [r for r in all_results if not r.error]
    h2_fails = [r for r in all_non_error for c in r.checks if c.name == "think_tokens_absent" and not c.passed]
    h2_total = sum(1 for r in all_non_error for c in r.checks if c.name == "think_tokens_absent")
    if h2_total:
        h2_rate = len(h2_fails) / h2_total * 100
        h2_status = RED + "CONFIRMÉE" if h2_rate > 5 else GREEN + "INFIRMÉE"
        print(f"  H2 (think tokens): {h2_status}{RESET} — {len(h2_fails)}/{h2_total} tests impactés ({h2_rate:.0f}%)")
    else:
        print(f"  H2: {YELLOW}non évaluable{RESET}")

    # H3 : finish_reason dans chunks
    h3_results = [r for r in l2 if not r.error]
    h3_check = "h3_finish_reason_in_chunks"
    h3_pass = sum(1 for r in h3_results for c in r.checks if c.name == h3_check and c.passed)
    h3_total = sum(1 for r in h3_results for c in r.checks if c.name == h3_check)
    if h3_total:
        h3_rate = h3_pass / h3_total * 100
        h3_status = GREEN + "INFIRMÉE" if h3_rate >= 90 else RED + "CONFIRMÉE"
        print(f"  H3 (finish_reason chunks): {h3_status}{RESET} — finish_reason trouvé dans {h3_pass}/{h3_total} ({h3_rate:.0f}%)")
    else:
        print(f"  H3: {YELLOW}non évaluable (L2 non exécuté){RESET}")

    # Recommandations
    print(f"\n{BOLD}RECOMMANDATIONS{RESET}")
    any_rec = False
    if h1_indicators and max(d for _, _, _, d in h1_indicators) > 10:
        print(f"  → {RED}H1 confirmée{RESET}: ajouter _fix_tool_calls dans async_post_call_streaming_iterator_hook")
        print(f"    (agréger les chunks, appeler _fix_tool_calls sur le message reconstruit)")
        any_rec = True
    if h2_total and len(h2_fails) / h2_total > 0.05:
        print(f"  → {RED}H2 confirmée{RESET}: filtrer les tokens <think> avant de transmettre à Roo")
        print(f"    (strip THINK_PATTERN dans async_post_call_streaming_iterator_hook et success_hook)")
        any_rec = True
    if not any_rec:
        print(f"  → {GREEN}Aucun problème critique détecté.{RESET}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test rigoureux qwen3:14b + tool calling (3 couches × 4 scénarios)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--layer", choices=["0", "1", "2", "all"], default="all", help="Couche à tester")
    parser.add_argument("--scenario", type=int, choices=[1, 2, 3, 4], default=None, help="Scénario seul (1-4)")
    parser.add_argument("--repeat", type=int, default=3, help="Répétitions par test (défaut: 3, recommandé: 10)")
    parser.add_argument("--verbose", action="store_true", help="Afficher les réponses brutes JSON")
    parser.add_argument("--ollama-model", default=CFG["ollama_model"], help=f"Modèle Ollama (défaut: {CFG['ollama_model']})")
    parser.add_argument("--proxy-model", default=CFG["proxy_model"], help=f"Modèle proxy (défaut: {CFG['proxy_model']})")
    parser.add_argument("--ollama-url", default=CFG["ollama_url"])
    parser.add_argument("--proxy-url", default=CFG["proxy_url"])
    args = parser.parse_args()

    # Appliquer les overrides dans CFG (dict mutable, pas de global)
    CFG["ollama_model"] = args.ollama_model
    CFG["proxy_model"] = args.proxy_model
    CFG["ollama_url"] = args.ollama_url
    CFG["proxy_url"] = args.proxy_url

    scenario_ids = [args.scenario] if args.scenario else list(SCENARIOS.keys())
    layers = [int(args.layer)] if args.layer != "all" else [0, 1, 2]

    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}TEST RIGOUREUX qwen3:14b + TOOL CALLING{RESET}")
    print(f"  Modèle Ollama : {CFG['ollama_model']}  |  Proxy : {CFG['proxy_model']}")
    print(f"  Couches : {layers}  |  Scénarios : {scenario_ids}  |  Répétitions : {args.repeat}")
    print(f"{'='*70}\n")

    all_results: list[TestResult] = []
    layer_fns = {0: run_layer0, 1: run_layer1, 2: run_layer2}

    for layer_id in layers:
        layer_name = {0: "L0-Ollama-direct", 1: "L1-Proxy-NonStream", 2: "L2-Proxy-FakeStream"}[layer_id]
        print(f"{BOLD}{'─'*60}{RESET}")
        print(f"{BOLD}Couche {layer_id} : {layer_name}{RESET}")
        print(f"{'─'*60}")

        # Vérification de connectivité
        url = CFG["ollama_url"] if layer_id == 0 else CFG["proxy_url"]
        check_url = url.replace("/v1/chat/completions", "/v1/models")
        try:
            with urllib.request.urlopen(urllib.request.Request(check_url, headers={"Authorization": "Bearer sk-1234"}), timeout=5):
                pass
            print(f"  {GREEN}✓ Connectivité OK ({url}){RESET}")
        except Exception as e:
            print(f"  {RED}✗ Service non joignable ({url}): {e}{RESET}")
            print(f"  {YELLOW}→ Couche {layer_id} ignorée{RESET}\n")
            continue

        for sid in scenario_ids:
            scenario = SCENARIOS[sid]
            print(f"\n  {BOLD}Scénario {sid}: {scenario['name']}{RESET}")
            results = layer_fns[layer_id](sid, scenario, args.repeat, args.verbose)
            for r in results:
                _print_result(r)
            all_results.extend(results)

    if all_results:
        _print_summary(all_results)
    else:
        print(f"\n{RED}Aucun test exécuté.{RESET}")
        sys.exit(1)

    # Exit code non-zéro si des tests ont échoué
    failed = [r for r in all_results if not r.passed]
    if failed:
        print(f"\n{RED}{len(failed)}/{len(all_results)} tests failed.{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}Tous les tests réussis ({len(all_results)}).{RESET}")


if __name__ == "__main__":
    main()
