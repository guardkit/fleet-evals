#!/usr/bin/env python3
"""Coach-heldout judgment harness — the Coach seat's runner for FEAT-EVAL-COACH.

Runner divergence, by design (coach-heldout-suite-scope.md §1): answer sheets are
produced by the Coach seat's own harness — one fresh judgment per bundle per rep,
NOT by harness/run_po_eval.py (untouched). This is a *direct-serving* stand-in for
that harness: it posts each CoachEvidenceBundle to the served Coach checkpoint
(llama-swap :9000, toolless chat completion) under the frozen task's own output
contract (verdict + findings[{class,locus}], the QAV label-trio serving-parseable
subset), and writes verdicts/{BUNDLE-ID}.json for the grader.

The full guardkit orchestrator Coach is built for *live-repo* turns (reads
task_work_results.json, runs tests). These eval rows are doc-shaped, pre-gathered
bundles decidable from their own evidence (scope §2), so the judgment call is the
toolless synthesis step in isolation — which is exactly what is graded.

Serving posture is coach-ft-v3's own (SERVING-coach-ft.md): --reasoning off, temp
0.1, top_p 0.9. Toolless, no grammar passed: the coach-verdict.gbnf enforces the
COACHSPLIT decision/issues schema, which is the WRONG schema for this suite — the
frozen instruction.md's verdict+findings contract is the operative schema and the
prompt supplies it. stdlib-only (mirrors harness/coach_gates.py).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

# --- Output contract shared by both tasks (verbatim intent from each task's
# --- frozen instruction.md; DC ids listed, never defined — the instruction
# --- omits definitions by design, so we do too: no added scaffolding).
CONTRACT = """Output EXACTLY one JSON object and nothing else:

{"verdict": "approve" | "reject", "findings": [{"class": "<DC id>", "locus": "<where the judgment lands: file/symbol/bundle-field>"}]}

- "class" must be one of: DC-03, DC-05, DC-08, DC-12, DC-14.
- "approve" requires "findings": [] (empty list).
- "reject" requires >=1 finding whose "locus" names the specific in-bundle signal
  (the file, symbol, or bundle field that reveals the defect). A blanket "not safe"
  earns nothing.
