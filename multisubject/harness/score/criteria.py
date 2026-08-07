#!/usr/bin/env python3
"""Criterion-referenced scoring — length-neutral.

Lifted from study-tutor ``scripts/eval/score_criteria.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``): paths root at ``--run-dir``
(change 1), scoring generalises to any candidate set (change 2 — the
2026-05-18 files load unchanged, their ``base``/``finetune`` keys are the
candidate names), MANIFEST stamp (change 4). Producing
``criteria_judgements.jsonl`` automatically (2026-05-18 required fix #7) is
still an open lift — today the file is hand/agent-authored.

The pairwise LLM-as-judge eval rewards longer, more 'thorough-looking'
responses — a well-documented bias. This scorer removes that: each response
is scored ONLY against its own item's ``expected_behaviours`` (met = 1.0 /
partial = 0.5 / not = 0.0) and ``red_flags`` (tripped = 1). There is no
comparison between candidates, so a concise response that satisfies every
expected behaviour scores 100% regardless of length.

Input : criteria_judgements.jsonl — one object per golden-set item:
  {"id": str, "category": str,
   "<candidate>": {"behaviours": [1|0.5|0, ...], "red_flags": [1|0, ...]},
   ... one key per candidate ...}
  The lists align positionally with the golden set's expected_behaviours
  and red_flags for that item.
Output: criteria_results-table.md
"""
from __future__ import annotations

import argparse

from harness.common import read_jsonl, run_path, update_manifest

_META_KEYS = {"id", "category", "subject"}


def candidate_names(rows: list[dict]) -> list[str]:
    names = [k for k in rows[0] if k not in _META_KEYS]
    for r in rows:
        if {k for k in r if k not in _META_KEYS} != set(names):
            raise SystemExit(f"row {r.get('id')}: candidate keys differ from {names}")
    return names


def aggregate(rows: list[dict], candidate: str) -> dict:
    beh_sum = beh_tot = rf_trip = rf_tot = 0.0
    clean = 0
    per = []
    for r in rows:
        m = r[candidate]
        b, rf = m["behaviours"], m["red_flags"]
        beh_sum += sum(b)
        beh_tot += len(b)
        rf_trip += sum(rf)
        rf_tot += len(rf)
        item_clean = sum(b) == len(b) and sum(rf) == 0
        clean += int(item_clean)
        per.append({"id": r["id"], "category": r["category"],
                    "behaviour_frac": round(sum(b) / max(len(b), 1), 2),
                    "red_flags": int(sum(rf))})
    return {
        "n": len(rows),
        "behaviour_pct": round(100 * beh_sum / max(beh_tot, 1), 1),
        "red_flags_tripped": int(rf_trip),
        "red_flag_total": int(rf_tot),
        "clean_items": clean,
        "per": per,
    }


def render_table(rows: list[dict], candidates: list[str]) -> str:
    agg = {c: aggregate(rows, c) for c in candidates}
    n = agg[candidates[0]]["n"]

    out = []
    out.append("# Criterion-Referenced Results")
    out.append("")
    out.append(f"_{n} golden-set prompts. Each response scored only against "
               "its own `expected_behaviours` and `red_flags` — length-neutral, "
               "no candidate-vs-candidate comparison, so verbosity cannot "
               "inflate a score._")
    out.append("")
    out.append("| Metric | " + " | ".join(candidates) + " |")
    out.append("|---" * (len(candidates) + 1) + "|")
    out.append("| Expected behaviours met (%) | "
               + " | ".join(str(agg[c]["behaviour_pct"]) for c in candidates) + " |")
    out.append("| Red flags tripped | "
               + " | ".join(f"{agg[c]['red_flags_tripped']} / {agg[c]['red_flag_total']}"
                            for c in candidates) + " |")
    out.append("| Clean items (all behaviours, no red flag) | "
               + " | ".join(f"{agg[c]['clean_items']} / {agg[c]['n']}"
                            for c in candidates) + " |")
    out.append("")
    out.append("## Per-item behaviour fraction (red flags in brackets)")
    out.append("")
    out.append("| Item | " + " | ".join(candidates) + " |")
    out.append("|---" * (len(candidates) + 1) + "|")
    per = {c: {p["id"]: p for p in agg[c]["per"]} for c in candidates}
    for r in rows:
        cells = []
        for c in candidates:
            p = per[c][r["id"]]
            cells.append(f"{p['behaviour_frac']:.2f}"
                         + (f" ⚑{p['red_flags']}" if p["red_flags"] else ""))
        out.append(f"| {r['id']} | " + " | ".join(cells) + " |")
    out.append("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--judgements", default=None,
                    help="Override input (default: <run-dir>/criteria_judgements.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/criteria_results-table.md).")
    args = ap.parse_args(argv)

    judgements_path = run_path(args.run_dir, args.judgements,
                               "criteria_judgements.jsonl")
    out_path = run_path(args.run_dir, args.out, "criteria_results-table.md")

    rows = read_jsonl(judgements_path)
    candidates = candidate_names(rows)

    text = render_table(rows, candidates)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)

    update_manifest(args.run_dir, "score_criteria", {  # change 4
        "judgements": str(judgements_path),
        "candidates": candidates,
    })
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
