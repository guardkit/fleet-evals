#!/usr/bin/env python3
"""qav-heldout runner — the QA-verifier judgment seat's answer-sheet producer.

Runner divergence, by design (ASSUM-013; the run_dcl_heldout.py convention
married to the run_coach_heldout.py bundle loop): answer sheets are produced by
ONE fresh toolless judgment per BUNDLE per rep against the served checkpoint
(llama-swap :9000, chat completion), NOT by harness/run_po_eval.py (untouched)
and NOT by importing another suite's runner. This runner NEVER grades: grading is
the task's gate battery (`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest
tasks/<task>/test -q`), which reads verdicts/{BUNDLE-ID}.json via
harness/qav_gates.py. A bad model verdict is a RESULT, not a retry trigger —
there is no retry-on-bad-content here, and a refusal is loud (nonzero + named),
never a silent degrade.

Why a bundle LOOP and not a single generation (the ASSUM-013 divergence from the
DCL runner): a qav task carries N CoachEvidenceBundles under
input/bundles/{BUNDLE-ID}/bundle.json and the graded artifact is one verdict file
PER bundle (adf OUTPUT-CONTRACT.md §3: verdict + findings[{class, locus}]). Each
bundle is judged in isolation — one bounded call in flight, strictly sequential,
with a fresh single-slot probe BEFORE EVERY seat call (the fleet single-slot law,
re-checked per bundle so nothing else can steal the slot mid-rep).

Pre-flight refuses loudly (never degrades):
  - task-dir must exist; task.toml must parse and declare suite == "qav-heldout";
  - instruction.md must be present and non-empty;
  - every bundle directory under input/bundles/ must carry a bundle.json (and
    there must be at least one bundle);
  - the output dir must be writable and empty-or-fresh (never overwrite another
    rep's answer sheet — a qav-heldout run never reuses another suite's --out);
  - GET <base>/running (or --probe health) must show the target alias ready.

Prompt composition is deterministic per bundle: the task's instruction.md
verbatim + THAT bundle's bundle.json inlined under a stable delimiter, so the
same instruction + same bundle => same bytes => same prompt_sha256 (recorded per
bundle in config.json).

Verdict extraction (never fabricate): a ```json fence first, then the first
balanced {...} object. If NO JSON object is extractable, the raw assistant text
bytes are written to verdicts/{BUNDLE-ID}.json so qav_gates.load_verdict surfaces
the defect honestly (json.loads fails -> __load_error__ -> an "unloadable"
finding). The runner never retries on bad content and never invents a verdict.

Truncation is recorded honestly: finish_reason != "stop" is recorded per bundle
(truncated == finish_reason == "length") and the result is still emitted.

Transport: with_transport_retries retries ONLY URLError/OSError/timeout/
JSONDecodeError/HTTP>=500 (a 4xx is surfaced immediately); TRANSPORT_RETRIES=2
=> up to 3 attempts. On abort the rep writes ABORTED.json (naming the bundle) and
exits 1 with NO config.json — the rep is INVALID (re-run in place), never a
half-written sheet claiming validity.

Serving posture mirrors the coach-heldout bundle-judgment runner
(SERVING-coach-ft.md): temperature 0.1, top_p 0.9, max_tokens 2048, no grammar
(the instruction.md verdict+findings contract is operative). stdlib-only (urllib
etc.) + pytest for the tests. No new dependencies.
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

SUITE = "qav-heldout"

# The pinned seat line. The operative contract (verdict + findings[{class,locus}])
# lives in the task's instruction.md, which is composed verbatim into the user
# turn; this system line only establishes the seat and the "JSON object only"
# posture, so the composed prompt is deterministic. OPEN POINT: the scope doc is
# silent on a system-prompt framing — narrowest reading is one pinned seat line,
# with instruction.md carrying the graded contract.
PINNED_SYSTEM_PROMPT = (
    "You are the QA-verifier judgment seat. Read the task instructions and the "
    "evidence bundle, then output ONLY the verdict JSON object the contract "
    "specifies — no prose, no explanation, no markdown fences."
)

TRANSPORT_RETRIES = 2  # => up to 3 total attempts (1 + 2 retries), then ABORT
PROBE_TIMEOUT_S = 15


class Refusal(SystemExit):
    """A loud, nonzero preflight/slot refusal — never a silent degrade."""


class TransportAborted(RuntimeError):
    def __init__(self, attempts: int, last: str) -> None:
        super().__init__(f"transport aborted after {attempts} attempt(s): {last}")
        self.attempts = attempts
        self.last = last


# --- bundle discovery -----------------------------------------------------------------

def bundle_dirs(task_dir: Path) -> list[Path]:
    """Every subdirectory of input/bundles/, sorted. Unlike
    qav_gates.bundle_ids (which silently skips dirs without a bundle.json), this
    returns ALL bundle dirs so preflight can refuse a dir missing its bundle.json
    loudly instead of silently dropping a row."""
    root = task_dir / "input" / "bundles"
    if not root.is_dir():
        return []
    return sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name)


# --- prompt composition (deterministic, per bundle) -----------------------------------

def compose_prompt(task_dir: Path, bundle_id: str) -> tuple[str, str, str]:
    """Return (system, user, prompt_sha256) for ONE bundle.

    The user turn = the task's instruction.md verbatim, followed by that bundle's
    bundle.json inlined in a clearly delimited block (the model judges from the
    bundle's own evidence). Deterministic: same instruction + same bundle bytes
    => same user bytes => same sha256. prompt_sha256 covers the full user turn."""
    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8")
    bpath = task_dir / "input" / "bundles" / bundle_id / "bundle.json"
    bundle_text = bpath.read_text(encoding="utf-8")
    rel = f"input/bundles/{bundle_id}/bundle.json"
    user = (
        instruction.rstrip("\n")
        + f"\n\n----- BEGIN {rel} -----\n"
        + bundle_text.rstrip("\n")
        + f"\n----- END {rel} -----\n"
    )
    prompt_sha256 = hashlib.sha256(user.encode("utf-8")).hexdigest()
    return PINNED_SYSTEM_PROMPT, user, prompt_sha256


# --- verdict extraction (never fabricate, never retry) --------------------------------

def _first_balanced_object(text: str) -> str | None:
    """The first balanced {...} object in `text`, honoring string literals and
    escapes so a brace inside a JSON string does not miscount depth. Returns None
    when no balanced object is present."""
    start = -1
    depth = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text):
        if start == -1:
            if ch == "{":
                start = i
                depth = 1
            continue
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def extract_json(content: str) -> dict:
    """Pull the verdict object out of the model's reply: a ```json fence first,
    then the first balanced {...} object. Raises ValueError when neither yields a
    JSON object — the caller then writes the raw bytes so the grader surfaces the
    defect honestly (never a fabricated verdict, never a retry)."""
    candidates: list[str] = []
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fence:
        candidates.append(fence.group(1))
    balanced = _first_balanced_object(content)
    if balanced is not None:
        candidates.append(balanced)
    for c in candidates:
        try:
            obj = json.loads(c)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError("no parseable JSON object in model reply")


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
    mode="health":  a bare llama.cpp llama-server has no /running; GET /health must
    answer HTTP 200 {"status":"ok"} (ad-hoc candidate probe)."""
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
            raise Refusal(f"REFUSING to run — health probe {url} not ok (got: {raw}).")
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


def _writability_check(out: Path) -> None:
    marker = out / ".writable-probe"
    try:
        marker.write_text("ok", encoding="utf-8")
        marker.unlink()
    except OSError as exc:
        raise Refusal(f"REFUSING to run — output dir not writable {out}: {exc}")


def preflight(task_dir: Path, out: Path, endpoint: str, model: str, *,
              probe_mode: str = "running") -> tuple[dict, list[str], dict]:
    """Refuse loudly on any precondition miss; never degrade. Returns
    (task.toml dict, sorted bundle ids, single-slot probe receipt)."""
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
    if not instruction.read_text(encoding="utf-8").strip():
        raise Refusal(f"REFUSING to run — instruction.md is empty at {instruction}")

    dirs = bundle_dirs(task_dir)
    if not dirs:
        raise Refusal(
            f"REFUSING to run — no bundle directories under {task_dir / 'input' / 'bundles'}"
        )
    for d in dirs:
        if not (d / "bundle.json").is_file():
            raise Refusal(
                f"REFUSING to run — bundle dir {d.name} is missing bundle.json "
                f"({d / 'bundle.json'})."
            )
    bundle_ids = [d.name for d in dirs]

    # output dir: writable + empty-or-fresh (never overwrite another rep's sheet)
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
    _writability_check(out)

    # single-slot law (last, right before any generation)
    receipt = probe_single_slot(endpoint, model, mode=probe_mode)
    return toml, bundle_ids, receipt


# --- main -----------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="rep output dir (holds verdicts/ + responses/)")
    ap.add_argument("--model", default="qav-ft", help="served alias (llama-swap :9000)")
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--endpoint", default="http://127.0.0.1:9000/v1/chat/completions")
    ap.add_argument("--temperature", type=float, default=0.1)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--timeout", type=float, default=None,
                    help="generation timeout (s); default = task.toml timeout_seconds")
    ap.add_argument("--freeze-commit", required=True,
                    help="the frozen qav-heldout-suite-scope.md commit sha (stamped into config.json; = 2165802)")
    ap.add_argument("--probe", choices=["running", "health"], default="running",
                    help="single-slot probe mode: llama-swap /running (default) or bare "
                         "llama-server /health (ad-hoc candidate probes)")
    return ap


