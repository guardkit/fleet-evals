#!/usr/bin/env python3
"""dcl-heldout runner — the DCL authoring seat's answer-sheet producer.

Runner divergence, by design (the run_gc_heldout.py / run_coach_heldout.py
precedent): answer sheets are produced by ONE fresh toolless generation per rep
against the served checkpoint (llama-swap :9000, chat completion), NOT by
harness/run_po_eval.py and NOT by importing run_gc_heldout / run_coach_heldout
logic. This runner NEVER grades: grading is the task's gate battery
(`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task>/test -q`), which
shells the vendored DCL compiler over the candidate `response.dcl`. A bad `.dcl`
is a RESULT, not a retry trigger — there is no retry-on-bad-content here.

Pre-flight refuses loudly (never degrades):
  - task.toml must parse and declare suite == "dcl-heldout";
  - instruction.md + the input/ files it references must be present;
  - the output dir must be writable and empty-or-fresh (never overwrite another
    rep's sheet);
  - single-slot law: GET <base>/running must show the target alias `ready` before
    any generation — the exact check the DCL spike recorded before claiming the
    seat. Calls are strictly sequential, one bounded call in flight.

Transport: 2 retries on connection / 5xx errors, then the rep ABORTS with
ABORTED.json written (rep INVALID, not a failure — re-run in place; no fabricated
or empty response is ever graded).

The token-ceiling lesson (SEAT-RESULT.md) is pinned in the default max_tokens
(16384): the spike's first call truncated at 4096 with an empty answer because
all tokens went to the reasoning channel. A rep that truncates
(finish_reason != "stop") is recorded HONESTLY and still graded.

stdlib-only (urllib etc.) + pytest for the tests. No new dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - environment is 3.12 (see .pyc pins)
    tomllib = None  # type: ignore

SUITE = "dcl-heldout"

# The one-line system turn the spike used (SEAT-RESULT.md §Setup): output only
# DCL, no prose, no fences. Pinned so the composed prompt is deterministic.
PINNED_SYSTEM_PROMPT = "Output ONLY the DCL source. No prose, no explanation, no markdown fences."

# Referenced-input discovery: markdown links / inline code paths of the form
# `input/<name>` in each task's instruction.md. Order = first appearance.
_INPUT_REF = re.compile(r"input/[A-Za-z0-9._][A-Za-z0-9._/-]*")

TRANSPORT_RETRIES = 2  # => up to 3 total attempts (1 + 2 retries), then ABORT
PROBE_TIMEOUT_S = 15

# §10 protocol (additive, opt-in) ------------------------------------------------------
# The standing vocabulary reference is appended to the composed user prompt under this
# delimiter (--vocab-ref); prompt_sha256 covers the full composed prompt including it.
VOCAB_DELIM = "\n\n=== DCL v1.0 VERIFIED VOCABULARY REFERENCE ===\n"

# The vendored checker used by the bounded compile->repair loop (--repair-loop). This is
# NOT grading: the runner runs the compiler here only to decide whether to fire the ONE
# bounded repair call (§10). The graded candidate is still response.dcl, judged later by
# the task's gate battery. Same checker home as harness/dcl_gates.py (the ONE checker).
DCL_CHECKER = Path(__file__).resolve().parent / "dcl" / "bin" / "dcl-check.mjs"
CHECKER_TIMEOUT_S = 120

# The terse repair instruction for the second (bounded) call.
REPAIR_INSTRUCTION = (
    "The DCL compiler REJECTED your previous attempt with the diagnostics above. "
    "Fix exactly those errors while preserving the declared semantics, and return "
    "ONLY the corrected, compile-clean DCL source — the full .dcl file, no prose, "
    "no explanation, no markdown fences."
)


class Refusal(SystemExit):
    """A loud, nonzero preflight refusal — never a silent degrade."""


class TransportAborted(RuntimeError):
    def __init__(self, attempts: int, last: str) -> None:
        super().__init__(f"transport aborted after {attempts} attempt(s): {last}")
        self.attempts = attempts
        self.last = last


# --- prompt composition (deterministic) -----------------------------------------------

def referenced_inputs(instruction: str, task_dir: Path) -> list[Path]:
    """The input/ files the instruction.md directs the reader to read, in first
    appearance order, deduped, restricted to files that actually exist under the
    task's input/ dir (a referenced-but-missing input is caught in preflight)."""
    seen: list[str] = []
    for m in _INPUT_REF.finditer(instruction):
        rel = m.group(0)
        if rel not in seen:
            seen.append(rel)
    out: list[Path] = []
    for rel in seen:
        p = (task_dir / rel).resolve()
        # keep it inside the task's input/ dir (no traversal), and existing
        try:
            p.relative_to((task_dir / "input").resolve())
        except ValueError:
            continue
        if p.is_file():
            out.append(p)
    return out


