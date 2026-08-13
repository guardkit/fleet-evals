#!/usr/bin/env python3
"""Local-model session judge for the multi-turn track — PROTOCOL v3's Judge B
leg over whole dialogues. Consumes ``multiturn_blind.jsonl`` (so BOTH judges
see the same blinding; resolution stays in ``multiturn_resolve``), composes
the subject rubric with the ``_multiturn.md`` session addendum (seven
dimensions incl. ``engagement_elicitation``), and writes label-space raw
judgements for ``multiturn_resolve --raw``.

Same serving discipline as ``pairwise_local`` (local endpoint, zero cost,
``--no-thinking`` for Qwen-family judges, keepalive paused per the runbook).
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import httpx

from harness.common import (
    MT_DIMS, RUBRICS_DIR, load_rubric, read_jsonl, run_path,
    update_manifest, write_jsonl,
)


def render_transcript(turns: list) -> str:
    """Turns are {student, tutor_visible} pairs (the multiturn transcript
    shape — verified against multiturn_blind.jsonl 2026-08-13; the first
    renderer assumed {role, content} and fed the judge EMPTY sessions,
    which it correctly tied — a caught-and-voided run, see RESULTS)."""
    out = []
    for t in turns:
        if isinstance(t, dict) and "student" in t:
            out.append(f"[STUDENT]: {t['student']}")
            out.append(f"[TUTOR]: {t.get('tutor_visible', t.get('tutor', ''))}")
        elif isinstance(t, dict):
            out.append(f"[{t.get('role', '?').upper()}]: {t.get('content', '')}")
        else:
            out.append(str(t))
    return "\n\n".join(out)


def judge(endpoint: str, model: str, system: str, row: dict, *,
          timeout: float, max_tokens: int, no_thinking: bool) -> dict:
    labels = sorted(row["transcripts"])
    parts = [f"SCENARIO: {row['summary']} (topic: {row['text']})", ""]
    for lab in labels:
        parts += [f"=== SESSION {lab} ===",
                  render_transcript(row["transcripts"][lab]), ""]
    payload = {"model": model, "max_tokens": max_tokens, "temperature": 0,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": "\n".join(parts)}]}
    if no_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            r = httpx.post(f"{endpoint}/chat/completions", json=payload,
                           timeout=timeout)
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"] or ""
            text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            if not text:
                raise json.JSONDecodeError("empty content", "", 0)
            m = re.search(r"```json\s*(.+?)```", text, re.S)
            raw = m.group(1) if m else text
            try:
                verdict = json.loads(raw)
            except json.JSONDecodeError:
                # Models writing maths/physics rationales emit LaTeX-style
                # backslashes (\( \times …) that are invalid JSON escapes —
                # repair by doubling any backslash not starting a valid one.
                verdict = json.loads(
                    re.sub(r'\\(?![\"\\/bfnrtu])', r'\\\\', raw))
            for lab in labels:
                missing = [d for d in MT_DIMS if d not in verdict.get(lab, {})]
                if missing:
                    raise json.JSONDecodeError(f"{lab} missing {missing}", text[:50], 0)
            return verdict
        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as exc:
            last_err = exc
            time.sleep(5 * attempt)
    raise SystemExit(f"session-judge call failed after 3 attempts: {last_err!r}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--blind", default=None,
                    help="Override input (default: <run-dir>/multiturn_blind.jsonl).")
    ap.add_argument("--out", default=None,
                    help="Override output (default: "
                         "<run-dir>/multiturn_raw-local.jsonl).")
    ap.add_argument("--endpoint", default="http://localhost:9000/v1")
    ap.add_argument("--model", default="workhorse")
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--max-tokens", type=int, default=1800)
    ap.add_argument("--no-thinking", action="store_true")
    ap.add_argument("--allow-draft-rubrics", action="store_true")
    args = ap.parse_args(argv)

    blind_path = run_path(args.run_dir, args.blind, "multiturn_blind.jsonl")
    out_path = run_path(args.run_dir, args.out, "multiturn_raw-local.jsonl")
    addendum = (Path(RUBRICS_DIR) / "_multiturn.md").read_text()

    rows = read_jsonl(blind_path)
    done: set[str] = set()
    if out_path.exists():
        done = {json.loads(l)["id"] for l in
                out_path.read_text().splitlines() if l.strip()}
        print(f"resuming: {len(done)} already judged")
    systems: dict[str, str] = {}
    out = []
    for i, r in enumerate(rows, 1):
        if r["id"] in done:
            continue
        subject = r.get("subject") or "english"
        if subject not in systems:
            systems[subject] = (load_rubric(
                subject, allow_draft=args.allow_draft_rubrics)
                + "\n\n" + addendum)
        verdict = judge(args.endpoint, args.model, systems[subject], r,
                        timeout=args.timeout, max_tokens=args.max_tokens,
                        no_thinking=args.no_thinking)
        verdict["id"] = r["id"]
        out.append(verdict)
        # Progressive append — a crash loses nothing (2026-08-13 lesson).
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("a") as f:
            f.write(json.dumps(verdict) + "\n")
        print(f"[{i}/{len(rows)}] {r['id']:<32} winner={verdict.get('winner')}",
              flush=True)

    update_manifest(args.run_dir, "multiturn_judge_local", {
        "judge_model": args.model, "endpoint": args.endpoint,
        "sessions": len(out), "dims": MT_DIMS, "subjects": sorted(systems),
    })
    print(f"Wrote {len(out)} raw session judgements -> {out_path}")


if __name__ == "__main__":
    main()
