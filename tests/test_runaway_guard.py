"""Integrity tests for harness/runaway_guard.py — the rule that stops a repeating reply.

On 2026-09-03 an exam rep wrote the same 19 scenarios eleven times, all the way to the 16,384
token ceiling, taking 17 minutes before it could be graded and failed. This module is what
notices. Two things have to hold, and both are tested here:

  * a reply that has started repeating itself is stopped, the connection is closed, the text
    received so far is kept, and the rule that fired can be read in plain English;
  * a healthy reply is folded back into exactly the shape a non-streaming reply has, so the
    runners' own response_text() reads it unchanged — same text, same provenance string.

Written to RUN, following tests/test_po_spec_response_text.py: `test_*.py` in `tests/`, the
directory the documented invocation `pytest tests/ tasks/` collects; imports nothing optional,
skips nothing.

Verify membership, not just outcome:
    python3 -m pytest tests/test_runaway_guard.py --collect-only -q
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD = REPO_ROOT / "harness" / "runaway_guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("runaway_guard_under_test", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeStream:
    """A server's streamed reply: an iterable of `data: {...}` lines that can be closed."""

    def __init__(self, chunks: list[dict]):
        self.lines = [f"data: {json.dumps(c)}\n".encode("utf-8") for c in chunks]
        self.lines.append(b"data: [DONE]\n")
        self.closed = False
        self.lines_read = 0

    def __iter__(self):
        for line in self.lines:
            if self.closed:
                return
            self.lines_read += 1
            yield line

    def close(self):
        self.closed = True


def _delta(**fields) -> dict:
    return {"model": "fake-model", "choices": [{"delta": dict(fields)}]}


def _repeating_chunks(block: str, times: int) -> list[dict]:
    return [_delta(content=block) for _ in range(times)]


def test_a_repeated_block_fires_the_rule_and_names_it_in_plain_english():
    mod = _load()
    block = "  Scenario: a member books a free slot\n    Given a free slot\n" + "x" * 260 + "\n"
    detector = mod.RunawayDetector()
    fired = None
    for _ in range(8):
        fired = detector.feed(block)
        if fired:
            break
    assert fired, "eight copies of the same block must trip the guard"
    assert "already been written" in fired
    assert "300" in fired and "abort at 4" in fired


def test_a_varied_reply_never_fires():
    """A real answer keeps saying new things; the guard must be silent for all of it."""
    mod = _load()
    detector = mod.RunawayDetector()
    for i in range(400):
        assert detector.feed(f"  Scenario {i}: the member does distinct thing number {i}\n") is None
    assert detector.fired is None


def test_abort_closes_the_connection_and_keeps_the_text_received():
    mod = _load()
    block = "REPEAT-ME " * 40  # 400 characters
    stream = FakeStream(_repeating_chunks(block, 40))
    outcome = mod.consume_stream(stream, detector=mod.RunawayDetector(), on_abort=stream.close)

    assert outcome["aborted"] is True
    assert outcome["rule"]
    assert stream.closed is True, "the point of the guard is to stop paying: close the connection"
    assert stream.lines_read < len(stream.lines), "it must stop early, not read the whole reply"
    kept = outcome["reply"]["choices"][0]["message"]["content"]
    assert kept.startswith("REPEAT-ME"), "the text received so far is kept for the grader"
    assert 0 < outcome["tokens_received"] < 40
    assert outcome["chars_received"] == len(kept)


def test_a_healthy_stream_folds_into_the_non_streaming_shape():
    mod = _load()
    pieces = ["Feature: kiln booking\n", "  Scenario: one\n", "    Given a slot\n"]
    chunks = [_delta(content=p) for p in pieces]
    chunks.append({"choices": [{"delta": {}, "finish_reason": "stop"}], "usage": {"completion_tokens": 3}})
    outcome = mod.consume_stream(FakeStream(chunks), detector=mod.RunawayDetector())

    assert outcome["aborted"] is False
    assert outcome["rule"] is None
    reply = outcome["reply"]
    assert reply["choices"][0]["message"] == {"content": "".join(pieces)}
    assert reply["choices"][0]["finish_reason"] == "stop"
    assert reply["model"] == "fake-model"
    assert reply["usage"] == {"completion_tokens": 3}


