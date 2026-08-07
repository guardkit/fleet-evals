#!/usr/bin/env python3
"""Resolve + aggregate the multi-turn judgements.

Lifted from study-tutor ``scripts/eval/multiturn_resolve.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``); n-way label resolution
(change 2 — the legacy 2026-05-18 ``base_position`` key still resolves),
``--run-dir`` rooting (change 1), MANIFEST stamp (change 4).

``multiturn_raw_judgements.jsonl`` is the judge's committed output — one
object per scenario, against the blind labels:

  {"id": str, "winner": "A"|"B"|...|"tie",
   "A": {socratic_stance, aqa_alignment, scaffolding,
         subject_accuracy, tone, reasoning_visibility},   # ints 1-5
   "B": {... same six keys ...}, ...,
   "rationale": str}

Deliberate format differences from the 2026-05-18 artefacts (semantic
equality proven by the golden-master tests): resolved rows carry
``scores: {candidate: {dims}}`` instead of ``base_scores``/``finetune_scores``,
and the results table's columns are the candidate names.

Run only AFTER multiturn_raw_judgements.jsonl is finalised.
"""
from __future__ import annotations

import argparse
import json

from harness.common import (
    DIMS, positions_from_key, read_jsonl, run_path, update_manifest,
    write_jsonl,
)
from harness.judge.resolve import resolve_rows


def render_table(resolved: list[dict], tally: dict[str, int],
                 candidates: list[str]) -> str:
    n = max(len(resolved), 1)
    dm = {c: {d: sum(r["scores"][c][d] for r in resolved) / n for d in DIMS}
          for c in candidates}

    out = []
    out.append("# Multi-Turn Evaluation Results")
    out.append("")
    out.append(f"_{len(resolved)} scripted multi-turn tutoring scenarios, blind "
               "position-randomised holistic judging. Identical system prompt, "
               "decoding and student script; each candidate built its own side "
               "of the conversation._")
    out.append("")
    out.append("## Head-to-head — judge preference (whole session)")
    out.append("")
    out.append("| Outcome | Count |")
    out.append("|---|---|")
    for c in candidates:
        out.append(f"| {c} preferred | {tally.get(c, 0)} |")
    out.append(f"| Tie | {tally.get('tie', 0)} |")
    out.append("")
    out.append("## Mean dimension scores (1–5)")
    out.append("")
    delta = len(candidates) == 2
    header = "| Dimension | " + " | ".join(candidates) + (" | Δ |" if delta else " |")
    out.append(header)
    out.append("|---" * (len(candidates) + 1 + int(delta)) + "|")
    for d in DIMS:
        cells = [f"{dm[c][d]:.2f}" for c in candidates]
        if delta:
            cells.append(f"{dm[candidates[1]][d] - dm[candidates[0]][d]:+.2f}")
        out.append(f"| {d.replace('_', ' ').title()} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("## Per-scenario verdicts")
    out.append("")
    out.append("| Scenario | Winner | Rationale |")
    out.append("|---|---|---|")
    for r in resolved:
        out.append(f"| {r['id']} | {r['winner']} | {r['rationale']} |")
    out.append("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--raw", default=None,
                    help="Override input (default: <run-dir>/multiturn_raw_judgements.jsonl).")
    ap.add_argument("--key", default=None,
                    help="Override input (default: <run-dir>/multiturn_key.json).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/multiturn_judgements.jsonl).")
    ap.add_argument("--table", default=None,
                    help="Override output (default: <run-dir>/multiturn_results-table.md).")
    args = ap.parse_args(argv)

    raw_path = run_path(args.run_dir, args.raw, "multiturn_raw_judgements.jsonl")
    key_path = run_path(args.run_dir, args.key, "multiturn_key.json")
    out_path = run_path(args.run_dir, args.out, "multiturn_judgements.jsonl")
    table_path = run_path(args.run_dir, args.table, "multiturn_results-table.md")

    key_data = json.loads(key_path.read_text(encoding="utf-8"))
    positions = positions_from_key(key_data)
    raw = read_jsonl(raw_path)

    resolved, tally = resolve_rows(raw, positions)
    # Stable candidate order: from the key when present, else first item.
    candidates = key_data.get("candidates") or list(
        next(iter(positions.values())).values())
    # resolve_rows stamps category "?" for pairless multiturn rows — drop it.
    for r in resolved:
        r.pop("category", None)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_path, resolved)

    text = render_table(resolved, tally, candidates)
    table_path.write_text(text, encoding="utf-8")
    print(text)

    update_manifest(args.run_dir, "multiturn_resolve", {  # change 4
        "raw": str(raw_path),
        "key": str(key_path),
        "tally": tally,
    })
    print("Tally  " + "  ".join(f"{k}={v}" for k, v in tally.items()))
    print(f"Wrote {out_path} and {table_path}")


if __name__ == "__main__":
    main()