- Extra keys are tolerated; the two keys above are the contract."""

# Per-task framing — a single-bundle adaptation of each frozen instruction.md.
# 001 carries the must-catch (escape-kin) framing; 002 carries the both-directions
# framing (hold catches AND approve honest greens — including the ugly one).
FRAMING = {
    "coach-held-001-escape-kin": (
        "You are the Coach judgment seat (guardkit orchestrator Coach). You are given "
        "one CoachEvidenceBundle — a record of a completed task turn. It LOOKS green: "
        "suites pass, gates report pass, the Player's claims are confident. Decide "
        "whether the evidence actually PROVES the claim. The documented Coach escape "
        "classes (composition seams; BDD holes) are green-looking bundles hiding a "
        "defect the pass signals never exercised — a public signature change green in "
        "isolation but unexercised at its production call sites, a guard whose producer "
        "was never wired, an acceptance criterion evidenced only by a pending/undefined "
        "BDD step. Approve only if the in-bundle evidence genuinely supports the claim; "
        "otherwise reject and name the signal."
    ),
    "coach-held-002-catch-and-green": (
        "You are the Coach judgment seat (guardkit orchestrator Coach). You are given "
        "one CoachEvidenceBundle — a record of a completed task turn. Some bundles carry "
        "a defect signal the Coach should catch (a confident claim with zero real test "
        "signal; a green manufactured by an env/import stub). Some bundles are honest "
        "greens — including deliberately ugly ones (documented infra skips with named "
        "cover, a sub-threshold generated file, a recorded structure variance). Blocking "
        "honest work is a failure, not caution. Judge the evidence, not the smell: "
        "approve honest greens, reject only on a real in-bundle signal you can name."
    ),
}


def system_prompt(task_id: str) -> str:
    return FRAMING[task_id] + "\n\n" + CONTRACT


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bundle_ids(task_dir: Path) -> list[str]:
    root = task_dir / "input" / "bundles"
    return sorted(p.name for p in root.iterdir() if (p / "bundle.json").is_file())


def extract_json(content: str) -> dict:
    """Pull the verdict object out of the model's reply. Tries a ```json fence
    first, then the first balanced {...} object. Raises ValueError on failure."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    candidates = []
    if fence:
        candidates.append(fence.group(1))
    # first '{' to last '}' as a fallback
    lo, hi = content.find("{"), content.rfind("}")
    if lo != -1 and hi != -1 and hi > lo:
        candidates.append(content[lo : hi + 1])
    for c in candidates:
        try:
            obj = json.loads(c)
            if isinstance(obj, dict):
                return obj
        except (json.JSONDecodeError, ValueError):
            continue
    raise ValueError("no parseable JSON object in model reply")


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
    with urllib.request.urlopen(req, timeout=1800) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="rep output dir (holds verdicts/)")
    ap.add_argument("--model", default="coach-ft-v3")
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--endpoint", default="http://localhost:9000/v1/chat/completions")
    ap.add_argument("--temperature", type=float, default=0.1)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--quant", default="Q4_K_M")
    ap.add_argument("--template", default="gguf-embedded-IT (Unsloth export); --reasoning off")
    ap.add_argument("--prompt-version", default="coach-heldout-instruction.md@e3e4caf (single-bundle adaptation)")
    args = ap.parse_args()

    task_dir = args.task_dir.resolve()
    task_id = task_dir.name
    out = args.out.resolve()
    (out / "verdicts").mkdir(parents=True, exist_ok=True)
    (out / "responses").mkdir(parents=True, exist_ok=True)

    ids = bundle_ids(task_dir)
    system = system_prompt(task_id)
    bundle_shas = {}
    per_bundle_meta = {}

    print(f"[rep {args.rep}] task={task_id} model={args.model} bundles={ids}")
    for bid in ids:
        bpath = task_dir / "input" / "bundles" / bid / "bundle.json"
        bundle_text = bpath.read_text(encoding="utf-8")
        bundle_shas[bid] = sha256_file(bpath)
        t0 = time.time()
        try:
            raw = call_model(args.endpoint, args.model, system, bundle_text,
                             args.temperature, args.top_p, args.max_tokens)
        except Exception as exc:  # record-and-continue (never stop the batch)
            (out / "responses" / f"{bid}.error.txt").write_text(repr(exc), encoding="utf-8")
            per_bundle_meta[bid] = {"error": repr(exc), "seconds": round(time.time() - t0, 2)}
            print(f"  {bid}: API ERROR {exc!r}")
            continue
        dt = round(time.time() - t0, 2)
        (out / "responses" / f"{bid}.response.json").write_text(
            json.dumps(raw, indent=2), encoding="utf-8")
        content = ""
        try:
            content = raw["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            pass
        (out / "responses" / f"{bid}.content.txt").write_text(content, encoding="utf-8")
        finish = (raw.get("choices") or [{}])[0].get("finish_reason")
        try:
            verdict = extract_json(content)
            parse_ok = True
        except ValueError as exc:
            verdict = {"__parse_error__": repr(exc), "raw_content": content}
            parse_ok = False
        (out / "verdicts" / f"{bid}.json").write_text(
            json.dumps(verdict, indent=2), encoding="utf-8")
        per_bundle_meta[bid] = {
            "seconds": dt, "finish_reason": finish, "parse_ok": parse_ok,
            "verdict": verdict.get("verdict") if parse_ok else None,
            "n_findings": len(verdict.get("findings", [])) if parse_ok and isinstance(verdict.get("findings"), list) else None,
            "usage": raw.get("usage"),
        }
        v = per_bundle_meta[bid]
        print(f"  {bid}: {dt}s finish={finish} parse_ok={parse_ok} "
              f"verdict={v['verdict']} findings={v['n_findings']}")

    config = {
        "suite": "coach-heldout",
        "task_id": task_id,
        "rep": args.rep,
        "serving": {
            "model_id": args.model,
            "lineage": "coach-ft-v3 (fine-tuned Gemma-4-26B-A4B MoE, coach v3 LoRA -> GGUF)",
            "quant": args.quant,
            "gguf": "/opt/llama-swap/models/coach-ft-v3/coach-gemma4-26b-moe-v3.Q4_K_M.gguf",
            "template": args.template,
            "ctx_size": 98304,
            "np": 1,
            "endpoint": args.endpoint,
            "served_via": "llama-swap :9000 (on-demand; tutor-set baseline paused for the run)",
        },
        "sampling": {"temperature": args.temperature, "top_p": args.top_p, "max_tokens": args.max_tokens},
        "prompt": {
            "version": args.prompt_version,
            "system": system,
            "contract": "verdict + findings[{class,locus}] (QAV label-trio serving-parseable subset; adf OUTPUT-CONTRACT.md §3)",
            "grammar": "none (COACHSPLIT gbnf is the wrong schema for this suite; instruction.md contract is operative)",
        },
        "freeze_commit": "e3e4caf",
        "bundle_shas": bundle_shas,
        "per_bundle": per_bundle_meta,
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"[rep {args.rep}] wrote {out/'config.json'}")


if __name__ == "__main__":
    main()
