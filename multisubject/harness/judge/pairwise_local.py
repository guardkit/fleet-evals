#!/usr/bin/env python3
"""Local-model-as-judge: blind pairwise comparison via an OpenAI-compatible
endpoint (llama-swap) — PROTOCOL v2's **Judge B** (registered 2026-08-13:
"amend: subscription + local judges").

Mirrors ``pairwise_api.py`` exactly — same blinding (position randomised per
item under ``--seed``), same per-subject rubric selection, same output row
shape and MANIFEST stamp — but the judge is a locally served model (default
``gpt-oss-120b``: a different model family from both Gemma candidates, so no
family bias, and zero marginal cost). No API key, no network beyond
localhost.

NOTE: performs model inference — never exercised by the hermetic suite;
attended scored-run phase only. Requesting the judge model on llama-swap
evicts other seats; run it batched (this script is one batch) with the
keepalive paused per RUNBOOK-serve-candidates Phase 3.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import time

import httpx

from harness.common import (
    load_rubric, normalise_response_rows, read_jsonl, run_path,
    update_manifest, write_jsonl,
)


def judge(endpoint: str, model: str, rubric: str, item: dict,
          resp_a: str, resp_b: str, *, timeout: float) -> dict:
    user = (
        f"STUDENT MESSAGE:\n{item['prompt']}\n\n"
        f"--- RESPONSE A ---\n{resp_a}\n\n"
        f"--- RESPONSE B ---\n{resp_b}\n"
    )
    payload = {
        "model": model,
        "max_tokens": 700,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": rubric},
            {"role": "user", "content": user},
        ],
    }
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            r = httpx.post(f"{endpoint}/chat/completions", json=payload,
                           timeout=timeout)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"] or ""
            match = re.search(r"```json\s*(.+?)```", text, re.S)
            return json.loads(match.group(1) if match else text)
        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as exc:
            last_err = exc
            time.sleep(5 * attempt)
    raise SystemExit(f"judge call failed after 3 attempts: {last_err!r}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--responses", default=None,
                    help="Override input (default: <run-dir>/responses.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: "
                         "<run-dir>/judgements-local.jsonl).")
    ap.add_argument("--endpoint", default="http://localhost:9000/v1")
    ap.add_argument("--model", default="gpt-oss-120b",
                    help="Judge model id on the endpoint (PROTOCOL v2 Judge B "
                         "default: gpt-oss-120b — not a Gemma).")
    ap.add_argument("--seed", type=int, default=20260518,
                    help="Seeds the A/B position randomisation.")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--allow-draft-rubrics", action="store_true",
                    help="Permit STATUS: DRAFT rubrics (dry runs only).")
    args = ap.parse_args(argv)

    responses_path = run_path(args.run_dir, args.responses, "responses.jsonl")
    out_path = run_path(args.run_dir, args.out, "judgements-local.jsonl")

    random.seed(args.seed)
    rows, candidates = normalise_response_rows(read_jsonl(responses_path))
    if len(candidates) != 2:
        raise SystemExit(
            f"pairwise judging needs exactly 2 candidates, got {candidates}.")
    c1, c2 = candidates

    rubrics: dict[str, str] = {}
    tally = {c1: 0, c2: 0, "tie": 0}
    resolved = []
    for i, r in enumerate(rows, 1):
        subject = r.get("subject") or "english"
        if subject not in rubrics:
            rubrics[subject] = load_rubric(
                subject, allow_draft=args.allow_draft_rubrics)

        c1_is_a = random.random() < 0.5
        positions = {"A": c1, "B": c2} if c1_is_a else {"A": c2, "B": c1}
        resp_a = r["responses"][positions["A"]]["visible"]
        resp_b = r["responses"][positions["B"]]["visible"]

        verdict = judge(args.endpoint, args.model, rubrics[subject], r,
                        resp_a, resp_b, timeout=args.timeout)

        w = verdict["winner"]
        winner = "tie" if w == "tie" else positions[w]
        tally[winner] += 1

        resolved.append({
            "id": r["id"],
            "category": r.get("category"),
            "subject": subject,
            "positions": positions,
            "winner": winner,
            "scores": {cand: verdict[label]
                       for label, cand in positions.items()},
            "rationale": verdict.get("rationale", ""),
        })
        print(f"[{i}/{len(rows)}] {r['id']:<24} winner={winner}", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_path, resolved)

    update_manifest(args.run_dir, "judge_local", {
        "judge_model": args.model,
        "endpoint": args.endpoint,
        "seed": args.seed,
        "candidates": candidates,
        "subjects": sorted(rubrics),
        "tally": tally,
    })
    print("\nTally  " + "  ".join(f"{k}={v}" for k, v in tally.items()))
    print(f"Wrote {len(resolved)} judgements -> {out_path}")


if __name__ == "__main__":
    main()