def compose_prompt(task_dir: Path, vocab_ref: Path | None = None) -> tuple[str, str, str]:
    """Return (system, user, prompt_sha256).

    The user turn = the task's instruction.md verbatim, followed by each
    input/ file it references inlined in a clearly delimited, order-stable block
    (the model cannot follow file links; the spike embedded its inputs inline).
    Deterministic: same instruction + same inputs => same bytes => same sha256.

    §10 additive: when ``vocab_ref`` is given, its content is appended verbatim
    under ``VOCAB_DELIM`` and prompt_sha256 covers the FULL composed prompt
    including it. When ``vocab_ref is None`` the returned bytes are byte-identical
    to the pre-amendment composition (default behaviour is unchanged)."""
    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8")
    parts = [instruction.rstrip("\n")]
    for path in referenced_inputs(instruction, task_dir):
        rel = path.relative_to(task_dir).as_posix()
        body = path.read_text(encoding="utf-8").rstrip("\n")
        parts.append(f"\n\n----- BEGIN {rel} -----\n{body}\n----- END {rel} -----")
    user = "".join(parts) + "\n"
    if vocab_ref is not None:
        user = user + VOCAB_DELIM + vocab_ref.read_text(encoding="utf-8")
    prompt_sha256 = hashlib.sha256(user.encode("utf-8")).hexdigest()
    return PINNED_SYSTEM_PROMPT, user, prompt_sha256


# --- single-slot probe (repo law) -----------------------------------------------------

def probe_base(endpoint: str) -> str:
    """Derive the llama-swap base URL (scheme://host[:port]) from the chat
    endpoint so the probe hits <base>/running on the same server."""
    parts = urlsplit(endpoint)
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def _slot_entries(payload) -> list[dict]:
    if isinstance(payload, dict):
        for key in ("running", "models", "data"):
            if isinstance(payload.get(key), list):
                return [e for e in payload[key] if isinstance(e, dict)]
        # a bare {model: state} style mapping
        return [{"model": k, "state": v} for k, v in payload.items() if isinstance(v, str)]
    if isinstance(payload, list):
        return [e for e in payload if isinstance(e, dict)]
    return []


def slot_ready(payload, alias: str) -> bool:
    for e in _slot_entries(payload):
        name = e.get("model") or e.get("alias") or e.get("id") or e.get("name")
        state = e.get("state") or e.get("status")
        if name == alias and isinstance(state, str) and state == "ready":
            return True
    return False


