"""Integrity tests for the runaway guard inside harness/run_po_spec_eval.py.

What a rep receipt has to say after 2026-09-03, and what must not change:

  * a reply that repeats itself is stopped, and the rep's config.json says so — provenance
    `runaway_aborted`, the tokens that arrived, and the rule that fired;
  * a healthy reply is byte-identical to the one the old non-streaming path produced: same
    response.txt, same provenance string, re-wrapped thinking included;
  * `--no-runaway-guard` puts the old single non-streaming POST back, and the receipt says the
    guard was off — every run before 2026-09-03 was made that way, so the frozen exam's
    comparability is readable rather than remembered.

Written to RUN, following tests/test_po_spec_response_text.py: `test_*.py` in `tests/`, the
directory the documented invocation `pytest tests/ tasks/` collects; imports nothing optional,
skips nothing. No network: every model call is a fake transport.

Verify membership, not just outcome:
    python3 -m pytest tests/test_po_spec_runaway_guard.py --collect-only -q
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "harness" / "run_po_spec_eval.py"

FEATURE = ("=== FILE: kiln-firing-slot-booking.feature ===\n"
           "Feature: Kiln firing slot booking\n"
           "  Scenario: a member books a free slot\n"
           "    Given a free slot\n"
           "=== END FILE ===\n")


def _load():
    spec = importlib.util.spec_from_file_location("run_po_spec_eval_guard", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeStream:
    """A streamed reply: `data: {...}` lines, closable, counting what was actually read."""

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
    """The old path's response object: one JSON body, read in one go."""

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


def _stream_of(pieces: list[dict], sent: list, streams: list):
    """An opener the guard can use in place of urllib: records the body, returns a fake stream."""
    def opener(request, timeout=None):
        sent.append(json.loads(request.data.decode("utf-8")))
        stream = FakeStream(pieces)
        streams.append(stream)
        return stream
    return opener


def _args(tmp_path: Path, **over) -> argparse.Namespace:
    base = dict(model="fake-model", endpoint="http://127.0.0.1:9/v1",
                prompts_root=str(tmp_path), template_root=str(tmp_path), out=str(tmp_path),
                rep=None, dry_run=False, grade=False, temperature=0.0, top_p=None,
                max_tokens=16384, runaway_guard=True)
    base.update(over)
    return argparse.Namespace(**base)


def _wire(mod, monkeypatch):
    """Everything except the model call: no prompt trees, no git, no network."""
    monkeypatch.setattr(mod, "assemble", lambda *a, **k: {"system": "sys", "user": "user"})
    monkeypatch.setattr(mod, "prompts_root_identity", lambda p: {"path": str(p)})
    monkeypatch.setattr(mod, "template_root_identity", lambda p: {"path": str(p)})


TASK = {"task": {"suite": "po-heldout-spec", "schema": "feature-spec-triple",
                 "reps": 3, "timeout_seconds": 30}}


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
    result = mod.run_rep(_args(tmp_path, **over), TASK, tmp_path, 1, out_dir)
    rep_dir = out_dir / mod.TASK_ID / "rep1"
    return result, json.loads((rep_dir / "config.json").read_text()), rep_dir


def test_a_repeating_reply_is_aborted_and_the_receipt_says_so(tmp_path, monkeypatch):
    mod = _load()
    block = "  Scenario: a member books a free slot\n    Given a free slot\n" + "x" * 250 + "\n"
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
    assert sent[0]["stream"] is True
    assert streams[0].closed is True
    assert streams[0].lines_read < len(streams[0].lines), "it stops early, that is the whole point"


def test_a_healthy_streamed_reply_is_byte_identical_to_the_old_path(tmp_path, monkeypatch):
    mod = _load()
    pieces = [FEATURE[i:i + 17] for i in range(0, len(FEATURE), 17)]

    chunks = [_delta(content=p) for p in pieces]
    chunks.append({"choices": [{"delta": {}, "finish_reason": "stop"}],
                   "usage": {"completion_tokens": 9}})
    guarded, guarded_cfg, guarded_dir = _run(
        mod, tmp_path / "a", monkeypatch, opener=_stream_of(chunks, [], []))

    whole = {"model": "fake-model", "usage": {"completion_tokens": 9},
             "choices": [{"message": {"content": FEATURE}, "finish_reason": "stop"}]}
    plain, plain_cfg, plain_dir = _run(
        mod, tmp_path / "b", monkeypatch,
        whole=lambda req, timeout=None: FakeWholeReply(whole), runaway_guard=False)

    assert (guarded_dir / "response.txt").read_bytes() == (plain_dir / "response.txt").read_bytes()
    assert guarded_cfg["response_provenance"] == plain_cfg["response_provenance"] == "content_verbatim"
    assert guarded_cfg["tree_source"] == plain_cfg["tree_source"]
    assert guarded_cfg["files_written"] == plain_cfg["files_written"]
    assert guarded_cfg["finish_reason"] == plain_cfg["finish_reason"] == "stop"
    # a receipt must not lose its token counts because the reply is now streamed
    assert guarded_cfg["usage"] == plain_cfg["usage"] == {"completion_tokens": 9}
    assert guarded["status"] == plain["status"] == "ok"
    assert "text_provenance" not in guarded_cfg


def test_separated_thinking_is_rewrapped_identically_on_the_streamed_path(tmp_path, monkeypatch):
    """The re-wrap logic is the runner's own response_text(); streaming must not disturb it."""
    mod = _load()
    chunks = [_delta(reasoning="weighing "), _delta(reasoning="it up"), _delta(content=FEATURE)]
    _, config, rep_dir = _run(mod, tmp_path / "a", monkeypatch, opener=_stream_of(chunks, [], []))

    assert config["response_provenance"] == "rewrapped_reasoning"
    assert (rep_dir / "response.txt").read_text() == f"<think>weighing it up</think>\n{FEATURE}"


def test_no_runaway_guard_restores_the_old_non_streaming_path(tmp_path, monkeypatch):
    mod = _load()
    sent = []

    def whole(request, timeout=None):
        sent.append(json.loads(request.data.decode("utf-8")))
        return FakeWholeReply({"model": "fake-model",
                               "choices": [{"message": {"content": FEATURE},
                                            "finish_reason": "stop"}]})

    def explode(*a, **k):  # the streaming path must not be touched at all
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
    assert (rep_dir / "response.txt").read_text() == FEATURE


def test_the_flag_defaults_to_on_and_is_recorded_on_a_dry_run(tmp_path, monkeypatch):
    mod = _load()
    _wire(mod, monkeypatch)
    args = _args(tmp_path)
    out_dir = tmp_path / "dry"
    mod.run_rep(argparse.Namespace(**{**vars(args), "dry_run": True}), TASK, tmp_path, 1, out_dir)
    config = json.loads((out_dir / mod.TASK_ID / "rep1" / "config.json").read_text())
    assert config["runaway_guard"]["enabled"] is True
    assert config["runaway_guard"]["fired"] is False
