"""Integrity tests for the runaway guard inside harness/run_po_eval.py.

Same three things the spec runner's guard has to hold (see
tests/test_po_spec_runaway_guard.py), plus the one thing only this runner has: a tool-calling
turn loop. A reply that has started repeating itself must end the loop rather than be re-asked —
re-asking a looping model is exactly the cost the guard exists to stop.

  * a reply that repeats itself is stopped, and the rep's config.json says so — provenance
    `runaway_aborted`, the tokens that arrived, and the rule that fired;
  * a healthy reply is byte-identical to the one the old non-streaming path produced: same
    response.txt, same provenance string, re-wrapped thinking included;
  * `--no-runaway-guard` puts the old single non-streaming POST back, and the receipt says the
    guard was off — every run before 2026-09-03 was made that way.

Written to RUN, following tests/test_po_eval_response_text.py: `test_*.py` in `tests/`, the
directory the documented invocation `pytest tests/ tasks/` collects; imports nothing optional,
skips nothing. No network: every model call is a fake transport.

Verify membership, not just outcome:
    python3 -m pytest tests/test_po_eval_runaway_guard.py --collect-only -q
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "harness" / "run_po_eval.py"

ANSWER = '{\n  "facts": [\n    {"id": "F1", "text": "members book kiln slots"}\n  ]\n}\n'
TASK_ID = "po-held-001-extract-phase-a"
TASK = {"task": {"suite": "po-heldout", "schema": "extract-phase-a", "reps": 3,
                 "timeout_seconds": 30},
        "provenance": {"instruction_source": "instruction.md"}}


def _load():
    spec = importlib.util.spec_from_file_location("run_po_eval_guard", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeStream:
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


class FakeWholeReply:
    def __init__(self, payload: dict):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _delta(**fields) -> dict:
    return {"model": "fake-model", "choices": [{"delta": dict(fields)}]}


def _stream_of(chunks: list[dict], sent: list, streams: list):
    def opener(request, timeout=None):
        sent.append(json.loads(request.data.decode("utf-8")))
        stream = FakeStream(chunks)
        streams.append(stream)
        return stream
    return opener


def _args(tmp_path: Path, **over) -> argparse.Namespace:
    base = dict(model="fake-model", endpoint="http://127.0.0.1:9/v1",
                prompts_root=str(tmp_path), out=str(tmp_path), suite="po-heldout",
                task=None, rep=None, dry_run=False, grade=False, temperature=0.6,
                top_p=0.95, max_tokens=16384, runaway_guard=True)
    base.update(over)
    return argparse.Namespace(**base)


def _wire(mod, monkeypatch):
    monkeypatch.setattr(mod, "assemble", lambda *a, **k: {"system": "sys", "user": "user",
                                                          "project": "fleet-evals"})


def _run(mod, tmp_path, monkeypatch, opener=None, whole=None, **over):
    _wire(mod, monkeypatch)
    if opener is not None:
        real = mod.stream_chat_completion
        monkeypatch.setattr(
            mod, "stream_chat_completion",
            lambda endpoint, body, timeout_s, detector=None: real(
                endpoint, body, timeout_s, detector, opener=opener),
        )
    if whole is not None:
        monkeypatch.setattr(urllib.request, "urlopen", whole)
    out_dir = tmp_path / "run"
    result = mod.run_rep(_args(tmp_path, **over), TASK_ID, TASK, tmp_path, 1, out_dir)
    rep_dir = out_dir / TASK_ID / "rep1"
    return result, json.loads((rep_dir / "config.json").read_text()), rep_dir


def test_a_repeating_reply_is_aborted_and_the_receipt_says_so(tmp_path, monkeypatch):
    mod = _load()
    block = '    {"id": "F1", "text": "members book kiln slots"},\n' + "y" * 260 + "\n"
    sent, streams = [], []
    result, config, rep_dir = _run(
        mod, tmp_path, monkeypatch, opener=_stream_of([_delta(content=block)] * 40, sent, streams))

    assert result["status"] == "runaway aborted"
    assert config["response_provenance"] == "runaway_aborted"
    guard = config["runaway_guard"]
    assert guard["enabled"] is True and guard["fired"] is True
    assert "already been written" in guard["fired_rule"]
    assert guard["tokens_received"] > 0
    assert guard["chars_received"] == len((rep_dir / "response.txt").read_text())
    assert config["text_provenance"] == "content_verbatim"
    assert len(sent) == 1, "a looping model must not be re-asked — that is the cost being stopped"
    assert streams[0].closed is True
    assert streams[0].lines_read < len(streams[0].lines)


def test_a_healthy_streamed_reply_is_byte_identical_to_the_old_path(tmp_path, monkeypatch):
    mod = _load()
    pieces = [ANSWER[i:i + 11] for i in range(0, len(ANSWER), 11)]

    chunks = [_delta(content=p) for p in pieces]
    chunks.append({"choices": [{"delta": {}, "finish_reason": "stop"}],
                   "usage": {"completion_tokens": 9}})
    guarded, guarded_cfg, guarded_dir = _run(
        mod, tmp_path / "a", monkeypatch, opener=_stream_of(chunks, [], []))

    whole = {"model": "fake-model", "usage": {"completion_tokens": 9},
             "choices": [{"message": {"content": ANSWER}, "finish_reason": "stop"}]}
    plain, plain_cfg, plain_dir = _run(
        mod, tmp_path / "b", monkeypatch,
        whole=lambda req, timeout=None: FakeWholeReply(whole), runaway_guard=False)

    assert (guarded_dir / "response.txt").read_bytes() == (plain_dir / "response.txt").read_bytes()
    assert guarded_cfg["response_provenance"] == plain_cfg["response_provenance"] == "content_verbatim"
    assert guarded_cfg["finish_reason"] == plain_cfg["finish_reason"] == "stop"
    # a receipt must not lose its token counts because the reply is now streamed
    assert guarded_cfg["usage"] == plain_cfg["usage"] == {"completion_tokens": 9}
    assert guarded["status"] == plain["status"] == "ok"
    assert "text_provenance" not in guarded_cfg


def test_separated_thinking_is_rewrapped_identically_on_the_streamed_path(tmp_path, monkeypatch):
    mod = _load()
    chunks = [_delta(reasoning_content="weighing "), _delta(reasoning_content="it up"),
              _delta(content=ANSWER)]
    _, config, rep_dir = _run(mod, tmp_path / "a", monkeypatch, opener=_stream_of(chunks, [], []))

    assert config["response_provenance"] == "rewrapped_reasoning_content"
    assert (rep_dir / "response.txt").read_text() == f"<think>weighing it up</think>\n{ANSWER}"


def test_no_runaway_guard_restores_the_old_non_streaming_path(tmp_path, monkeypatch):
    mod = _load()
    sent = []

    def whole(request, timeout=None):
        sent.append(json.loads(request.data.decode("utf-8")))
        return FakeWholeReply({"model": "fake-model",
                               "choices": [{"message": {"content": ANSWER},
                                            "finish_reason": "stop"}]})

    def explode(*a, **k):
        raise AssertionError("--no-runaway-guard must not stream")

    monkeypatch.setattr(mod, "stream_chat_completion", explode)
    result, config, rep_dir = _run(mod, tmp_path, monkeypatch, whole=whole, runaway_guard=False)

    assert result["status"] == "ok"
    assert sent[0]["stream"] is False
    assert config["response_provenance"] == "content_verbatim"
    assert config["runaway_guard"] == {
        "enabled": False,
        "note": "off (--no-runaway-guard): the reply was read in one non-streaming response, "
                "as in every run before 2026-09-03",
    }
    assert (rep_dir / "response.txt").read_text() == ANSWER


def test_a_tool_call_turn_still_works_under_the_guard(tmp_path, monkeypatch):
    """The guard streams each turn; the tool loop must be unchanged for a healthy reply."""
    mod = _load()
    tool_turn = [_delta(content='call:corpus_search{query: "kiln"}')]
    answer_turn = [_delta(content=ANSWER)]
    turns = [tool_turn, answer_turn]
    sent = []

    def opener(request, timeout=None):
        body = json.loads(request.data.decode("utf-8"))
        sent.append(body)
        return FakeStream(turns[len(sent) - 1])

    monkeypatch.setattr(mod, "_execute_tool", lambda name, query: "[]")
    result, config, rep_dir = _run(mod, tmp_path, monkeypatch, opener=opener)

    assert result["status"] == "ok"
    assert len(sent) == 2, "the tool turn is serviced, then the answer turn is read"
    assert (rep_dir / "response.txt").read_text() == ANSWER
    assert config["runaway_guard"]["fired"] is False


def test_the_flag_defaults_to_on_and_is_recorded_on_a_dry_run(tmp_path, monkeypatch):
    mod = _load()
    _wire(mod, monkeypatch)
    args = _args(tmp_path)
    out_dir = tmp_path / "dry"
    mod.run_rep(argparse.Namespace(**{**vars(args), "dry_run": True}), TASK_ID, TASK,
                tmp_path, 1, out_dir)
    config = json.loads((out_dir / TASK_ID / "rep1" / "config.json").read_text())
    assert config["runaway_guard"]["enabled"] is True
    assert config["runaway_guard"]["fired"] is False
