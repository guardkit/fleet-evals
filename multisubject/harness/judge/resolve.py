#!/usr/bin/env python3
"""Resolve step: apply the blind key to raw labelled judgements, producing
the final ``judgements.jsonl`` that ``aggregate.py`` consumes.

Lifted from study-tutor ``scripts/eval/judge_resolve.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``); label→candidate resolution is
n-way (change 2), paths root at ``--run-dir`` (change 1), and the tally is
recorded into ``MANIFEST.json`` (change 4). The legacy 2026-05-18 two-way
key (``{"base_position": {id: "A"|"B"}}``) still resolves — its candidates
are named ``base``/``finetune``.

``raw_judgements.jsonl`` is the judge's committed output — one object per
line, written against the *blind* labels:

  {"id": str,
   "winner": "A" | "B" | ... | "tie",
   "A": {socratic_stance, aqa_alignment, scaffolding,
         subject_accuracy, tone, reasoning_visibility},   # ints 1-5
   "B": {... same six keys ...}, ...,
   "rationale": str}

Output rows (n-way shape — deliberate format difference from 2026-05-18,
which used base_position/base_scores/finetune_scores; the golden-master
tests prove semantic equality against the published artefacts):

  {"id", "category", "positions": {label: candidate},
   "winner": candidate-name | "tie", "scores": {candidate: {dims}},
   "rationale"}

Run it only AFTER ``raw_judgements.jsonl`` is finalised.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness.common import (
    DIMS, positions_from_key, read_jsonl, run_path, update_manifest,
    write_jsonl,
)


def resolve_rows(raw: list[dict], positions: dict[str, dict[str, str]],
                 categories: dict[str, str] | None = None,
                 subjects: dict[str, str] | None = None,
                 dims: list[str] | None = None,
                 ) -> tuple[list[dict], dict[str, int]]:
    """Map blind labels back to candidate names; validate every judging
    dimension on every labelled response (SystemExit on any missing).
    ``dims`` defaults to the single-turn six; multi-turn passes MT_DIMS
    (the six + engagement_elicitation, PROTOCOL v3)."""
    dims = dims or DIMS
    categories = categories or {}
    subjects = subjects or {}
    tally: dict[str, int] = {"tie": 0}
    resolved = []
    for j in raw:
        if j["id"] not in positions:
            raise SystemExit(f"{j['id']}: not present in blind key")
        pos = positions[j["id"]]  # {label: candidate}
        for label in pos:
            missing = [d for d in dims if d not in j.get(label, {})]
            if missing:
                raise SystemExit(f"{j['id']}: response {label} missing {missing}")

        w = j["winner"]
        if w == "tie":
            winner = "tie"
        elif w in pos:
            winner = pos[w]
        else:
            raise SystemExit(f"{j['id']}: winner '{w}' is not a blind label {list(pos)}")
        for cand in pos.values():
            tally.setdefault(cand, 0)
        tally[winner] = tally.get(winner, 0) + 1

        row = {
            "id": j["id"],
            "category": categories.get(j["id"], "?"),
            "positions": pos,
            "winner": winner,
            "scores": {cand: j[label] for label, cand in pos.items()},
            "rationale": j.get("rationale", ""),
        }
        if subjects.get(j["id"]):
            row["subject"] = subjects[j["id"]]
        resolved.append(row)
    return resolved, tally


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--raw", default=None,
                    help="Override input (default: <run-dir>/raw_judgements.jsonl).")
    ap.add_argument("--key", default=None,
                    help="Override input (default: <run-dir>/blind_key.json).")
    ap.add_argument("--pairs", default=None,
                    help="Override input (default: <run-dir>/blind_pairs.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/judgements.jsonl).")
    args = ap.parse_args(argv)

    raw_path = run_path(args.run_dir, args.raw, "raw_judgements.jsonl")
    key_path = run_path(args.run_dir, args.key, "blind_key.json")
    pairs_path = run_path(args.run_dir, args.pairs, "blind_pairs.jsonl")
    out_path = run_path(args.run_dir, args.out, "judgements.jsonl")

    positions = positions_from_key(
        json.loads(key_path.read_text(encoding="utf-8")))
    categories: dict[str, str] = {}
    subjects: dict[str, str] = {}
    if Path(pairs_path).is_file():
        for r in read_jsonl(pairs_path):
            categories[r["id"]] = r.get("category") or "?"
            if r.get("subject"):
                subjects[r["id"]] = r["subject"]
    raw = read_jsonl(raw_path)

    resolved, tally = resolve_rows(raw, positions, categories, subjects)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_path, resolved)

    update_manifest(args.run_dir, "judge_resolve", {  # change 4
        "raw": str(raw_path),
        "key": str(key_path),
        "tally": tally,
    })
    print(f"Resolved {len(raw)} judgements -> {out_path}")
    print("Tally  " + "  ".join(f"{k}={v}" for k, v in tally.items()))


if __name__ == "__main__":
    main()
