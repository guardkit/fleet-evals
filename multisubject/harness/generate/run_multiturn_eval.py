#!/usr/bin/env python3
"""N-way multi-turn harness: walk each scripted tutoring scenario through
every declared candidate and capture the full session transcript per
candidate.

Lifted from study-tutor ``scripts/eval/run_multiturn_eval.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``) with the five pinned changes
(see ``run_ab_eval.py`` — same treatments).

Why multi-turn matters: a model trained on multi-turn dialogue takes short
conversational turns by design. A single-turn eval judges one reply as a
whole lesson and structurally favours a verbose single-shot model. This
harness gives each candidate the SAME fixed sequence of student messages and
lets it build its own side of the conversation.

Parity: identical system prompt, identical decoding, identical student
script. Each candidate accumulates its own assistant turns (the VISIBLE
answer, <think> stripped — chat history does not normally carry thinking).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

from harness.common import (
    _THINK, load_candidates, read_jsonl, require_protocol, run_path,
    sha256_file, sha256_text, strip_think, update_manifest,
)


def generate(endpoint, model, messages, *, temperature, max_tokens, timeout, retries=3):
    payload = {"model": model, "temperature": temperature,
               "max_tokens": max_tokens, "messages": messages}
    for attempt in range(1, retries + 1):
        try:
            resp = httpx.post(f"{endpoint.rstrip('/')}/chat/completions",
                              json=payload, timeout=timeout)
            resp.raise_for_status()
            break
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            if attempt == retries:
                raise
            wait = 5 * attempt
            print(f"      transient error ({exc!r}) — retry in {wait}s")
            time.sleep(wait)
    m = resp.json()["choices"][0]["message"]
    content = m.get("content") or ""
    return {"content": content, "visible": strip_think(content),
            "reasoning_content": m.get("reasoning_content") or ""}


def run_scenario(endpoint, model, system_prompt, student_turns, **kw) -> list[dict]:
    """Walk one scenario; return a list of {student, tutor_visible, ...} turns."""
    messages = [{"role": "system", "content": system_prompt}]
    transcript = []
    for student in student_turns:
        messages.append({"role": "user", "content": student})
        t0 = time.time()
        r = generate(endpoint, model, messages, **kw)
        # Feed the VISIBLE answer back as history (thinking is not retained).
        messages.append({"role": "assistant", "content": r["visible"]})
        transcript.append({
            "student": student,
            "tutor_visible": r["visible"],
            "tutor_reasoning": r["reasoning_content"]
                               or (_THINK.search(r["content"]).group(0)
                                   if "<think>" in r["content"] else ""),
            "latency_s": round(time.time() - t0, 2),
        })
    return transcript


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--venue", required=True,
                    help="Venue dir — must contain a committed PROTOCOL.md.")
    ap.add_argument("--scenarios", required=True,
                    help="Scenario JSONL (e.g. <venue>/golden/multiturn/scenarios.jsonl).")
    ap.add_argument("--system-prompt", required=True)
    ap.add_argument("--candidates", default=None,
                    help="candidates.yaml (default: <venue>/candidates.yaml).")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--subject", default=None,
                    help="Subject stamped on scenarios lacking one (default: english).")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--out", default=None,
                    help="Override output (default: <run-dir>/multiturn_transcripts.jsonl).")
    args = ap.parse_args(argv)

    protocol = require_protocol(args.venue)  # change 5

    candidates_path = args.candidates or str(Path(args.venue) / "candidates.yaml")
    candidates = load_candidates(candidates_path)

    system_prompt = Path(args.system_prompt).read_text(encoding="utf-8").strip()
    scenarios = read_jsonl(args.scenarios)
    kw = dict(temperature=args.temperature, max_tokens=args.max_tokens,
              timeout=args.timeout)

    print(f"Venue protocol: {protocol}")
    print(f"Scenarios: {len(scenarios)}  |  system prompt: {len(system_prompt)} bytes\n")

    def run_pass(cand: dict):
        print(f"--- pass: {cand['name']} = {cand['model']} ---")
        out = {}
        for sc in scenarios:
            try:
                tr = run_scenario(cand["endpoint"], cand["model"], system_prompt,
                                  sc["student_turns"], **kw)
            except Exception as exc:  # noqa: BLE001
                print(f"  ERROR on {sc['id']}: {exc}", file=sys.stderr)
                sys.exit(1)
            out[sc["id"]] = tr
            print(f"  {sc['id']:<26} {len(tr)} turns "
                  f"({sum(t['latency_s'] for t in tr):.0f}s total)")
        return out

    results = {c["name"]: run_pass(c) for c in candidates}

    out_path = run_path(args.run_dir, args.out, "multiturn_transcripts.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for sc in scenarios:
            f.write(json.dumps({
                "id": sc["id"], "text": sc["text"], "summary": sc["summary"],
                "subject": sc.get("subject") or args.subject or "english",
                "student_turns": sc["student_turns"],
                "transcripts": {c["name"]: results[c["name"]][sc["id"]]
                                for c in candidates},
            }) + "\n")

    update_manifest(args.run_dir, "generate_multiturn", {  # change 4
        "venue": str(args.venue),
        "protocol_sha256": sha256_file(protocol),
        "scenarios": str(args.scenarios),
        "scenarios_sha256": sha256_file(args.scenarios),
        "system_prompt": str(args.system_prompt),
        "system_prompt_sha256": sha256_text(system_prompt),
        "candidates": [{"name": c["name"], "model": c["model"],
                        "endpoint": c["endpoint"],
                        "gguf_sha256": c.get("gguf_sha256")} for c in candidates],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "n_scenarios": len(scenarios),
    })
    print(f"\nWrote {len(scenarios)} scenario transcript rows -> {out_path}")


if __name__ == "__main__":
    main()
