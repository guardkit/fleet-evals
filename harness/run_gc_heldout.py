#!/usr/bin/env python3
"""gc-heldout runner — the general-capability seat's answer-sheet producer.

Runner divergence, by design (ASSUM-013, the run_coach_heldout.py precedent):
answer sheets are produced by one fresh generation per pinned row per rep
against the served checkpoint (llama-swap, toolless chat completion), NOT by
harness/run_po_eval.py (untouched). This runner NEVER grades: grading is the
task's gate battery (`PO_EVAL_OUTPUT_DIR=<rep-dir> pytest tasks/<task>/test -q`),
which executes candidate programs against the benchmarks' reference assertions
inside the gc sandbox.

Pre-flight refuses loudly (never degrades):
  - sandbox isolation must prove itself (gc_sandbox.ensure_available)
  - content pins must verify (a drifted row blocks before any model call)
  - the output directory must not hold another suite's records (qav §5 rule)

Transport: 2 retries per model call, then the REP ABORTS with ABORTED.json
written (INVALID, not a failure — re-run in place; no fabricated or empty
response is ever graded).

stdlib-only (mirrors harness/gc_gates.py).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import gc_gates, gc_rows, gc_sandbox  # noqa: E402


def call_model(endpoint: str, model: str, system: str, user: str,
               temperature: float, top_p: float, max_tokens: int) -> dict:
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
        endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=gc_gates.GENERATION_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="rep output dir (the answer sheet)")
    ap.add_argument("--model", required=True, help="served model id (llama-swap handle)")
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--endpoint", default="http://localhost:9000/v1/chat/completions")
    ap.add_argument("--temperature", type=float, default=0.1)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--base-family", required=True,
                    help="base model family (matching-family rule key half 1)")
    ap.add_argument("--quant", required=True,
                    help="quant family, e.g. Q4_K_XL (matching-family rule key half 2)")
    ap.add_argument("--lineage", default="", help="candidate lineage note for the record")
    ap.add_argument("--template", default="gguf-embedded chat template")
    ap.add_argument("--prompt-version",
                    default="gc-heldout instruction.md @ FEAT-EVAL-GC build (PROPOSED — pre-freeze)")
    args = ap.parse_args()

    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    out = args.out.resolve()

    # --- Pre-flight: refuse loudly, never degrade -----------------------------------
    gc_sandbox.ensure_available()
    pin_findings = gc_gates.verify_pins(task_dir)
    if pin_findings:
        sys.exit(f"REFUSING to run — content pins broken (grading would be meaningless): "
                 f"{pin_findings}")
    ownership = gc_gates.output_dir_findings(out) if out.exists() else []
    if ownership:
        sys.exit(f"REFUSING to run — {ownership}")

    (out / "programs").mkdir(parents=True, exist_ok=True)
    (out / "responses").mkdir(parents=True, exist_ok=True)
    (out / "rows").mkdir(parents=True, exist_ok=True)

    manifest = gc_rows.load_manifest(task_dir)
    row_shas = {e["row_id"]: e["sha256"] for e in manifest["rows"]}
    per_row_meta: dict[str, dict] = {}

    print(f"[rep {args.rep}] task={task_id} model={args.model} rows={len(row_shas)}")
    for row_id in gc_rows.manifest_row_ids(task_dir):
        row = gc_rows.load_row(task_dir, row_id)
        user = gc_rows.user_prompt(row)
        t0 = time.time()
        try:
            raw = gc_gates.with_transport_retries(lambda: call_model(
                args.endpoint, args.model, gc_rows.PINNED_SYSTEM_PROMPT, user,
                args.temperature, args.top_p, args.max_tokens))
        except gc_gates.TransportAborted as abort:
            (out / "ABORTED.json").write_bytes(gc_rows.canonical_json_bytes({
                "task_id": task_id, "rep": args.rep, "row_id": row_id,
                "attempts": abort.attempts, "error": str(abort),
                "disposition": "rep INVALID — re-run in place under the same pinned "
                               "config; never grade a partial sheet",
            }))
            sys.exit(f"[rep {args.rep}] ABORTED at {row_id}: {abort}")
        seconds = round(time.time() - t0, 2)

        (out / "responses" / f"{row_id}.response.json").write_text(
            json.dumps(raw, indent=2), encoding="utf-8")
        content = ""
        try:
            content = raw["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            pass
        (out / "responses" / f"{row_id}.content.txt").write_text(content, encoding="utf-8")
        finish = (raw.get("choices") or [{}])[0].get("finish_reason")

        diagnostic: dict = {}
        extracted = False
        try:
            program = gc_gates.extract_program(content)
            (out / "programs" / f"{row_id}.py").write_text(program, encoding="utf-8")
            extracted = True
        except gc_gates.ExtractionError as exc:
            diagnostic["extraction"] = str(exc)
        if finish == "length":
            diagnostic["finish_reason"] = "length"
        if diagnostic:
            (out / "rows" / f"{row_id}.json").write_bytes(
                gc_rows.canonical_json_bytes(diagnostic))

        per_row_meta[row_id] = {
            "seconds": seconds, "finish_reason": finish, "extracted": extracted,
            "prompt_hashes": gc_rows.prompt_hashes(row), "usage": raw.get("usage"),
        }
        print(f"  {row_id}: {seconds}s finish={finish} extracted={extracted}")

    (out / "candidate.json").write_bytes(gc_rows.canonical_json_bytes({
        "model_id": args.model,
        "lineage": args.lineage,
        "base_family": args.base_family,
        "quant": args.quant,
    }))
    (out / "config.json").write_bytes(gc_rows.canonical_json_bytes({
        "suite": gc_gates.SUITE,
        "task_id": task_id,
        "rep": args.rep,
        "serving": {
            "model_id": args.model,
            "lineage": args.lineage,
            "base_family": args.base_family,
            "quant": args.quant,
            "template": args.template,
            "endpoint": args.endpoint,
            "served_via": "llama-swap :9000 (on-demand)",
        },
        "sampling": {"temperature": args.temperature, "top_p": args.top_p,
                     "max_tokens": args.max_tokens},
        "prompt": {
            "version": args.prompt_version,
            "system": gc_rows.PINNED_SYSTEM_PROMPT,
            "system_sha256": gc_rows.sha256_text(gc_rows.PINNED_SYSTEM_PROMPT),
            "convention": "ASSUM-009: HumanEval signature+docstring completion; MBPP "
                          "problem text + reference asserts verbatim; one fenced block out",
        },
        "freeze_commit": "PROPOSED — gc-heldout-suite-scope.md not yet frozen; "
                         "record the freeze sha here once Rich freezes by commit",
        "transport_retries": gc_gates.TRANSPORT_RETRIES,
        "generation_timeout_s": gc_gates.GENERATION_TIMEOUT_S,
        "row_shas": row_shas,
        "per_row": per_row_meta,
    }))
    print(f"[rep {args.rep}] wrote {out / 'config.json'}")


if __name__ == "__main__":
    main()
