#!/usr/bin/env python3
"""Deterministic (no-LLM) scoring of the n-way responses.

Lifted from study-tutor ``scripts/eval/score_deterministic.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``): paths root at ``--run-dir``
(change 1), scoring runs over every candidate (change 2), the leak-token
list is overridable per model family, and the stage records itself into
``MANIFEST.json`` (change 4). Legacy two-way ``responses.jsonl`` files load
unchanged (``base``/``finetune`` become candidate names) and produce the
exact 2026-05-18 ``deterministic.json`` shape.

Measures the things a judge is not needed for — and the things a judge
should never be trusted with because they must be exact:

* template-token leaks in the visible stream — a fine-tune regression
  signal; must be zero
* where each model puts its reasoning — inline ``<think>`` vs the
  ``reasoning_content`` API channel
* visible-answer length and whether the reply asks the student a question
  (a crude Socratic-stance proxy; the judge does the real assessment)

Length and question-presence are measured on the VISIBLE answer (``<think>``
stripped) so no candidate is flattered by its inline reasoning block.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness.common import (
    normalise_response_rows, read_jsonl, run_path, update_manifest,
)

# Chat-template control tokens that must never appear in user-visible text.
# Gemma-family default; override with --leak-tokens for other families
# (e.g. Qwen control tokens for a bake-off candidate).
LEAK_TOKENS = [
    "<|channel>", "<channel|>", "<|turn>", "<turn|>",
    "<|message>", "<end_of_turn>", "<start_of_turn>",
]


def score_one(resp: dict, leak_tokens: list[str]) -> dict:
    content = resp.get("content", "")
    visible = resp.get("visible", content)
    reasoning_channel = resp.get("reasoning_content", "")
    inline_think = "<think>" in content
    return {
        "visible_chars": len(visible),
        "visible_words": len(visible.split()),
        "inline_think": inline_think,
        "reasoning_present": inline_think or bool(reasoning_channel.strip()),
        "leak_tokens": sum(visible.count(t) for t in leak_tokens),
        "asks_a_question": "?" in visible,
        "finish_reason": resp.get("finish_reason"),
    }


def summarise(items: list[dict]) -> dict:
    n = max(len(items), 1)
    return {
        "n": len(items),
        "inline_think_pct": round(100 * sum(i["inline_think"] for i in items) / n, 1),
        "reasoning_present_pct": round(100 * sum(i["reasoning_present"] for i in items) / n, 1),
        "leak_total": sum(i["leak_tokens"] for i in items),
        "asks_question_pct": round(100 * sum(i["asks_a_question"] for i in items) / n, 1),
        "mean_visible_words": round(sum(i["visible_words"] for i in items) / n, 1),
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--responses", default=None,
                    help="Override input (default: <run-dir>/responses.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/deterministic.json).")
    ap.add_argument("--leak-tokens", default=None,
                    help="JSON file with a list of leak tokens (per model family).")
    args = ap.parse_args(argv)

    responses_path = run_path(args.run_dir, args.responses, "responses.jsonl")
    out_path = run_path(args.run_dir, args.out, "deterministic.json")
    leak_tokens = (json.loads(Path(args.leak_tokens).read_text(encoding="utf-8"))
                   if args.leak_tokens else LEAK_TOKENS)

    rows, candidates = normalise_response_rows(read_jsonl(responses_path))

    scores: dict[str, list[dict]] = {c: [] for c in candidates}
    per_item = []
    for r in rows:
        item_scores = {c: score_one(r["responses"][c], leak_tokens)
                       for c in candidates}
        for c in candidates:
            scores[c].append(item_scores[c])
        per_item.append({"id": r["id"], "category": r["category"], **item_scores})

    summary = {c: summarise(scores[c]) for c in candidates}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({"summary": summary, "per_item": per_item}, indent=2),
        encoding="utf-8",
    )

    print(f"{'metric':<26}" + "".join(f"{c:>16}" for c in candidates))
    print("-" * (26 + 16 * len(candidates)))
    for k in ["n", "inline_think_pct", "reasoning_present_pct",
              "leak_total", "asks_question_pct", "mean_visible_words"]:
        print(f"{k:<26}" + "".join(f"{summary[c][k]:>16}" for c in candidates))

    print()
    leaky = {c: summary[c]["leak_total"] for c in candidates if summary[c]["leak_total"]}
    if leaky:
        print(f"WARNING: template-token leak(s) in visible output: {leaky} — "
              "a chat-template regression signal.")
    else:
        print("PASS: zero template-token leaks in every candidate's visible output.")

    update_manifest(args.run_dir, "score_deterministic", {  # change 4
        "responses": str(responses_path),
        "leak_tokens": leak_tokens,
        "candidates": candidates,
        "leak_totals": {c: summary[c]["leak_total"] for c in candidates},
    })
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