def _write_aborted(out: Path, task_id: str, rep: int, bundle_id: str,
                   abort: TransportAborted) -> None:
    """Write ABORTED.json for a transport-aborted rep (INVALID, re-run in place).
    Names the bundle the abort landed on; no config.json is written, so the rep
    is loudly incomplete rather than a silent partial sheet."""
    (out / "ABORTED.json").write_text(json.dumps({
        "suite": SUITE, "task_id": task_id, "rep": rep, "bundle_id": bundle_id,
        "attempts": abort.attempts, "error": str(abort), "last": abort.last,
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

    toml, bundle_ids, first_receipt = preflight(
        task_dir, out, args.endpoint, args.model, probe_mode=args.probe)
    timeout = args.timeout
    if timeout is None:
        timeout = float(toml.get("task", {}).get("timeout_seconds", 1800))

    (out / "verdicts").mkdir(parents=True, exist_ok=True)
    (out / "responses").mkdir(parents=True, exist_ok=True)

    per_bundle: dict[str, dict] = {}
    probe_receipts: list[dict] = [
        {"bundle_id": None, "url": first_receipt.get("probe_url"), "ok": True, "stage": "preflight"}
    ]

    print(f"[rep {args.rep}] task={task_id} model={args.model} bundles={bundle_ids}")
    for bid in bundle_ids:
        system, user, prompt_sha256 = compose_prompt(task_dir, bid)
        bundle_sha256 = hashlib.sha256(
            (task_dir / "input" / "bundles" / bid / "bundle.json").read_bytes()).hexdigest()

        # fresh single-slot probe BEFORE every seat call (one bounded call in flight)
        receipt = probe_single_slot(args.endpoint, args.model, mode=args.probe)
        probe_receipts.append(
            {"bundle_id": bid, "url": receipt.get("probe_url"), "ok": True, "stage": "per-bundle"})

        t0 = time.time()
        try:
            raw = with_transport_retries(lambda: call_model(
                args.endpoint, args.model, system, user,
                args.temperature, args.top_p, args.max_tokens, timeout))
        except TransportAborted as abort:
            _write_aborted(out, task_id, args.rep, bid, abort)
            print(f"[rep {args.rep}] ABORTED on bundle {bid}: {abort}", file=sys.stderr)
            return 1
        wall_time = round(time.time() - t0, 2)

        (out / "responses" / f"{bid}.raw-response.json").write_text(
            json.dumps(raw, indent=2), encoding="utf-8")

        content = _content_of(raw)
        finish_reason = _finish_of(raw)
        # verdicts/{bid}.json = the extracted JSON object; if none is extractable,
        # the RAW assistant bytes so qav_gates.load_verdict surfaces it honestly.
        try:
            verdict_obj = extract_json(content)
            json_extracted = True
            (out / "verdicts" / f"{bid}.json").write_text(
                json.dumps(verdict_obj, indent=2), encoding="utf-8")
        except ValueError:
            json_extracted = False
            (out / "verdicts" / f"{bid}.json").write_text(content, encoding="utf-8")

        per_bundle[bid] = {
            "bundle_sha256": bundle_sha256,
            "prompt_sha256": prompt_sha256,
            "finish_reason": finish_reason,
            "truncated": finish_reason == "length",
            "json_extracted": json_extracted,
            "usage": raw.get("usage"),
            "wall_time": wall_time,
        }
        if finish_reason != "stop":
            per_bundle[bid]["finish_reason_note"] = (
                f"finish_reason={finish_reason!r} — recorded honestly; still emitted. "
                f"finish_reason=='length' is a truncated generation (the token-ceiling lesson), "
                f"distinct from a well-formed but wrong verdict."
            )
        v = per_bundle[bid]
        print(f"  {bid}: {wall_time}s finish={finish_reason} json_extracted={json_extracted}")

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
        "prompt": {
            "system": PINNED_SYSTEM_PROMPT,
            "system_sha256": hashlib.sha256(PINNED_SYSTEM_PROMPT.encode("utf-8")).hexdigest(),
            "composition": "instruction.md verbatim + that bundle's bundle.json inlined "
                           "under a stable delimiter (deterministic, per bundle)",
            "contract": "verdict + findings[{class,locus}] (adf OUTPUT-CONTRACT.md §3); "
                        "instruction.md is operative",
            "grammar": "none (the instruction.md verdict+findings contract is operative)",
        },
        "freeze_commit": args.freeze_commit,
        "generation_timeout_s": timeout,
        "transport_retries": TRANSPORT_RETRIES,
        "bundles": per_bundle,
        "single_slot_probe": probe_receipts,
        "runner": "harness/run_qav_heldout.py (never grades; grading = tasks/<task>/test)",
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print(f"[rep {args.rep}] wrote {out / 'config.json'} ({len(bundle_ids)} verdicts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