def test_separated_thinking_survives_the_fold_under_either_field_name():
    """The two servers name that field differently; both must reach response_text() intact."""
    mod = _load()
    for field in ("reasoning_content", "reasoning"):
        chunks = [_delta(**{field: "weighing "}), _delta(**{field: "it up"}), _delta(content="body\n")]
        message = mod.consume_stream(FakeStream(chunks))["reply"]["choices"][0]["message"]
        assert message[field] == "weighing it up"
        assert message["content"] == "body\n"


def test_a_runaway_inside_the_thinking_is_caught_too():
    """A loop in the think block costs exactly as much as a loop in the answer."""
    mod = _load()
    block = "thinking in circles " * 20  # 400 characters
    chunks = [_delta(reasoning_content=block) for _ in range(40)]
    stream = FakeStream(chunks)
    outcome = mod.consume_stream(stream, detector=mod.RunawayDetector(), on_abort=stream.close)
    assert outcome["aborted"] is True
    assert stream.closed is True


def test_keepalives_junk_and_done_are_handled():
    mod = _load()
    raw = [
        b": keep-alive\n",
        b"\n",
        b"data: {not json\n",
        b'data: {"choices": [{"delta": {"content": "hello"}}]}\n',
        b"data: [DONE]\n",
        b'data: {"choices": [{"delta": {"content": "never read"}}]}\n',
    ]
    events = list(mod.iter_sse_events(raw))
    assert len(events) == 1
    assert events[0]["choices"][0]["delta"]["content"] == "hello"


def test_the_receipt_block_says_what_the_guard_did():
    mod = _load()
    off = mod.guard_record(False, None)
    assert off["enabled"] is False and "2026-09-03" in off["note"]

    quiet = mod.guard_record(True, {"aborted": False, "rule": None,
                                    "tokens_received": 120, "chars_received": 4000})
    assert quiet["enabled"] is True and quiet["fired"] is False
    assert quiet["tokens_received"] == 120 and "fired_rule" not in quiet

    fired = mod.guard_record(True, {"aborted": True, "rule": "the last 300 characters …",
                                    "tokens_received": 900, "chars_received": 15000})
    assert fired["fired"] is True and fired["fired_rule"] == "the last 300 characters …"
    assert fired["tokens_received"] == 900


def test_the_rule_would_have_caught_the_2026_09_03_runaway():
    """The incident that caused this guard, replayed 500 characters at a time.

    The receipt lives at runs/po-heldout-spec/20260902-followup-po-v6-v3-batchinvariant/
    po-held-007-feature-spec/rep1/response.txt (73,229 bytes, 203 `Scenario:` lines, 19
    distinct). runs/ is untracked by convention, so when it is absent this asserts nothing —
    the synthetic cases above carry the rule.
    """
    mod = _load()
    incident = (REPO_ROOT / "runs" / "po-heldout-spec"
                / "20260902-followup-po-v6-v3-batchinvariant"
                / "po-held-007-feature-spec" / "rep1" / "response.txt")
    if not incident.is_file():
        return
    text = incident.read_text(encoding="utf-8", errors="replace")
    detector = mod.RunawayDetector()
    for start in range(0, len(text), 500):
        if detector.feed(text[start:start + 500]):
            break
    assert detector.fired, "the guard must fire on the reply that caused it to exist"
    assert detector.chars < len(text) / 2, "and early enough to save most of the seventeen minutes"


def test_token_counts_are_asked_for_and_the_ask_is_dropped_if_the_server_refuses():
    """A streamed reply carries no usage unless asked; an older server must not fail the rep."""
    mod = _load()
    import urllib.error

    sent = []

    def refusing_opener(request, timeout=None):
        body = json.loads(request.data.decode("utf-8"))
        sent.append(body)
        if "stream_options" in body:
            raise urllib.error.HTTPError(request.full_url, 400, "unknown field", None, None)
        return FakeStream([_delta(content="hello")])

    outcome = mod.stream_chat_completion(
        "http://127.0.0.1:9/v1", {"model": "m", "messages": []}, 5, opener=refusing_opener)

    assert [("stream_options" in b) for b in sent] == [True, False]
    assert outcome["reply"]["choices"][0]["message"]["content"] == "hello"
