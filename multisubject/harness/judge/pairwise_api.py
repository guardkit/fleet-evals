#!/usr/bin/env python3
"""Claude-as-judge: blind pairwise comparison of two candidates' responses
via the Anthropic API (prepare→judge→resolve in one shot).

Lifted from study-tutor ``scripts/eval/judge_pairwise.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``): paths root at ``--run-dir``
(change 1), candidates come from the responses file rather than hard-coded
base/finetune names (change 2 — but the pairwise protocol itself is
two-way: this script refuses >2 candidates; n-way round-robin judging is
future work), the rubric is selected per item from
``harness/rubrics/<subject>.md`` instead of a hard-coded English rubric
(change 3), and the judge model + seed are recorded into ``MANIFEST.json``
(change 4).

Bias controls built in:

* **Blind** — the judge is shown "Response A" / "Response B" and is never
  told which candidate produced which.
* **Position-randomised** — per item the candidate→label assignment is
  randomised (deterministically, via ``--seed``) so any positional
  preference of the judge averages out across the set.

Each rubric is sent as a ``cache_control`` system block so it is written to
the Anthropic prompt cache once per subject and re-read on every item.

Requires: ``ANTHROPIC_API_KEY`` in the environment and the ``api-judge``
extra (``uv sync --extra api-judge``). NOTE: this script performs model
inference — it is never exercised by the hermetic test suite and belongs to
the attended, scored-run phase only.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re

from harness.common import (
    load_rubric, normalise_response_rows, read_jsonl, run_path,
    update_manifest, write_jsonl,
)


def judge(client, model: str, rubric: str, item: dict,
          resp_a: str, resp_b: str) -> dict:
    user = (
        f"STUDENT MESSAGE:\n{item['prompt']}\n\n"
        f"--- RESPONSE A ---\n{resp_a}\n\n"
        f"--- RESPONSE B ---\n{resp_b}\n"
    )
    msg = client.messages.create(
        model=model,
        max_tokens=700,
        temperature=0,
        system=[{"type": "text", "text": rubric,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    match = re.search(r"```json\s*(.+?)```", text, re.S)
    return json.loads(match.group(1) if match else text)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--responses", default=None,
                    help="Override input (default: <run-dir>/responses.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/judgements.jsonl).")
    ap.add_argument("--model", default="claude-opus-4-7",
                    help="Judge model. claude-sonnet-4-6 is fine for a dry run.")
    ap.add_argument("--seed", type=int, default=20260518,
                    help="Seeds the A/B position randomisation — keep it fixed "
                         "across re-runs for reproducibility.")
    ap.add_argument("--allow-draft-rubrics", action="store_true",
                    help="Permit STATUS: DRAFT rubrics (dry runs only — a stub "
                         "rubric must never drive a scored run).")
    args = ap.parse_args(argv)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set.")
    import anthropic  # optional extra [api-judge]

    responses_path = run_path(args.run_dir, args.responses, "responses.jsonl")
    out_path = run_path(args.run_dir, args.out, "judgements.jsonl")

    random.seed(args.seed)
    client = anthropic.Anthropic()
    rows, candidates = normalise_response_rows(read_jsonl(responses_path))
    if len(candidates) != 2:
        raise SystemExit(
            f"pairwise judging needs exactly 2 candidates, got {candidates} — "
            "n-way round-robin judging is not implemented yet."
        )
    c1, c2 = candidates

    # Change 3 — rubric per item subject, loaded once per subject.
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
        # Judge the VISIBLE answer (content with any <think> block stripped)
        # so neither candidate is flattered by where it reasons.
        resp_a = r["responses"][positions["A"]]["visible"]
        resp_b = r["responses"][positions["B"]]["visible"]

        verdict = judge(client, args.model, rubrics[subject], r, resp_a, resp_b)

        w = verdict["winner"]
        winner = "tie" if w == "tie" else positions[w]
        tally[winner] += 1

        resolved.append({
            "id": r["id"],
            "category": r.get("category"),
            "subject": subject,
            "positions": positions,
            "winner": winner,
            "scores": {cand: verdict[label] for label, cand in positions.items()},
            "rationale": verdict.get("rationale", ""),
        })
        print(f"[{i}/{len(rows)}] {r['id']:<20} winner={winner}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_path, resolved)

    update_manifest(args.run_dir, "judge_api", {  # change 4
        "judge_model": args.model,
        "seed": args.seed,
        "candidates": candidates,
        "subjects": sorted(rubrics),
        "tally": tally,
    })
    print("\nTally  " + "  ".join(f"{k}={v}" for k, v in tally.items()))
    print(f"Wrote {len(resolved)} judgements -> {out_path}")


if __name__ == "__main__":
    main()
