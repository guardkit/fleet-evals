"""Tests for harness/run_dcl_heldout.py — the dcl-heldout answer-sheet runner.

Additive (the dcl-heldout suite is FROZEN at 8d2d676; this file is a NEW test
module, touching no frozen path). NEVER calls the real seat — all model/probe
traffic is served by a LOCAL mock http server bound to an ephemeral localhost
port. Covers: prompt-composition determinism + input inlining, the single-slot
probe, preflight refusals (loud, nonzero), the ABORTED transport path, and the
happy-path artifacts (response.dcl byte-for-byte + config.json fields).
"""
from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness import run_dcl_heldout as rdh  # noqa: E402

FREEZE = "8d2d6762c38ef0a3aab1c8d5904dd456e008500b"
REAL_TASK_001 = REPO_ROOT / "tasks" / "dcl-held-001-author-stats"
REAL_TASK_004 = REPO_ROOT / "tasks" / "dcl-held-004-repair-diagnostics"


# --- mock llama-swap server (ephemeral localhost port) --------------------------------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # silence
        pass

    def _send(self, code: int, payload) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        if self.path == "/running":
            cfg = self.server.cfg  # type: ignore[attr-defined]
            self.server.running_hits += 1  # type: ignore[attr-defined]
            if cfg["running"] is None:
                self._send(503, {"error": "no models loaded"})
            else:
                self._send(200, cfg["running"])
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if self.path == "/v1/chat/completions":
            cfg = self.server.cfg  # type: ignore[attr-defined]
            self.server.chat_hits += 1  # type: ignore[attr-defined]
            length = int(self.headers.get("Content-Length", 0))
            self.rfile.read(length)
            if cfg["chat_status"] != 200:
                self._send(cfg["chat_status"], {"error": "boom"})
                return
            self._send(200, {
                "choices": [{
                    "message": {"role": "assistant", "content": cfg["chat_content"]},
                    "finish_reason": cfg["chat_finish"],
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            })
        else:
            self._send(404, {"error": "not found"})


class MockSeat:
    def __init__(self):
        self.httpd = HTTPServer(("127.0.0.1", 0), _Handler)
        self.httpd.cfg = {
            "running": [{"model": "qwen36-workhorse", "state": "ready"}],
            "chat_status": 200,
            "chat_content": "language dcl 1.0\n",
            "chat_finish": "stop",
        }
        self.httpd.running_hits = 0
        self.httpd.chat_hits = 0
        self._t = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._t.start()

    @property
    def endpoint(self) -> str:
        host, port = self.httpd.server_address
        return f"http://127.0.0.1:{port}/v1/chat/completions"

    def configure(self, **kw):
        self.httpd.cfg.update(kw)

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def seat():
    s = MockSeat()
    try:
        yield s
    finally:
        s.close()


# --- prompt composition ---------------------------------------------------------------

def test_compose_prompt_is_deterministic():
    s1, u1, sha1 = rdh.compose_prompt(REAL_TASK_001)
    s2, u2, sha2 = rdh.compose_prompt(REAL_TASK_001)
    assert (s1, u1) == (s2, u2)
    assert sha1 == sha2
    assert sha1 == __import__("hashlib").sha256(u1.encode("utf-8")).hexdigest()


def test_compose_prompt_inlines_referenced_inputs():
    _, user, _ = rdh.compose_prompt(REAL_TASK_001)
    brief = (REAL_TASK_001 / "input" / "feature-brief.md").read_text(encoding="utf-8").strip()
    # instruction text is present, and the referenced input is inlined verbatim
    assert "author a DCL capability" in user
    assert "BEGIN input/feature-brief.md" in user
    assert brief.splitlines()[0] in user


def test_compose_prompt_inlines_multiple_inputs_in_order():
    _, user, _ = rdh.compose_prompt(REAL_TASK_004)
    # 004 references broken.dcl BEFORE diagnostics.json in instruction.md
    assert user.index("BEGIN input/broken.dcl") < user.index("BEGIN input/diagnostics.json")


def test_referenced_inputs_ignores_missing(tmp_path):
    (tmp_path / "input").mkdir()
    (tmp_path / "instruction.md").write_text(
        "see input/present.md and input/ghost.md", encoding="utf-8")
    (tmp_path / "input" / "present.md").write_text("here", encoding="utf-8")
    got = [p.name for p in rdh.referenced_inputs(
        (tmp_path / "instruction.md").read_text(), tmp_path)]
    assert got == ["present.md"]


# --- single-slot probe ----------------------------------------------------------------

def test_slot_ready_variants():
    assert rdh.slot_ready([{"model": "qwen36-workhorse", "state": "ready"}], "qwen36-workhorse")
    assert rdh.slot_ready({"running": [{"model": "m", "state": "ready"}]}, "m")
    assert not rdh.slot_ready([{"model": "m", "state": "loading"}], "m")
    assert not rdh.slot_ready([{"model": "other", "state": "ready"}], "m")
    assert not rdh.slot_ready({}, "m")


def test_probe_base_derivation():
    assert rdh.probe_base("http://127.0.0.1:9000/v1/chat/completions") == "http://127.0.0.1:9000"


def test_probe_single_slot_ok(seat):
    receipt = rdh.probe_single_slot(seat.endpoint, "qwen36-workhorse")
    assert receipt["probe_url"].endswith("/running")


def test_probe_single_slot_refuses_when_not_ready(seat):
    seat.configure(running=[{"model": "qwen36-workhorse", "state": "loading"}])
    with pytest.raises(rdh.Refusal):
        rdh.probe_single_slot(seat.endpoint, "qwen36-workhorse")


def test_probe_single_slot_refuses_when_probe_unreachable():
    # nothing is listening on this port -> loud refusal, never a degrade
    with pytest.raises(rdh.Refusal):
        rdh.probe_single_slot("http://127.0.0.1:1/v1/chat/completions", "qwen36-workhorse")


# --- preflight refusals ---------------------------------------------------------------

def _mktask(tmp_path: Path, *, suite="dcl-heldout", instruction="do it",
            with_input=True) -> Path:
    d = tmp_path / "dcl-held-xxx"
    (d / "input").mkdir(parents=True)
    (d / "task.toml").write_text(
        f'[task]\nid = "dcl-held-xxx"\nsuite = "{suite}"\ntimeout_seconds = 900\n',
        encoding="utf-8")
    (d / "instruction.md").write_text(instruction, encoding="utf-8")
    if with_input:
        (d / "input" / "feature-brief.md").write_text("brief", encoding="utf-8")
    return d


def test_preflight_refuses_wrong_suite(tmp_path, seat):
    d = _mktask(tmp_path, suite="po-heldout")
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, tmp_path / "out", seat.endpoint, "qwen36-workhorse")


def test_preflight_refuses_missing_instruction(tmp_path, seat):
    d = _mktask(tmp_path)
    (d / "instruction.md").unlink()
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, tmp_path / "out", seat.endpoint, "qwen36-workhorse")


