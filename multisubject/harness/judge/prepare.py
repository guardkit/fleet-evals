#!/usr/bin/env python3
"""Blind-prepare step: turn ``responses.jsonl`` into anonymised labelled
items for a judge that must not know which candidate produced which
response.

Lifted from study-tutor ``scripts/eval/judge_prepare.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``); the two-way A/B coin flip is
generalised to an n-way per-item shuffle of the candidate order (change 2),
paths root at ``--run-dir`` (change 1), and the stage records its seed into
``MANIFEST.json`` (change 4).

Splitting *blinding* from *judging* keeps the eval judge-agnostic — the
judge may be an agent session, a human, or the automated API path in
``pairwise_api.py``. Whoever judges sees only "Response A" / "Response B"
(/ "C" ...); the label→candidate mapping is held in a separate key file and
applied afterwards by ``resolve.py``.

Writes:
  blind_pairs.jsonl — {id, category, subject, prompt, expected_behaviours,
                       red_flags, responses: {label: {visible, reasoning}}}
                      (NO candidate names anywhere)
  blind_key.json    — {seed, candidates: [names],
                       positions: {id: {label: candidate}}}
"""
from __future__ import annotations

import argparse
import json
import random
import re

from harness.common import (
    labels_for, normalise_response_rows, read_jsonl, run_path,
    update_manifest, write_jsonl,
)


def channels(side: dict) -> dict:
    """The judge sees the visible answer plus the model's reasoning —
    the reasoning may be inline ``<think>`` or the ``reasoning_content``
    channel, so prefer whichever is populated."""
    content = side.get("content", "")
    reasoning = side.get("reasoning_content", "").strip()
    if not reasoning and "<think>" in content:
        m = re.search(r"<think>(.*?)</think>", content, re.S)
        reasoning = m.group(1).strip() if m else ""
    return {"visible": side.get("visible", content), "reasoning": reasoning}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--responses", default=None,
                    help="Override input (default: <run-dir>/responses.jsonl).")
    ap.add_argument("--pairs-out", default=None,
                    help="Override output (default: <run-dir>/blind_pairs.jsonl).")
    ap.add_argument("--key-out", default=None,
                    help="Override output (default: <run-dir>/blind_key.json).")
    ap.add_argument("--seed", type=int, default=20260518,
                    help="Seeds the label shuffle — keep fixed across re-runs.")
    args = ap.parse_args(argv)

    responses_path = run_path(args.run_dir, args.responses, "responses.jsonl")
    pairs_path = run_path(args.run_dir, args.pairs_out, "blind_pairs.jsonl")
    key_path = run_path(args.run_dir, args.key_out, "blind_key.json")

    random.seed(args.seed)
    rows, candidates = normalise_response_rows(read_jsonl(responses_path))
    labels = labels_for(len(candidates))

    positions: dict[str, dict[str, str]] = {}
    blind_rows = []
    for r in rows:
        order = list(candidates)
        random.shuffle(order)
        positions[r["id"]] = dict(zip(labels, order))
        blind_rows.append({
            "id": r["id"],
            "category": r.get("category"),
            "subject": r.get("subject"),
            "prompt": r["prompt"],
            "expected_behaviours": r.get("expected_behaviours", []),
            "red_flags": r.get("red_flags", []),
            "responses": {
                label: channels(r["responses"][cand])
                for label, cand in positions[r["id"]].items()
            },
        })

    pairs_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(pairs_path, blind_rows)
    key_path.write_text(
        json.dumps({"seed": args.seed, "candidates": candidates,
                    "positions": positions}, indent=2),
        encoding="utf-8",
    )

    update_manifest(args.run_dir, "judge_prepare", {  # change 4
        "seed": args.seed,
        "candidates": candidates,
        "n_items": len(blind_rows),
    })
    print(f"Wrote {len(blind_rows)} blind items -> {pairs_path}")
    print(f"Wrote label→candidate key -> {key_path}")
    print("The judge must commit raw_judgements.jsonl BEFORE the key is applied.")


if __name__ == "__main__":
    main()
