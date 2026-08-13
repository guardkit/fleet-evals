#!/usr/bin/env python3
"""N-way generation harness: run a venue's golden set against every declared
candidate model under identical conditions.

Lifted from study-tutor ``scripts/eval/run_ab_eval.py`` (HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843``); the two-way base/finetune CLI
is generalised to an n-way ``candidates.yaml`` (pinned change 2), output is
rooted in ``--run-dir`` (change 1), every run stamps ``MANIFEST.json``
(change 4) and refuses to start without the venue's ``PROTOCOL.md``
(change 5). Each row is stamped with ``subject`` + ``prompt_sha256``.

Parity is the whole point of this harness: every candidate receives the SAME
system prompt, the SAME decoding parameters and the SAME prompts. The only
variable is the model weights.

Reasoning-channel asymmetry (handled here): a thinking model may emit
reasoning INLINE in ``content`` as ``<think>...</think>`` or route it to the
separate ``reasoning_content`` field. Each response is captured as three
things:
  * ``content``           — the raw assistant message content
  * ``reasoning_content`` — the model's reasoning channel
  * ``visible``           — what the student actually reads: ``content`` with
                            any ``<think>`` block stripped
Downstream scoring/judging compares ``visible`` so no candidate is unfairly
credited or penalised for *where* it puts its reasoning.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import httpx

from harness.common import (
    load_candidates, read_jsonl, require_protocol, run_path, sha256_file,
    sha256_text, strip_think, update_manifest,
)


def generate(
    endpoint: str,
    model: str,
    system_prompt: str,
    user_message: str,
    *,
    temperature: float,
    max_tokens: int,
    timeout: float,
    retries: int = 3,
) -> dict:
    """One chat-completions round-trip against an OpenAI-compatible server.

    Retries transient failures (5xx, transport errors) with backoff — a
    cold model swap inside llama-swap can briefly 500.
    """
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    t0 = time.time()
    for attempt in range(1, retries + 1):
        try:
            resp = httpx.post(
                f"{endpoint.rstrip('/')}/chat/completions", json=payload, timeout=timeout
            )
            resp.raise_for_status()
            break
        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            if attempt == retries:
                raise
            wait = 5 * attempt
            print(f"    transient error ({exc!r}) — retry {attempt}/{retries - 1} in {wait}s")
            time.sleep(wait)
    data = resp.json()
    choice = data["choices"][0]
    message = choice["message"]
    content = message.get("content") or ""
    reasoning = message.get("reasoning_content") or ""
    return {
        "content": content,
        "reasoning_content": reasoning,
        "visible": strip_think(content),
        "finish_reason": choice.get("finish_reason"),
        "routed_model": data.get("model"),
        "latency_s": round(time.time() - t0, 2),
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--venue", required=True,
                    help="Venue dir — must contain a committed PROTOCOL.md.")
    ap.add_argument("--golden", required=True,
                    help="Golden-set JSONL (e.g. <venue>/golden/english.jsonl).")
    ap.add_argument(
        "--system-prompt",
        required=True,
        help="Path to the system-prompt file — fed to EVERY candidate.",
    )
    ap.add_argument("--candidates", default=None,
                    help="candidates.yaml (default: <venue>/candidates.yaml).")
    ap.add_argument("--run-dir", required=True,
                    help="Run directory (convention: runs/YYYY-MM-DD-<venue>-<slug>/).")
    ap.add_argument("--subject", default=None,
                    help="Subject stamped on items that lack a 'subject' field "
                         "(default: english).")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=2048,
                    help="Generous — reasoning + answer share this budget.")
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--out", default=None,
                    help="Override output path (default: <run-dir>/responses.jsonl).")
    args = ap.parse_args(argv)

    protocol = require_protocol(args.venue)  # change 5 — refuse unregistered runs

    candidates_path = args.candidates or str(Path(args.venue) / "candidates.yaml")
    candidates = load_candidates(candidates_path)

    system_prompt = Path(args.system_prompt).read_text(encoding="utf-8").strip()
    golden = read_jsonl(args.golden)
    out_path = run_path(args.run_dir, args.out, "responses.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Venue protocol   : {protocol}")
    print(f"Golden items     : {len(golden)}")
    print(f"System prompt    : {len(system_prompt)} bytes (identical for all candidates)")
    print(f"Decoding         : temperature={args.temperature}, max_tokens={args.max_tokens}")
    for c in candidates:
        print(f"CANDIDATE        : {c['name']} = {c['model']} @ {c['endpoint']}")
    print()

    # Generate one candidate fully before the next. llama-swap keeps a single
    # worker hot per pass, so the whole run costs ONE model swap per candidate
    # instead of one per item — far faster and avoids cold-swap 500s.
    def run_pass(cand: dict) -> dict[str, dict]:
        print(f"--- pass: {cand['name']} = {cand['model']} @ {cand['endpoint']} ---")
        out: dict[str, dict] = {}
        for i, item in enumerate(golden, 1):
            try:
                r = generate(
                    cand["endpoint"], cand["model"], system_prompt, item["prompt"],
                    temperature=args.temperature, max_tokens=args.max_tokens,
                    timeout=args.timeout,
                )
            except Exception as exc:  # noqa: BLE001 — fail fast; operator fixes infra
                print(f"  ERROR on {item['id']}: {exc}", file=sys.stderr)
                sys.exit(1)
            out[item["id"]] = r
            print(f"  [{i}/{len(golden)}] {item['id']:<20} {r['latency_s']}s "
                  f"({len(r['visible'])} ch visible)")
        return out

    results = {c["name"]: run_pass(c) for c in candidates}

    with out_path.open("w", encoding="utf-8") as f:
        for item in golden:
            f.write(json.dumps({
                **item,
                "subject": item.get("subject") or args.subject or "english",
                "prompt_sha256": sha256_text(item["prompt"]),
                "responses": {c["name"]: results[c["name"]][item["id"]]
                              for c in candidates},
            }) + "\n")

    update_manifest(args.run_dir, "generate", {  # change 4
        "venue": str(args.venue),
        "protocol_sha256": sha256_file(protocol),
        "golden": str(args.golden),
        "golden_sha256": sha256_file(args.golden),
        "system_prompt": str(args.system_prompt),
        "system_prompt_sha256": sha256_text(system_prompt),
        "candidates": [{"name": c["name"], "model": c["model"],
                        "endpoint": c["endpoint"],
                        "gguf_sha256": c.get("gguf_sha256")} for c in candidates],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "n_items": len(golden),
    })
    print(f"\nWrote {len(golden)} n-way response rows -> {out_path}")


if __name__ == "__main__":
    main()