def probe_single_slot(endpoint: str, alias: str, timeout: float = PROBE_TIMEOUT_S,
                      mode: str = "running") -> dict:
    """Refuse loudly unless the seat proves ready.

    mode="running": llama-swap's /running must show `alias` in state ready (the fleet law).
    mode="health":  a bare llama.cpp llama-server (ad-hoc candidate probe, 2026-07-18
    addition) has no /running; GET /health must answer HTTP 200 {"status":"ok"}.
    """
    if mode == "health":
        url = probe_base(endpoint) + "/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            raise Refusal(
                f"REFUSING to run — health probe GET {url} failed ({exc!r}); "
                f"cannot prove the candidate server is up."
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            raise Refusal(f"REFUSING to run — health probe {url} returned non-JSON:\n{raw}")
        if payload.get("status") != "ok":
            raise Refusal(
                f"REFUSING to run — health probe {url} not ok (got: {raw})."
            )
        return {"probe_url": url, "raw": payload}
    url = probe_base(endpoint) + "/running"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise Refusal(
            f"REFUSING to run — single-slot probe GET {url} failed ({exc!r}); "
            f"cannot prove the seat is free and ready."
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise Refusal(f"REFUSING to run — single-slot probe {url} returned non-JSON:\n{raw}")
    if not slot_ready(payload, alias):
        raise Refusal(
            f"REFUSING to run — single-slot probe {url} does not show alias "
            f"'{alias}' in state 'ready' (got: {raw}). Nothing else may drive the slot."
        )
    return {"probe_url": url, "raw": payload}


# --- transport ------------------------------------------------------------------------

def call_model(endpoint: str, model: str, system: str, user: str,
               temperature: float, top_p: float, max_tokens: int, timeout: float) -> dict:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def with_transport_retries(fn, retries: int = TRANSPORT_RETRIES):
    """Retry on connection / 5xx errors only (not on a valid-but-bad response).
    Raises TransportAborted after `retries` retries (attempts = retries + 1)."""
    attempts = 0
    last = ""
    while attempts <= retries:
        attempts += 1
        try:
            return fn()
        except urllib.error.HTTPError as exc:
            if exc.code < 500:
                raise  # a 4xx is a request defect, not a transient — surface it
            last = f"HTTP {exc.code}"
        except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            last = repr(exc)
        if attempts <= retries:
            time.sleep(min(2 ** (attempts - 1), 5))
    raise TransportAborted(attempts, last)


# --- vendored checker (repair-loop firing decision — NOT grading) ---------------------

def run_response_checker(dcl_path: Path) -> dict:
    """Run the vendored DCL checker (``harness/dcl/bin/dcl-check.mjs``) over a
    candidate ``.dcl`` file and return its verbatim JSON envelope.

    Used ONLY by --repair-loop to decide whether the first attempt compiled clean
    (and, after a repair, whether the repaired file did). This is not a grade: the
    graded candidate is response.dcl, judged by the task's gate battery. A missing
    node or a non-JSON stdout is a loud Refusal (never silently treated as dirty —
    that would fabricate a repair trigger)."""
    node = shutil.which("node")
    if not node:
        raise Refusal(
            "REFUSING to run --repair-loop — node is required to run the vendored "
            f"checker {DCL_CHECKER}."
        )
    if not DCL_CHECKER.is_file():
        raise Refusal(f"REFUSING to run --repair-loop — missing vendored checker {DCL_CHECKER}")
    proc = subprocess.run(
        [node, str(DCL_CHECKER), str(dcl_path)],
        capture_output=True, text=True, timeout=CHECKER_TIMEOUT_S,
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise Refusal(
            f"REFUSING to continue --repair-loop — checker did not emit JSON "
            f"(exit {proc.returncode}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from exc


def _envelope_clean(envelope: dict) -> bool:
    """The compile-clean predicate the suite uses (G1): ok:true AND errorCount 0."""
    return bool(envelope.get("ok")) and envelope.get("errorCount", 1) == 0


# --- preflight ------------------------------------------------------------------------

def load_task_toml(task_dir: Path) -> dict:
    toml_path = task_dir / "task.toml"
    if not toml_path.is_file():
        raise Refusal(f"REFUSING to run — no task.toml at {toml_path}")
    if tomllib is None:  # pragma: no cover
        raise Refusal("REFUSING to run — tomllib unavailable (need Python 3.11+)")
    try:
        return tomllib.loads(toml_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise Refusal(f"REFUSING to run — task.toml does not parse: {exc}")


def preflight(task_dir: Path, out: Path, endpoint: str, model: str, *,
              repair_loop: bool = False, vocab_ref: Path | None = None) -> tuple[dict, dict]:
    """Refuse loudly on any precondition miss; never degrade. Returns
    (task.toml dict, single-slot probe receipt).

    §10 additive preconditions (only checked when the flags are set, so the
    default preflight is unchanged): --vocab-ref must point to a readable file;
    --repair-loop requires node + the vendored checker present up front (loud,
    before any seat call)."""
    if not task_dir.is_dir():
        raise Refusal(f"REFUSING to run — task-dir does not exist: {task_dir}")

    toml = load_task_toml(task_dir)
    suite = toml.get("task", {}).get("suite")
    if suite != SUITE:
        raise Refusal(
            f"REFUSING to run — task.toml suite is {suite!r}, expected {SUITE!r} "
            f"(wrong suite / wrong task-dir)."
        )

    instruction = task_dir / "instruction.md"
    if not instruction.is_file():
        raise Refusal(f"REFUSING to run — missing instruction.md at {instruction}")
    text = instruction.read_text(encoding="utf-8")
    if not text.strip():
        raise Refusal(f"REFUSING to run — instruction.md is empty at {instruction}")

    # every input/ file the instruction references must exist
    for m in _INPUT_REF.finditer(text):
        rel = m.group(0)
        p = (task_dir / rel).resolve()
        try:
            p.relative_to((task_dir / "input").resolve())
        except ValueError:
            continue
        if not p.is_file():
            raise Refusal(f"REFUSING to run — instruction references missing input {rel}")

    # output dir: writable + empty-or-fresh
    if out.exists():
        if not out.is_dir():
            raise Refusal(f"REFUSING to run — output path exists and is not a directory: {out}")
        if any(out.iterdir()):
            raise Refusal(
                f"REFUSING to run — output dir is not empty: {out} "
                f"(never overwrite another rep's answer sheet — pick a fresh rep dir)."
            )
    else:
        try:
            out.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise Refusal(f"REFUSING to run — cannot create output dir {out}: {exc}")
    probe = _writability_check(out)

    # §10 additive preconditions (only when the flags are set)
    if vocab_ref is not None and not vocab_ref.is_file():
        raise Refusal(f"REFUSING to run — --vocab-ref file does not exist: {vocab_ref}")
    if repair_loop:
        if not shutil.which("node"):
            raise Refusal(
                "REFUSING to run --repair-loop — node is required to run the vendored "
                f"checker {DCL_CHECKER}."
            )
        if not DCL_CHECKER.is_file():
            raise Refusal(f"REFUSING to run --repair-loop — missing vendored checker {DCL_CHECKER}")

    # single-slot law (last, right before the call)
    receipt = probe_single_slot(endpoint, model, mode=probe_mode)
    _ = probe
    return toml, receipt


def _writability_check(out: Path) -> None:
    marker = out / ".writable-probe"
    try:
        marker.write_text("ok", encoding="utf-8")
        marker.unlink()
    except OSError as exc:
        raise Refusal(f"REFUSING to run — output dir not writable {out}: {exc}")


# --- main -----------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="rep output dir (the answer sheet)")
    ap.add_argument("--model", default="qwen36-workhorse", help="served alias (llama-swap :9000)")
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:9000/v1/chat/completions")
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-tokens", type=int, default=16384)
    ap.add_argument("--timeout", type=float, default=None,
                    help="generation timeout (s); default = task.toml timeout_seconds")
    ap.add_argument("--freeze-commit", required=True,
                    help="the frozen dcl-heldout-suite-scope.md commit sha (stamped into config.json)")
    ap.add_argument("--refreeze-commit", default=None,
                    help="OPTIONAL: the §10 re-freeze commit sha (the amendment that set the "
                         "machine-chain authoring protocol of record). Additive — when omitted, "
                         "config.json is byte-identical to the pre-amendment default.")
    # §10 protocol (additive, opt-in — defaults leave behaviour byte-identical)
    ap.add_argument("--vocab-ref", type=Path, default=None,
                    help="append this file (the compiler-verified vocabulary reference) to the "
                         "composed user prompt under a delimiter; prompt_sha256 covers it (§10)")
    ap.add_argument("--probe", choices=["running", "health"], default="running",
                    help="single-slot probe mode: llama-swap /running (default) or bare "
                         "llama-server /health (ad-hoc candidate probes)")
    ap.add_argument("--repair-loop", action="store_true",
                    help="bounded (<=1) compile->repair pass: if attempt 1 compiles dirty, make "
                         "exactly ONE second call carrying the checker's verbatim diagnostics; the "
                         "graded candidate is the FINAL response (§10). The runner still never grades.")
    return ap


def _write_aborted(out: Path, task_id: str, rep: int, abort: TransportAborted) -> None:
    """Write the ABORTED.json for a transport-aborted rep (INVALID, re-run in
    place). Factored so both the first call and the bounded second (repair) call
    write byte-identical abort receipts; no completed sheet is left behind."""
    (out / "ABORTED.json").write_text(json.dumps({
        "task_id": task_id, "rep": rep, "attempts": abort.attempts,
        "error": str(abort), "last": abort.last,
        "disposition": "rep INVALID — re-run in place under the same pinned config; "
                       "never grade a partial sheet",
    }, indent=2), encoding="utf-8")


def _content_of(raw: dict) -> str:
    try:
        return raw["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        return ""


def _finish_of(raw: dict):
    try:
        return raw["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError):
        return None


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    out = args.out.resolve()
    vocab_ref = args.vocab_ref.resolve() if args.vocab_ref is not None else None

    toml, probe_receipt = preflight(task_dir, out, args.endpoint, args.model,
                                    repair_loop=args.repair_loop, vocab_ref=vocab_ref,
                                    probe_mode=args.probe)
    timeout = args.timeout
    if timeout is None:
        timeout = float(toml.get("task", {}).get("timeout_seconds", 900))

    system, user, prompt_sha256 = compose_prompt(task_dir, vocab_ref)

    print(f"[rep {args.rep}] task={task_id} model={args.model} prompt_sha256={prompt_sha256[:12]}")
    t0 = time.time()
    try:
        raw = with_transport_retries(lambda: call_model(
            args.endpoint, args.model, system, user,
            args.temperature, args.top_p, args.max_tokens, timeout))
    except TransportAborted as abort:
        _write_aborted(out, task_id, args.rep, abort)
        print(f"[rep {args.rep}] ABORTED: {abort}", file=sys.stderr)
        return 1
    wall_time = round(time.time() - t0, 2)

    (out / "raw-response.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    content = _content_of(raw)
    finish_reason = _finish_of(raw)
    # response.dcl = the graded candidate, VERBATIM. In default mode this is the
    # sole attempt; under --repair-loop it is the FINAL response (§10). The write
    # is deferred to just before config.json so it always holds the graded bytes.
    final_content = content

    config = {
        "suite": SUITE,
        "task_id": task_id,
        "rep": args.rep,
        "model": args.model,
        "endpoint": args.endpoint,
        "sampling": {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
        },
        "prompt_sha256": prompt_sha256,
        "prompt": {
            "system": system,
            "system_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
            "user_sha256": prompt_sha256,
            "composition": "instruction.md verbatim + referenced input/ files inlined "
                           "in first-appearance order (deterministic)",
        },
        "freeze_commit": args.freeze_commit,
        "wall_time": wall_time,
        **({"refreeze_commit": args.refreeze_commit} if args.refreeze_commit else {}),
        "usage": raw.get("usage"),
        "finish_reason": finish_reason,
        "generation_timeout_s": timeout,
        "transport_retries": TRANSPORT_RETRIES,
        "single_slot_probe": {"url": probe_receipt.get("probe_url"), "ok": True},
        "runner": "harness/run_dcl_heldout.py (never grades; grading = tasks/<task>/test)",
    }
    if finish_reason != "stop":
        config["finish_reason_note"] = (
            f"finish_reason={finish_reason!r} — recorded honestly; still graded. "
            f"finish_reason=='length' is a truncated-generation row FAIL (the token-ceiling "
            f"lesson: 16384 should suffice), distinct from a compile failure."
        )

    # §10 additive: standing vocabulary reference (only recorded when supplied).
    if vocab_ref is not None:
        config["vocab_ref"] = {
            "path": str(vocab_ref),
            "sha256": hashlib.sha256(vocab_ref.read_text(encoding="utf-8").encode("utf-8")).hexdigest(),
        }

    # §10 additive: bounded (<=1) compile->repair pass (only when --repair-loop).
    # The runner runs the checker ONLY to decide whether to fire the ONE second
    # call; it still never grades. The graded candidate is final_content.
    if args.repair_loop:
        # attempt 1 persisted as attempt-1.dcl + its verbatim checker envelope
        attempt1_path = out / "attempt-1.dcl"
        attempt1_path.write_text(content, encoding="utf-8")
        envelope1 = run_response_checker(attempt1_path)
        checker1_json = json.dumps(envelope1, indent=2)
        (out / "attempt-1-checker.json").write_text(checker1_json + "\n", encoding="utf-8")
        zero_shot_clean = _envelope_clean(envelope1)
        repaired_clean = None
        attempts = 1
        if not zero_shot_clean:
            # exactly ONE second call: original composed prompt + attempt 1's
            # response + the checker's verbatim envelope + a terse instruction.
            repair_user = (
                user
                + "\n\n===== YOUR PREVIOUS ATTEMPT (REJECTED BY THE DCL COMPILER) =====\n"
                + content.rstrip("\n")
                + "\n\n===== DCL COMPILER DIAGNOSTICS (VERBATIM) =====\n"
                + checker1_json
                + "\n\n===== INSTRUCTION =====\n"
                + REPAIR_INSTRUCTION
                + "\n"
            )
            # single-slot probe before the SECOND call too (repo law, both attempts)
            probe_single_slot(args.endpoint, args.model, mode=args.probe)
            t1 = time.time()
            try:
                raw2 = with_transport_retries(lambda: call_model(
                    args.endpoint, args.model, system, repair_user,
                    args.temperature, args.top_p, args.max_tokens, timeout))
            except TransportAborted as abort:
                _write_aborted(out, task_id, args.rep, abort)
                print(f"[rep {args.rep}] ABORTED (repair call): {abort}", file=sys.stderr)
                return 1
            config["repair_wall_time"] = round(time.time() - t1, 2)
            (out / "raw-response-2.json").write_text(json.dumps(raw2, indent=2), encoding="utf-8")
            final_content = _content_of(raw2)
            config["repair_finish_reason"] = _finish_of(raw2)
            attempts = 2
        config["repair_loop"] = True
        config["zero_shot_clean"] = zero_shot_clean
        config["repaired_clean"] = repaired_clean  # filled after the final is graded by the checker
        config["attempts"] = attempts

    # response.dcl = the graded candidate (final), written once, VERBATIM.
    (out / "response.dcl").write_text(final_content, encoding="utf-8")

    # If a repair fired, record honestly whether the FINAL landed clean (informational
    # split; the bar does not distinguish zero-shot vs repaired). The checker runs over
    # the just-written response.dcl — still a firing/recording decision, never a grade.
    if args.repair_loop and not config["zero_shot_clean"]:
        envelope2 = run_response_checker(out / "response.dcl")
        (out / "attempt-2-checker.json").write_text(
            json.dumps(envelope2, indent=2) + "\n", encoding="utf-8")
        config["repaired_clean"] = _envelope_clean(envelope2)

    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"[rep {args.rep}] wrote {out / 'response.dcl'} "
          f"({len(final_content)} chars, finish={finish_reason}, {wall_time}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