def test_preflight_refuses_missing_referenced_input(tmp_path, seat):
    d = _mktask(tmp_path, instruction="read input/feature-brief.md", with_input=False)
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, tmp_path / "out", seat.endpoint, "qwen36-workhorse")


def test_preflight_refuses_unparseable_toml(tmp_path, seat):
    d = _mktask(tmp_path)
    (d / "task.toml").write_text("this is = = not toml", encoding="utf-8")
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, tmp_path / "out", seat.endpoint, "qwen36-workhorse")


def test_preflight_refuses_nonempty_out(tmp_path, seat):
    d = _mktask(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "response.dcl").write_text("stale", encoding="utf-8")
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, out, seat.endpoint, "qwen36-workhorse")


def test_preflight_refuses_failed_probe(tmp_path, seat):
    d = _mktask(tmp_path)
    seat.configure(running=None)  # /running 503
    with pytest.raises(rdh.Refusal):
        rdh.preflight(d, tmp_path / "out", seat.endpoint, "qwen36-workhorse")


# --- main: happy path + ABORTED -------------------------------------------------------

def _argv(task_dir: Path, out: Path, endpoint: str) -> list[str]:
    return [
        "--task-dir", str(task_dir), "--out", str(out),
        "--endpoint", endpoint, "--rep", "1",
        "--freeze-commit", FREEZE, "--timeout", "30",
    ]


def test_main_happy_path_writes_verbatim_artifacts(tmp_path, seat):
    content = "language dcl 1.0\n\ncapability GetStats {\n  intent X from Y\n}\n"
    seat.configure(chat_content=content, chat_finish="stop")
    out = tmp_path / "rep-1"
    rc = rdh.main(_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0
    # response.dcl = assistant content byte-for-byte
    assert (out / "response.dcl").read_text(encoding="utf-8") == content
    assert (out / "raw-response.json").is_file()
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["suite"] == "dcl-heldout"
    assert cfg["task_id"] == "dcl-held-001-author-stats"
    assert cfg["rep"] == 1
    assert cfg["model"] == "qwen36-workhorse"
    assert cfg["freeze_commit"] == FREEZE
    assert cfg["finish_reason"] == "stop"
    assert cfg["sampling"] == {"temperature": 0.3, "top_p": 0.9, "max_tokens": 16384}
    assert cfg["prompt_sha256"] == rdh.compose_prompt(REAL_TASK_001)[2]
    assert cfg["usage"]["total_tokens"] == 30
    assert cfg["single_slot_probe"]["ok"] is True
    # exactly one generation call (bounded, sequential)
    assert seat.httpd.chat_hits == 1


def test_main_records_truncation_honestly(tmp_path, seat):
    seat.configure(chat_content="", chat_finish="length")
    out = tmp_path / "rep-1"
    rc = rdh.main(_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0  # a truncated/bad answer is a RESULT, still recorded (not a runner error)
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["finish_reason"] == "length"
    assert "finish_reason_note" in cfg
    assert (out / "response.dcl").read_text(encoding="utf-8") == ""


def test_main_aborts_on_persistent_5xx(tmp_path, seat, monkeypatch):
    monkeypatch.setattr(rdh.time, "sleep", lambda *_: None)  # keep the retry loop fast
    seat.configure(chat_status=500)
    out = tmp_path / "rep-1"
    rc = rdh.main(_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 1
    aborted = json.loads((out / "ABORTED.json").read_text(encoding="utf-8"))
    assert aborted["rep"] == 1
    assert aborted["attempts"] == rdh.TRANSPORT_RETRIES + 1
    assert "INVALID" in aborted["disposition"]
    # no answer sheet is ever written for an aborted rep
    assert not (out / "response.dcl").exists()
    assert not (out / "config.json").exists()
    assert seat.httpd.chat_hits == rdh.TRANSPORT_RETRIES + 1


def test_main_refuses_missing_freeze_commit(tmp_path, seat):
    out = tmp_path / "rep-1"
    with pytest.raises(SystemExit):
        rdh.main(["--task-dir", str(REAL_TASK_001), "--out", str(out),
                  "--endpoint", seat.endpoint, "--rep", "1"])
