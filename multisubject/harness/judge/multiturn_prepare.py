#!/usr/bin/env python3
"""Blind-prepare for the multi-turn eval — anonymise the per-scenario
transcripts into labelled sets for holistic session judging.

Lifted from study-tutor ``scripts/eval/multiturn_prepare.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``) with the same treatments as
``prepare.py``: n-way label shuffle (change 2), ``--run-dir`` rooting
(change 1), MANIFEST stamp (change 4).

Writes:
  multiturn_blind.jsonl — {id, text, summary, subject,
                           transcripts: {label: [turns]}}
  multiturn_key.json    — {seed, candidates: [names],
                           positions: {id: {label: candidate}}}
"""
from __future__ import annotations

import argparse
import json
import random

from harness.common import (
    labels_for, normalise_transcript_rows, read_jsonl, run_path,
    update_manifest, write_jsonl,
)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--transcripts", default=None,
                    help="Override input (default: <run-dir>/multiturn_transcripts.jsonl).")
    ap.add_argument("--blind-out", default=None,
                    help="Override output (default: <run-dir>/multiturn_blind.jsonl).")
    ap.add_argument("--key-out", default=None,
                    help="Override output (default: <run-dir>/multiturn_key.json).")
    ap.add_argument("--seed", type=int, default=20260518)
    args = ap.parse_args(argv)

    transcripts_path = run_path(args.run_dir, args.transcripts,
                                "multiturn_transcripts.jsonl")
    blind_path = run_path(args.run_dir, args.blind_out, "multiturn_blind.jsonl")
    key_path = run_path(args.run_dir, args.key_out, "multiturn_key.json")

    random.seed(args.seed)
    rows, candidates = normalise_transcript_rows(read_jsonl(transcripts_path))
    labels = labels_for(len(candidates))

    positions: dict[str, dict[str, str]] = {}
    blind_rows = []
    for r in rows:
        order = list(candidates)
        random.shuffle(order)
        positions[r["id"]] = dict(zip(labels, order))
        blind_rows.append({
            "id": r["id"], "text": r["text"], "summary": r["summary"],
            "subject": r.get("subject"),
            "transcripts": {label: r["transcripts"][cand]
                            for label, cand in positions[r["id"]].items()},
        })

    blind_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(blind_path, blind_rows)
    key_path.write_text(
        json.dumps({"seed": args.seed, "candidates": candidates,
                    "positions": positions}, indent=2),
        encoding="utf-8",
    )

    update_manifest(args.run_dir, "multiturn_prepare", {  # change 4
        "seed": args.seed,
        "candidates": candidates,
        "n_scenarios": len(blind_rows),
    })
    print(f"Wrote {len(blind_rows)} blind scenario sets -> {blind_path}")
    print(f"Wrote label→candidate key -> {key_path}")


if __name__ == "__main__":
    main()
