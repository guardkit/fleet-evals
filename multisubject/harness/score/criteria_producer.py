#!/usr/bin/env python3
"""Automated criterion-referenced judging — the 2026-05-18 required fix #7's
missing producer, built 2026-08-13 (PROTOCOL v3 extension, Rich's word).

LENGTH-NEUTRAL by construction: each candidate response is scored ALONE (no
A-vs-B comparison, so comprehensiveness cannot beat conciseness by contrast)
against the golden item's own pre-registered ``expected_behaviours`` (met=1 /
partial=0.5 / not=0) and ``red_flags`` (tripped=1 / clean=0). The judge never
sees candidate names or the other candidate's response.

Output: ``criteria_judgements.jsonl`` in exactly the shape
``harness/score/criteria.py`` consumes:
{"id", "category", "<candidate>": {"behaviours": [...], "red_flags": [...]},
 ...one key per candidate...}

Judge = a locally served model via the OpenAI-compatible endpoint (zero cost;
same ``--no-thinking`` discipline as ``pairwise_local``).
"""
from __future__ import annotations

import argparse
import json
import re
import time

import httpx

from harness.common import read_jsonl, run_path, update_manifest, write_jsonl

PROMPT = """You are scoring ONE AI tutor response against pre-registered criteria.
Score each EXPECTED BEHAVIOUR: 1 if the response clearly exhibits it, 0.5 if
partially, 0 if not. Score each RED FLAG: 1 if the response trips it, 0 if not.
Judge only what is present in the response text; do not reward length.

STUDENT MESSAGE:
{prompt}

TUTOR RESPONSE:
{response}

EXPECTED BEHAVIOURS (score each in order):
{behaviours}

RED FLAGS (score each in order):
{flags}

Return ONLY a fenced ```json block of exactly this shape:
{{"behaviours": [<one number per expected behaviour, in order>],
 "red_flags": [<one number per red flag, in order>]}}"""


def score_one(endpoint: str, model: str, item: dict, response: str, *,
              timeout: float, max_tokens: int, no_thinking: bool) -> dict:
    user = PROMPT.format(
        prompt=item["prompt"], response=response,
        behaviours="\n".join(f"{i+1}. {b}" for i, b in
                             enumerate(item["expected_behaviours"])),
        flags="\n".join(f"{i+1}. {f}" for i, f in enumerate(item["red_flags"])))
    payload = {"model": model, "max_tokens": max_tokens, "temperature": 0,
               "messages": [{"role": "user", "content": user}]}
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
            verdict = json.loads(m.group(1) if m else text)
            nb, nf = len(item["expected_behaviours"]), len(item["red_flags"])
            if (len(verdict.get("behaviours", [])) != nb
                    or len(verdict.get("red_flags", [])) != nf):
                raise json.JSONDecodeError("wrong counts", text[:50], 0)
            return verdict
        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as exc:
            last_err = exc
            time.sleep(5 * attempt)
    raise SystemExit(f"criterion call failed after 3 attempts: {last_err!r}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--responses", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--endpoint", default="http://localhost:9000/v1")
    ap.add_argument("--model", default="workhorse")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--max-tokens", type=int, default=400)
    ap.add_argument("--no-thinking", action="store_true")
    args = ap.parse_args(argv)

    responses_path = run_path(args.run_dir, args.responses, "responses.jsonl")
    out_path = run_path(args.run_dir, args.out, "criteria_judgements.jsonl")

    rows = read_jsonl(responses_path)
    out = []
    for i, r in enumerate(rows, 1):
        entry = {"id": r["id"], "category": r.get("category")}
        for cand, resp in r["responses"].items():
            entry[cand] = score_one(
                args.endpoint, args.model, r, resp["visible"],
                timeout=args.timeout, max_tokens=args.max_tokens,
                no_thinking=args.no_thinking)
        out.append(entry)
        print(f"[{i}/{len(rows)}] {r['id']}", flush=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_path, out)
    update_manifest(args.run_dir, "criteria_producer", {
        "judge_model": args.model, "endpoint": args.endpoint,
        "items": len(out),
        "note": "length-neutral: each response scored ALONE vs pre-registered "
                "behaviours/flags; no candidate names shown to the judge",
    })
    print(f"Wrote {len(out)} criterion judgements -> {out_path}")


if __name__ == "__main__":
    main()
