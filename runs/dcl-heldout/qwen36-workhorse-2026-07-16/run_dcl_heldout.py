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


def compose_prompt(task_dir: Path) -> tuple[str, str, str]:
    """Return (system, user, prompt_sha256).

    The user turn = the task's instruction.md verbatim, followed by each
    input/ file it references inlined in a clearly delimited, order-stable block
    (the model cannot follow file links; the spike embedded its inputs inline).
    Deterministic: same instruction + same inputs => same bytes => same sha256."""
    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8")
    parts = [instruction.rstrip("\n")]
    for path in referenced_inputs(instruction, task_dir):
        rel = path.relative_to(task_dir).as_posix()
        body = path.read_text(encoding="utf-8").rstrip("\n")
        parts.append(f"\n\n----- BEGIN {rel} -----\n{body}\n----- END {rel} -----")
    user = "".join(parts) + "\n"
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


def probe_single_slot(endpoint: str, alias: str, timeout: float = PROBE_TIMEOUT_S) -> dict:
    """Refuse loudly unless <base>/running shows `alias` in state `ready`."""
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


def preflight(task_dir: Path, out: Path, endpoint: str, model: str) -> tuple[dict, dict]:
    """Refuse loudly on any precondition miss; never degrade. Returns
    (task.toml dict, single-slot probe receipt)."""
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

    # single-slot law (last, right before the call)
    receipt = probe_single_slot(endpoint, model)
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
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    out = args.out.resolve()

    toml, probe_receipt = preflight(task_dir, out, args.endpoint, args.model)
    timeout = args.timeout
    if timeout is None:
        timeout = float(toml.get("task", {}).get("timeout_seconds", 900))

    system, user, prompt_sha256 = compose_prompt(task_dir)

    print(f"[rep {args.rep}] task={task_id} model={args.model} prompt_sha256={prompt_sha256[:12]}")
    t0 = time.time()
    try:
        raw = with_transport_retries(lambda: call_model(
            args.endpoint, args.model, system, user,
            args.temperature, args.top_p, args.max_tokens, timeout))
    except TransportAborted as abort:
        (out / "ABORTED.json").write_text(json.dumps({
            "task_id": task_id, "rep": args.rep, "attempts": abort.attempts,
            "error": str(abort), "last": abort.last,
            "disposition": "rep INVALID — re-run in place under the same pinned config; "
                           "never grade a partial sheet",
        }, indent=2), encoding="utf-8")
        print(f"[rep {args.rep}] ABORTED: {abort}", file=sys.stderr)
        return 1
    wall_time = round(time.time() - t0, 2)

    (out / "raw-response.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    content = ""
    try:
        content = raw["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        content = ""
    # response.dcl = the assistant message content VERBATIM, byte-for-byte.
    (out / "response.dcl").write_text(content, encoding="utf-8")

    finish_reason = None
    try:
        finish_reason = raw["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError):
        finish_reason = None

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
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"[rep {args.rep}] wrote {out / 'response.dcl'} "
          f"({len(content)} chars, finish={finish_reason}, {wall_time}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
