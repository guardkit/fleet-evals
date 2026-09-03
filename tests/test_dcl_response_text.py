"""Integrity tests for response_text() in harness/run_dcl_heldout.py.

A grading run reads the model's answer through this one function. When a server hands back the
model's thinking in a field of its own instead of inside the content, this is the only place that
notices and puts it back. llama.cpp calls that field `reasoning_content`; vLLM v0.25.0 calls it
`reasoning`. Reading only the first name — or, as this runner did until 2026-09-03, only
`content` — meant a vLLM reply reached the grader with its thinking silently missing, and the rep
record said nothing about it. Both names are read here and the returned provenance string says
which one was used, exactly as the PO runners already do (commits 85cb025 and 783b00d).

Four field cases, and the two that must stay byte-identical to the old behaviour: both fields
empty, and a `<think>` block the server already inlined (a fenced `<think>` is sample text, not
the model's own block, so it does not count as already inlined).

Written to RUN, following tests/test_po_spec_response_text.py: `test_*.py` in `tests/`, the
directory the documented invocation `pytest tests/ tasks/` collects; imports nothing optional,
skips nothing.

Verify membership, not just outcome:
    python3 -m pytest tests/test_dcl_response_text.py --collect-only -q
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "harness" / "run_dcl_heldout.py"

BODY = 'machine Kiln {\n  state idle;\n}\n'


def _load():
    spec = importlib.util.spec_from_file_location("run_dcl_heldout_rt", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _reply(**message) -> dict:
    return {"choices": [{"message": message}]}


def test_reasoning_content_is_rewrapped_and_named():
    """llama.cpp's field name: the thinking goes back inline, provenance names the field."""
    mod = _load()
    text, provenance = mod.response_text(_reply(content=BODY, reasoning_content="weighing it up"))
    assert text == f"<think>weighing it up</think>\n{BODY}"
    assert provenance == "rewrapped_reasoning_content"


def test_reasoning_is_rewrapped_and_named():
    """vLLM v0.25.0's field name: same re-wrap, and the provenance says it came from `reasoning`."""
    mod = _load()
    text, provenance = mod.response_text(_reply(content=BODY, reasoning="weighing it up"))
    assert text == f"<think>weighing it up</think>\n{BODY}"
    assert provenance == "rewrapped_reasoning"


def test_both_empty_returns_content_verbatim():
    """The ordinary case — nothing separated out — must be byte-identical to the content."""
    mod = _load()
    for message in (
        {"content": BODY},
        {"content": BODY, "reasoning_content": "", "reasoning": ""},
        {"content": BODY, "reasoning_content": None, "reasoning": None},
    ):
        text, provenance = mod.response_text(_reply(**message))
        assert text == BODY
        assert provenance == "content_verbatim"


def test_think_already_in_content_is_left_alone():
    """The server already inlined it. Re-wrapping would nest a second block; don't."""
    mod = _load()
    inlined = f"<think>weighing it up</think>\n{BODY}"
    for message in (
        {"content": inlined, "reasoning_content": "weighing it up"},
        {"content": inlined, "reasoning": "weighing it up"},
    ):
        text, provenance = mod.response_text(_reply(**message))
        assert text == inlined
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
        _reply(content=BODY, reasoning_content="preferred", reasoning="fallback"))
    assert text == f"<think>preferred</think>\n{BODY}"
    assert provenance == "rewrapped_reasoning_content"


def test_a_malformed_reply_reads_as_empty_exactly_as_before():
    """The old `_content_of` never raised on a broken reply; neither may this."""
    mod = _load()
    for raw in ({}, {"choices": []}, {"choices": [{}]}, {"choices": [{"message": {"content": None}}]}):
        assert mod.response_text(raw) == ("", "content_verbatim")
