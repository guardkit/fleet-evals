"""Tests for harness/run_qav_heldout.py — the qav-heldout answer-sheet runner.

Additive (the qav-heldout suite is FROZEN at 2165802; this file is a NEW test
module touching no frozen path). NEVER calls the real seat or a GPU — all
model/probe traffic is served by a LOCAL mock http server bound to an ephemeral
localhost port (law 4). The mock records a /running hit count at each chat call
(running_at_chat) so a test can PROVE a fresh single-slot probe preceded EVERY
seat call. Covers: prompt-composition determinism + bundle inlining, every
preflight refusal (loud, nonzero), the happy path (verdict files byte-equal to
the extracted object + config.json fields incl. freeze_commit + per-bundle shas),
the no-JSON-extractable honest raw write, truncation honesty, the persistent-5xx
ABORTED path, the missing --freeze-commit SystemExit, and a happy-path answer
sheet that GRADES clean against the real qav_gates functions (runner ⟷ grader).
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness import qav_gates  # noqa: E402
from harness import run_qav_heldout as rqh  # noqa: E402

FREEZE = "2165802"
REAL_TASK_001 = REPO_ROOT / "tasks" / "qav-held-001-gold-negatives"
REAL_TASK_002 = REPO_ROOT / "tasks" / "qav-held-002-honest-green"


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
            # preceded THIS seat call (single-slot law, every bundle).
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
            # a per-call queue (content, finish) takes precedence, so each bundle can
            # get a DIFFERENT answer; else fall back to the single content.
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
            "running": [{"model": "qav-ft", "state": "ready"}],
            "chat_status": 200,
            "chat_content": '{"verdict": "approve", "findings": []}',
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


# a well-formed verdict per honest-green bundle (sorted order HG-01, RC-01, UG-01, UG-02):
# approve the honest/ugly greens, reject the catch floor RC-01 with its owning class + locus.
_GOOD_002_QUEUE = [
    ('{"verdict": "approve", "findings": []}', "stop"),                       # HG-01
    ('{"verdict": "reject", "findings": [{"class": "DC-14", '
     '"locus": "tests.tests_run=0 zero signal"}]}', "stop"),                  # RC-01
    ('{"verdict": "approve", "findings": []}', "stop"),                       # UG-01
    ('{"verdict": "approve", "findings": []}', "stop"),                       # UG-02
]


# --- prompt composition ---------------------------------------------------------------

def test_compose_prompt_is_deterministic():
    s1, u1, sha1 = rqh.compose_prompt(REAL_TASK_001, "GN-1")
    s2, u2, sha2 = rqh.compose_prompt(REAL_TASK_001, "GN-1")
    assert (s1, u1) == (s2, u2)
    assert sha1 == sha2 == hashlib.sha256(u1.encode("utf-8")).hexdigest()


def test_compose_prompt_inlines_the_bundle():
    _, user, _ = rqh.compose_prompt(REAL_TASK_001, "GN-1")
    bundle = (REAL_TASK_001 / "input" / "bundles" / "GN-1" / "bundle.json").read_text(
        encoding="utf-8").strip()
    assert "QA-verifier judgment seat" in user            # instruction.md verbatim
    assert "BEGIN input/bundles/GN-1/bundle.json" in user
    assert bundle.splitlines()[0] in user                 # the bundle inlined


def test_compose_prompt_differs_per_bundle():
    _, _, sha1 = rqh.compose_prompt(REAL_TASK_001, "GN-1")
    _, _, sha2 = rqh.compose_prompt(REAL_TASK_001, "GN-2")
    assert sha1 != sha2  # different bundle bytes => different prompt


# --- extraction -----------------------------------------------------------------------

def test_extract_json_fence_then_balanced():
    fenced = 'noise\n```json\n{"verdict": "approve", "findings": []}\n```\ntail'
    assert rqh.extract_json(fenced) == {"verdict": "approve", "findings": []}
    bare = 'thinking... {"verdict": "reject", "findings": [{"class": "DC-03"}]} done'
    assert rqh.extract_json(bare)["verdict"] == "reject"


def test_extract_json_handles_braces_in_strings():
    # a brace inside a JSON string must not break balance-matching
    content = '{"verdict": "reject", "findings": [{"class": "DC-14", "locus": "a{b}c"}]}'
    assert rqh.extract_json(content)["findings"][0]["locus"] == "a{b}c"


def test_extract_json_raises_when_absent():
    with pytest.raises(ValueError):
        rqh.extract_json("no json here at all")


# --- single-slot probe ----------------------------------------------------------------

def test_probe_single_slot_ok(seat):
    receipt = rqh.probe_single_slot(seat.endpoint, "qav-ft")
    assert receipt["probe_url"].endswith("/running")


def test_probe_single_slot_refuses_when_not_ready(seat):
    seat.configure(running=[{"model": "qav-ft", "state": "loading"}])
    with pytest.raises(rqh.Refusal):
        rqh.probe_single_slot(seat.endpoint, "qav-ft")


def test_probe_single_slot_refuses_when_unreachable():
    with pytest.raises(rqh.Refusal):
        rqh.probe_single_slot("http://127.0.0.1:1/v1/chat/completions", "qav-ft")


# --- preflight refusals ---------------------------------------------------------------

def _mktask(tmp_path: Path, *, suite="qav-heldout", instruction="judge it",
            bundles=("B-1",), with_bundle_json=True) -> Path:
    d = tmp_path / "qav-held-xxx"
    (d / "input" / "bundles").mkdir(parents=True)
    (d / "task.toml").write_text(
        f'[task]\nid = "qav-held-xxx"\nsuite = "{suite}"\ntimeout_seconds = 1800\n',
        encoding="utf-8")
    (d / "instruction.md").write_text(instruction, encoding="utf-8")
    for b in bundles:
        bd = d / "input" / "bundles" / b
        bd.mkdir(parents=True)
        if with_bundle_json:
            (bd / "bundle.json").write_text(
                json.dumps({"bundle_id": b}), encoding="utf-8")
    return d


def test_preflight_refuses_missing_task_dir(tmp_path, seat):
    with pytest.raises(rqh.Refusal):
        rqh.preflight(tmp_path / "nope", tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_wrong_suite(tmp_path, seat):
    d = _mktask(tmp_path, suite="coach-heldout")
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_unparseable_toml(tmp_path, seat):
    d = _mktask(tmp_path)
    (d / "task.toml").write_text("this is = = not toml", encoding="utf-8")
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_missing_instruction(tmp_path, seat):
    d = _mktask(tmp_path)
    (d / "instruction.md").unlink()
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_empty_instruction(tmp_path, seat):
    d = _mktask(tmp_path, instruction="   \n")
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_bundle_dir_without_bundle_json(tmp_path, seat):
    d = _mktask(tmp_path, bundles=("B-1", "B-2"), with_bundle_json=False)
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_no_bundles(tmp_path, seat):
    d = _mktask(tmp_path, bundles=())
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


def test_preflight_refuses_nonempty_out(tmp_path, seat):
    d = _mktask(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "verdicts").mkdir()
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, out, seat.endpoint, "qav-ft")


def test_preflight_refuses_failed_probe(tmp_path, seat):
    d = _mktask(tmp_path)
    seat.configure(running=None)  # /running 503
    with pytest.raises(rqh.Refusal):
        rqh.preflight(d, tmp_path / "out", seat.endpoint, "qav-ft")


# --- main: happy path -----------------------------------------------------------------

def _argv(task_dir: Path, out: Path, endpoint: str) -> list[str]:
    return [
        "--task-dir", str(task_dir), "--out", str(out),
        "--endpoint", endpoint, "--rep", "1",
        "--freeze-commit", FREEZE, "--timeout", "30",
    ]


def test_main_happy_path_writes_verbatim_artifacts(tmp_path, seat):
    seat.configure(chat_queue=list(_GOOD_002_QUEUE))
    out = tmp_path / "rep-1"
    rc = rqh.main(_argv(REAL_TASK_002, out, seat.endpoint))
    assert rc == 0

    ids = qav_gates.bundle_ids(REAL_TASK_002)  # sorted: HG-01, RC-01, UG-01, UG-02
    assert seat.httpd.chat_hits == len(ids)
    for content, bid in zip((q[0] for q in _GOOD_002_QUEUE), ids):
        # verdict file == the extracted object, re-serialised deterministically
        expected = json.dumps(rqh.extract_json(content), indent=2)
        assert (out / "verdicts" / f"{bid}.json").read_text(encoding="utf-8") == expected
        assert (out / "responses" / f"{bid}.raw-response.json").is_file()

    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["suite"] == "qav-heldout"
    assert cfg["task_id"] == "qav-held-002-honest-green"
    assert cfg["rep"] == 1
    assert cfg["model"] == "qav-ft"
    assert cfg["freeze_commit"] == FREEZE
    assert cfg["sampling"] == {"temperature": 0.1, "top_p": 0.9, "max_tokens": 2048}
    assert cfg["generation_timeout_s"] == 30
    # per-bundle shas recorded and correct
    for bid in ids:
        meta = cfg["bundles"][bid]
        _, _, psha = rqh.compose_prompt(REAL_TASK_002, bid)
        bsha = hashlib.sha256(
            (REAL_TASK_002 / "input" / "bundles" / bid / "bundle.json").read_bytes()).hexdigest()
        assert meta["prompt_sha256"] == psha
        assert meta["bundle_sha256"] == bsha
        assert meta["finish_reason"] == "stop"
        assert meta["truncated"] is False
        assert meta["json_extracted"] is True


def test_main_probe_precedes_every_seat_call(tmp_path, seat):
    seat.configure(chat_queue=list(_GOOD_002_QUEUE))
    out = tmp_path / "rep-1"
    rc = rqh.main(_argv(REAL_TASK_002, out, seat.endpoint))
    assert rc == 0
    n = len(qav_gates.bundle_ids(REAL_TASK_002))  # 4 bundles
    assert seat.httpd.chat_hits == n
    # a fresh probe preceded EVERY seat call: preflight readiness probe (#1) then one
    # per-bundle probe before each of the 4 calls => running_at_chat == [2, 3, 4, 5].
    assert seat.httpd.running_at_chat == [2, 3, 4, 5]
    assert seat.httpd.running_hits == n + 1
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    # a probe receipt for preflight + one per bundle
    assert len(cfg["single_slot_probe"]) == n + 1


def test_main_answer_sheet_grades_clean_against_qav_gates(tmp_path, seat):
    """The runner and the grader must actually mate: a well-formed answer sheet
    produces zero verdict_schema_findings (G-Q1 contract battery) for every
    bundle when loaded by the real qav_gates functions."""
    seat.configure(chat_queue=list(_GOOD_002_QUEUE))
    out = tmp_path / "rep-1"
    assert rqh.main(_argv(REAL_TASK_002, out, seat.endpoint)) == 0
    for bid in qav_gates.bundle_ids(REAL_TASK_002):
        verdict = qav_gates.load_verdict(out, bid)
        assert qav_gates.verdict_schema_findings(verdict, bid) == []


def test_main_no_json_extractable_writes_raw_bytes(tmp_path, seat):
    """A reply with no JSON object is a RESULT, not a retry: the raw assistant
    text is written to the verdict file so qav_gates.load_verdict surfaces it as
    an 'unloadable' finding — never a fabricated verdict."""
    seat.configure(chat_content="I refuse to answer in JSON.", chat_finish="stop",
                   chat_queue=None)
    out = tmp_path / "rep-1"
    assert rqh.main(_argv(REAL_TASK_002, out, seat.endpoint)) == 0
    bid = qav_gates.bundle_ids(REAL_TASK_002)[0]
    assert (out / "verdicts" / f"{bid}.json").read_text(
        encoding="utf-8") == "I refuse to answer in JSON."
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    assert cfg["bundles"][bid]["json_extracted"] is False
    # the grader surfaces it honestly (unparseable -> load_error -> unloadable finding)
    verdict = qav_gates.load_verdict(out, bid)
    findings = qav_gates.verdict_schema_findings(verdict, bid)
    assert findings and findings[0]["defect"] == "unloadable"


def test_main_records_truncation_honestly(tmp_path, seat):
    seat.configure(chat_content="", chat_finish="length", chat_queue=None)
    out = tmp_path / "rep-1"
    assert rqh.main(_argv(REAL_TASK_002, out, seat.endpoint)) == 0  # a RESULT, still recorded
    cfg = json.loads((out / "config.json").read_text(encoding="utf-8"))
    bid = qav_gates.bundle_ids(REAL_TASK_002)[0]
    meta = cfg["bundles"][bid]
    assert meta["finish_reason"] == "length"
    assert meta["truncated"] is True
    assert "finish_reason_note" in meta
    # empty content -> empty verdict file -> honestly unloadable at grade time
    assert (out / "verdicts" / f"{bid}.json").read_text(encoding="utf-8") == ""


# --- main: ABORTED transport path -----------------------------------------------------

def test_main_aborts_on_persistent_5xx(tmp_path, seat, monkeypatch):
    monkeypatch.setattr(rqh.time, "sleep", lambda *_: None)  # keep the retry loop fast
    seat.configure(chat_status=500)
    out = tmp_path / "rep-1"
    rc = rqh.main(_argv(REAL_TASK_002, out, seat.endpoint))
    assert rc == 1
    aborted = json.loads((out / "ABORTED.json").read_text(encoding="utf-8"))
    assert aborted["rep"] == 1
    assert aborted["attempts"] == rqh.TRANSPORT_RETRIES + 1
    assert aborted["bundle_id"] == qav_gates.bundle_ids(REAL_TASK_002)[0]  # first bundle
    assert "INVALID" in aborted["disposition"]
    # NO config.json is ever written for an aborted rep (no silent partial sheet)
    assert not (out / "config.json").exists()
    # the retry budget hit exactly on the first bundle, then stopped (no further calls)
    assert seat.httpd.chat_hits == rqh.TRANSPORT_RETRIES + 1


# --- main: CLI contract ---------------------------------------------------------------

def test_main_refuses_missing_freeze_commit(tmp_path, seat):
    out = tmp_path / "rep-1"
    with pytest.raises(SystemExit):
        rqh.main(["--task-dir", str(REAL_TASK_002), "--out", str(out),
                  "--endpoint", seat.endpoint, "--rep", "1"])
