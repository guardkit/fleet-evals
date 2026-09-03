"""Integrity tests for response_text() in harness/run_po_eval.py.

A grading run reads the model's answer through this one function. When a server hands back the
model's thinking in a field of its own instead of inside the content, this is the only place that
notices and puts it back. llama.cpp calls that field `reasoning_content`; vLLM v0.25.0 calls it
`reasoning`. Reading only the first name meant a vLLM reply arrived at the grader with its
thinking silently missing, so both names are read here and the returned provenance string says
which one was used.

The sibling file tests/test_po_spec_response_text.py holds the same tests for the spec runner;
these two runners carry the same function and must not drift apart.

Written to RUN, following tests/test_po_spec_response_text.py: this file matches the suite's
`test_*.py` collection pattern, lives in `tests/` (the directory the documented build-end
invocation `pytest tests/ tasks/` actually collects), imports nothing optional, and skips nothing.

Verify membership, not just outcome:
    python3 -m pytest tests/test_po_eval_response_text.py --collect-only -q
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "harness" / "run_po_eval.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_po_eval_rt", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _reply(**message) -> dict:
    return {"choices": [{"message": message}]}


def test_reasoning_content_is_rewrapped_and_named():
    """llama.cpp's field name: the thinking goes back inline, provenance names the field."""
    mod = _load()
    text, provenance = mod.response_text(
        _reply(content="Given a user\n", reasoning_content="weighing it up")
    )
    assert text == "<think>weighing it up</think>\nGiven a user\n"
    assert provenance == "rewrapped_reasoning_content"


def test_reasoning_is_rewrapped_and_named():
    """vLLM v0.25.0's field name: same re-wrap, and the provenance says it came from `reasoning`."""
    mod = _load()
    text, provenance = mod.response_text(
        _reply(content="Given a user\n", reasoning="weighing it up")
    )
    assert text == "<think>weighing it up</think>\nGiven a user\n"
    assert provenance == "rewrapped_reasoning"


def test_both_empty_returns_content_verbatim():
    """The ordinary case - nothing separated out - must be byte-identical to the content."""
    mod = _load()
    body = "=== FILE: plan.md ===\n# Plan\n"
    for message in (
        {"content": body},
        {"content": body, "reasoning_content": "", "reasoning": ""},
        {"content": body, "reasoning_content": None, "reasoning": None},
    ):
        text, provenance = mod.response_text(_reply(**message))
        assert text == body
        assert provenance == "content_verbatim"


def test_think_already_in_content_is_left_alone():
    """The server already inlined it. Re-wrapping would nest a second block; don't."""
    mod = _load()
    body = "<think>weighing it up</think>\nGiven a user\n"
    for message in (
        {"content": body, "reasoning_content": "weighing it up"},
        {"content": body, "reasoning": "weighing it up"},
    ):
        text, provenance = mod.response_text(_reply(**message))
        assert text == body
        assert provenance == "content_verbatim"


def test_think_only_inside_a_code_fence_still_counts_as_absent():
    """A fenced `<think>` is sample text, not the model's own block, so the real one is re-wrapped."""
    mod = _load()
    fenced = "Here is the shape:\n```\n<think>example</think>\n```\n"
    text, provenance = mod.response_text(_reply(content=fenced, reasoning="the actual thinking"))
    assert text == f"<think>the actual thinking</think>\n{fenced}"
    assert provenance == "rewrapped_reasoning"


def test_reasoning_content_wins_when_a_server_sends_both():
    mod = _load()
    text, provenance = mod.response_text(
        _reply(content="body\n", reasoning_content="preferred", reasoning="fallback")
    )
    assert text == "<think>preferred</think>\nbody\n"
    assert provenance == "rewrapped_reasoning_content"
