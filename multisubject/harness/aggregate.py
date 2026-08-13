#!/usr/bin/env python3
"""Aggregate the deterministic + judge results into a results table.

Lifted from study-tutor ``scripts/eval/aggregate.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``): paths root at ``--run-dir``
(change 1), all tables are n-way over the candidate list (change 2 — the Δ
column appears only for exactly two candidates), a per-subject breakdown is
emitted when judgements carry a ``subject`` field, and the stage records
itself into ``MANIFEST.json`` (change 4). Legacy 2026-05-18 artefacts load
unchanged (``base_scores``/``finetune_scores`` become
``scores: {base, finetune}``).

Deliberate format differences from the published 2026-05-18 table (semantic
equality proven by the golden-master tests): the preamble no longer
hard-codes serving claims (Q4_K_M / llama.cpp — those now live in the
venue's PROTOCOL.md and the run's MANIFEST.json), and column/row labels are
the raw candidate names instead of "Base"/"Fine-tuned" prose.

Input : deterministic.json + judgements.jsonl
Output: results-table.md (and the same content printed to stdout)
"""
from __future__ import annotations

import argparse
import datetime
import json

from harness.common import (
    DIMS, normalise_judgement_rows, read_jsonl, run_path, update_manifest,
)


def render_table(judgements: list[dict], det_summary: dict | None,
                 candidates: list[str]) -> str:
    n = max(len(judgements), 1)
    delta = len(candidates) == 2

    wins = {c: 0 for c in candidates} | {"tie": 0}
    for j in judgements:
        wins[j["winner"]] += 1

    dim_means = {c: {d: sum(j["scores"][c][d] for j in judgements) / n
                     for d in DIMS} for c in candidates}

    cats: dict[str, dict[str, int]] = {}
    subjects: dict[str, dict[str, int]] = {}
    for j in judgements:
        c = cats.setdefault(j.get("category") or "?",
                            {c: 0 for c in candidates} | {"tie": 0})
        c[j["winner"]] += 1
        if j.get("subject"):
            s = subjects.setdefault(j["subject"],
                                    {c: 0 for c in candidates} | {"tie": 0})
            s[j["winner"]] += 1

    out: list[str] = []
    out.append("# Evaluation Results")
    out.append("")
    out.append(
        f"_Generated {datetime.date.today()} — {len(judgements)} golden-set "
        "prompts, blind position-randomised judging; candidates: "
        f"{', '.join(candidates)}. Parity per the venue PROTOCOL.md and this "
        "run's MANIFEST.json: identical system prompt, decoding and "
        "quantisation — the only variable is the weights._"
    )
    out.append("")
    out.append("## Head-to-head — judge preference")
    out.append("")
    out.append("| Outcome | Count | Share |")
    out.append("|---|---|---|")
    for c in candidates:
        out.append(f"| {c} preferred | {wins[c]} | {100 * wins[c] / n:.0f}% |")
    out.append(f"| Tie | {wins['tie']} | {100 * wins['tie'] / n:.0f}% |")
    out.append("")
    out.append("## Mean dimension scores (1–5)")
    out.append("")
    out.append("| Dimension | " + " | ".join(candidates) + (" | Δ |" if delta else " |"))
    out.append("|---" * (len(candidates) + 1 + int(delta)) + "|")
    for d in DIMS:
        cells = [f"{dim_means[c][d]:.2f}" for c in candidates]
        if delta:
            cells.append(
                f"{dim_means[candidates[1]][d] - dim_means[candidates[0]][d]:+.2f}")
        out.append(f"| {d.replace('_', ' ').title()} | " + " | ".join(cells) + " |")
    out.append("")
    out.append("## Win rate by prompt category")
    out.append("")
    out.append("| Category | " + " | ".join(candidates) + " | Tie |")
    out.append("|---" * (len(candidates) + 2) + "|")
    for cat in sorted(cats):
        v = cats[cat]
        out.append(f"| {cat} | " + " | ".join(str(v[c]) for c in candidates)
                   + f" | {v['tie']} |")
    out.append("")
    if subjects:
        out.append("## Win rate by subject")
        out.append("")
        out.append("| Subject | " + " | ".join(candidates) + " | Tie |")
        out.append("|---" * (len(candidates) + 2) + "|")
        for subj in sorted(subjects):
            v = subjects[subj]
            out.append(f"| {subj} | " + " | ".join(str(v[c]) for c in candidates)
                       + f" | {v['tie']} |")
        out.append("")
    if det_summary:
        out.append("## Deterministic checks")
        out.append("")
        out.append("| Metric | " + " | ".join(candidates) + " |")
        out.append("|---" * (len(candidates) + 1) + "|")
        for k, label in [
            ("inline_think_pct", "Inline `<think>` block in output (%)"),
            ("reasoning_present_pct", "Reasoning present, either channel (%)"),
            ("leak_total", "Template-token leaks, visible stream (must be 0)"),
            ("asks_question_pct", "Visible answer contains a question (%)"),
            ("mean_visible_words", "Mean visible-answer length (words)"),
        ]:
            out.append(f"| {label} | "
                       + " | ".join(str(det_summary[c][k]) for c in candidates) + " |")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--deterministic", default=None,
                    help="Override input (default: <run-dir>/deterministic.json).")
    ap.add_argument("--judgements", default=None,
                    help="Override input (default: <run-dir>/judgements.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/results-table.md).")
    args = ap.parse_args(argv)

    det_path = run_path(args.run_dir, args.deterministic, "deterministic.json")
    judgements_path = run_path(args.run_dir, args.judgements, "judgements.jsonl")
    out_path = run_path(args.run_dir, args.out, "results-table.md")

    judgements, candidates = normalise_judgement_rows(read_jsonl(judgements_path))

    det_summary = None
    if det_path.is_file():
        det_summary = json.loads(det_path.read_text(encoding="utf-8"))["summary"]
        # The deterministic summary's key order is the candidates' declared
        # order — prefer it for column ordering when it covers the same set.
        if set(det_summary) == set(candidates):
            candidates = list(det_summary)

    text = render_table(judgements, det_summary, candidates)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(text)

    update_manifest(args.run_dir, "aggregate", {  # change 4
        "judgements": str(judgements_path),
        "deterministic": str(det_path) if det_summary else None,
        "candidates": candidates,
    })
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
