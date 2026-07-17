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
            # record the /running hit count at call time so a test can prove a probe
            # preceded THIS seat call (single-slot law, both attempts).
            self.server.running_at_chat.append(self.server.running_hits)  # type: ignore[attr-defined]
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                self.server.posted.append(json.loads(raw))  # type: ignore[attr-defined]
            except json.JSONDecodeError:
                self.server.posted.append(None)  # type: ignore[attr-defined]
            if cfg["chat_status"] != 200:
                self._send(cfg["chat_status"], {"error": "boom"})
                return
            # a per-call queue (content, finish) takes precedence, so a repair run can
            # return a DIFFERENT second answer; else fall back to the single content.
            queue = cfg.get("chat_queue")
            if queue:
                content, finish = queue.pop(0)
            else:
                content, finish = cfg["chat_content"], cfg["chat_finish"]
            self._send(200, {
                "choices": [{
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": finish,
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
        self.httpd.running_at_chat = []  # running_hits observed at each chat call
        self.httpd.posted = []           # parsed request bodies, in call order
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


# --- §10: default shape is byte-preserved (no new flags) -------------------------------

# the committed 07-16 config.json key set (finish_reason=="stop" => no finish_reason_note)
_COMMITTED_CONFIG_KEYS = {
    "suite", "task_id", "rep", "model", "endpoint", "sampling", "prompt_sha256",
    "prompt", "freeze_commit", "wall_time", "usage", "finish_reason",
    "generation_timeout_s", "transport_retries", "single_slot_probe", "runner",
}


def test_default_run_matches_committed_shape(tmp_path, seat):
    """Without the §10 flags the runner emits the committed 07-16 artifact shape:
    no vocab_ref key, no repair_loop/zero_shot_clean/repaired_clean/attempts, and
    exactly one seat call — proving the additive flags default to byte-identical."""
    seat.configure(chat_content="language dcl 1.0\n", chat_finish="stop")
    out = tmp_path / "rep-1"
    rc = rdh.main(_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert set(cfg.keys()) == _COMMITTED_CONFIG_KEYS
    # the §10-only artifacts must NOT appear on a default run
    for name in ("attempt-1.dcl", "attempt-1-checker.json", "raw-response-2.json",
                 "attempt-2-checker.json"):
        assert not (out / name).exists()
    # prompt_sha256 == the no-vocab composition
    assert cfg["prompt_sha256"] == rdh.compose_prompt(REAL_TASK_001)[2]
    assert seat.httpd.chat_hits == 1


# --- §10: --vocab-ref inclusion + sha coverage ----------------------------------------

def test_vocab_ref_appended_and_sha_covers_full_prompt(tmp_path, seat):
    vocab = tmp_path / "vocab-reference.md"
    vocab_body = "# CLOSED VOCAB\nactor kinds: human, system\nSENTINEL-VOCAB-LINE\n"
    vocab.write_text(vocab_body, encoding="utf-8")
    out = tmp_path / "rep-1"
    argv = _argv(REAL_TASK_001, out, seat.endpoint) + ["--vocab-ref", str(vocab)]
    rc = rdh.main(argv)
    assert rc == 0

    no_vocab_sha = rdh.compose_prompt(REAL_TASK_001)[2]
    with_vocab_sha = rdh.compose_prompt(REAL_TASK_001, vocab)[2]
    assert with_vocab_sha != no_vocab_sha  # appending the ref changes the prompt

    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    # prompt_sha256 covers the FULL composed prompt (instruction + inputs + vocab)
    assert cfg["prompt_sha256"] == with_vocab_sha
    # vocab_ref path + sha recorded (sha = of the vocab file content)
    assert cfg["vocab_ref"]["path"] == str(vocab.resolve())
    import hashlib
    assert cfg["vocab_ref"]["sha256"] == hashlib.sha256(vocab_body.encode("utf-8")).hexdigest()
    # the vocab text actually reached the model, under the delimiter
    sent_user = seat.httpd.posted[0]["messages"][1]["content"]
    assert "SENTINEL-VOCAB-LINE" in sent_user
    assert rdh.VOCAB_DELIM in sent_user


def test_vocab_ref_missing_file_refuses(tmp_path, seat):
    out = tmp_path / "rep-1"
    argv = _argv(REAL_TASK_001, out, seat.endpoint) + [
        "--vocab-ref", str(tmp_path / "does-not-exist.md")]
    with pytest.raises(rdh.Refusal):
        rdh.main(argv)


# --- §10: bounded (<=1) compile->repair loop ------------------------------------------

def _fake_checker(verdicts: dict):
    """A stand-in for the vendored checker keyed on the candidate filename, so the
    loop's firing decision is controlled without invoking real node/WASM."""
    def fake(path):
        ok = verdicts[str(path).rsplit("/", 1)[-1]]
        diags = [] if ok else [{"severity": "error", "code": "DCL_BAD", "message": "nope"}]
        return {"ok": ok, "diagnostics": diags, "diagnosticCount": len(diags),
                "errorCount": 0 if ok else 1, "warningCount": 0, "infoCount": 0,
                "sourceCount": 1}
    return fake


def _repair_argv(task_dir, out, endpoint):
    return _argv(task_dir, out, endpoint) + ["--repair-loop"]


def test_repair_loop_not_fired_on_clean_first(tmp_path, seat, monkeypatch):
    monkeypatch.setattr(rdh, "run_response_checker",
                        _fake_checker({"attempt-1.dcl": True}))
    seat.configure(chat_content="language dcl 1.0\nCLEAN\n", chat_finish="stop")
    out = tmp_path / "rep-1"
    rc = rdh.main(_repair_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0
    # exactly ONE seat call; no second call
    assert seat.httpd.chat_hits == 1
    assert not (out / "raw-response-2.json").exists()
    assert not (out / "attempt-2-checker.json").exists()
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["repair_loop"] is True
    assert cfg["zero_shot_clean"] is True
    assert cfg["repaired_clean"] is None
    assert cfg["attempts"] == 1
    assert (out / "attempt-1.dcl").read_text(encoding="utf-8") == "language dcl 1.0\nCLEAN\n"
    assert (out / "response.dcl").read_text(encoding="utf-8") == "language dcl 1.0\nCLEAN\n"
    # single-slot probe preceded the one call (preflight probe only)
    assert seat.httpd.running_hits == 1
    assert seat.httpd.running_at_chat == [1]


def test_repair_loop_fires_once_then_repaired_clean(tmp_path, seat, monkeypatch):
    # attempt 1 compiles dirty; the repaired FINAL compiles clean
    monkeypatch.setattr(rdh, "run_response_checker",
                        _fake_checker({"attempt-1.dcl": False, "response.dcl": True}))
    seat.configure(chat_queue=[("DIRTY-ONE\n", "stop"), ("REPAIRED-CLEAN\n", "stop")])
    out = tmp_path / "rep-1"
    rc = rdh.main(_repair_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0
    # exactly TWO seat calls — never a third (loop bounded at 1)
    assert seat.httpd.chat_hits == 2
    # graded candidate = the FINAL response
    assert (out / "response.dcl").read_text(encoding="utf-8") == "REPAIRED-CLEAN\n"
    assert (out / "attempt-1.dcl").read_text(encoding="utf-8") == "DIRTY-ONE\n"
    assert (out / "raw-response-2.json").is_file()
    assert (out / "attempt-1-checker.json").is_file()
    assert (out / "attempt-2-checker.json").is_file()
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["zero_shot_clean"] is False
    assert cfg["repaired_clean"] is True
    assert cfg["attempts"] == 2
    # the repair call's user message carried attempt 1 + the verbatim checker envelope
    repair_user = seat.httpd.posted[1]["messages"][1]["content"]
    assert "DIRTY-ONE" in repair_user
    assert "DCL_BAD" in repair_user  # the checker diagnostic, verbatim
    # a single-slot probe preceded EACH call: preflight(1) then pre-repair(2)
    assert seat.httpd.running_hits == 2
    assert seat.httpd.running_at_chat == [1, 2]


def test_repair_loop_dirty_second_recorded_honestly(tmp_path, seat, monkeypatch):
    # both attempts compile dirty -> still exactly two calls, honestly recorded
    monkeypatch.setattr(rdh, "run_response_checker",
                        _fake_checker({"attempt-1.dcl": False, "response.dcl": False}))
    seat.configure(chat_queue=[("DIRTY-ONE\n", "stop"), ("STILL-DIRTY\n", "stop")])
    out = tmp_path / "rep-1"
    rc = rdh.main(_repair_argv(REAL_TASK_001, out, seat.endpoint))
    assert rc == 0
    assert seat.httpd.chat_hits == 2  # never a third call
    assert (out / "response.dcl").read_text(encoding="utf-8") == "STILL-DIRTY\n"
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["zero_shot_clean"] is False
    assert cfg["repaired_clean"] is False  # honest: the repair did NOT land clean
    assert cfg["attempts"] == 2
