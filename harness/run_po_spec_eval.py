#!/usr/bin/env python3
"""Serving-faithful runner for po-held-007-feature-spec (the `po-heldout-spec` suite).

WHY THIS IS A SEPARATE RUNNER, not a branch in run_po_eval.py
-------------------------------------------------------------
`tasks/po-held-007-feature-spec/instruction.md` §"Harness assembly" says it outright:

    Answer sheets for this task are produced by the FEAT-SPL-007 target-terminal harness …
    This task is NOT assembled by `harness/run_po_eval.py` (the artifact is a file tree,
    not `response.txt`).

007's answer is a **three-file triple** written into `features/<kebab-name>/` (`.feature` +
`_assumptions.yaml` + `_summary.md`), optionally beside a `qa/` pass-bar seed — not a single
response string. So this runner produces a file TREE per rep and hands its directory to the
task's own pytest grader through `PO_EVAL_OUTPUT_DIR`, exactly as the instruction specifies.

WHY IT EXISTS AT ALL (2026-08-21, Rich's ruling)
------------------------------------------------
The frozen `po-heldout` suite (001–004) grades extract + greenfield. It does **not** test
feature-spec — which is the factory's own spec-writing step and the thing the PO tune is
actually for. Without this runner nothing about that goal is measurable. Note `po-heldout-spec`
still does not GATE the po-ft-v1 deploy decision (its scope says so); this measures the business
target, it does not silently widen the frozen bar.

HOW THE TREE IS PRODUCED — and why the mechanism is recorded per rep
--------------------------------------------------------------------
Preferred: the production post-processor
`specialist_agent.roles.product_owner.modes.feature_spec.postprocess_feature_spec`, so the eval
exercises the same code the live seat does. If a runtime context cannot be constructed outside a
real session, the runner falls back to slicing the model's own `=== FILE: <path> ===` bundle —
the emission contract the trace corpus and the serving prompt both use. **Which path ran is
written into `config.json` as `tree_source`**, because a receipt that hides how the artifact was
produced is how "green-but-dead" grades happen (see po-lane-state §10.7/§10.9).

stdlib only, like the other runners. Python 3.11+.

Usage:
  python3 harness/run_po_spec_eval.py --model po-ft-v1-gemma4 --endpoint http://127.0.0.1:5998/v1
  python3 harness/run_po_spec_eval.py --model … --grade      # run + pytest-grade each rep
  python3 harness/run_po_spec_eval.py --model … --dry-run    # assemble + record, no network
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "tasks"
TASK_ID = "po-held-007-feature-spec"
DEFAULT_ENDPOINT = "http://promaxgb10-41b1:9000/v1"
DEFAULT_PROMPTS_ROOT = REPO_ROOT.parent / "specialist-agent"
SERVING_PROMPT = "roles/product-owner/prompts/player_feature_spec.md"
RETRIES_PER_REP = 2

# `=== FILE: <path> ===` … the emission contract the serving prompt pins and the trace corpus shows.
FILE_BLOCK = re.compile(r"^===\s*FILE:\s*(?P<path>[^=]+?)\s*===\s*$", re.MULTILINE)


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def load_task(task_dir: Path) -> dict:
    with open(task_dir / "task.toml", "rb") as f:
        return tomllib.load(f)


def prompts_root_identity(prompts_root: Path) -> dict:
    """Stamp WHICH TREE the prompts came from, not just their hashes.

    2026-08-21: the shared specialist-agent checkout was found sitting on another session's
    branch while this suite's baseline was pinned to main's bytes. The hashes happened to match,
    but a branch switch is SILENT and there is no signal — so a grade must carry evidence of the
    tree it read, and a later reader must be able to tell without asking anyone.
    """
    def _git(*a):
        try:
            return subprocess.run(["git", "-C", str(prompts_root), *a], capture_output=True,
                                  text=True, timeout=15).stdout.strip() or None
        except Exception:
            return None
    return {
        "path": str(prompts_root),
        "head": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(_git("status", "--porcelain", "--", "roles/product-owner/prompts")),
    }


def assemble(task_dir: Path, prompts_root: Path) -> dict:
    """instruction.md: the pinned serving template + this brief as the description."""
    prompt_path = prompts_root / SERVING_PROMPT
    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"Serving prompt not found: {prompt_path} — pass --prompts-root at your "
            "specialist-agent checkout (provenance is pinned in task.toml)."
        )
    brief = (task_dir / "input" / "brief.md").read_text(encoding="utf-8")
    return {"system": prompt_path.read_text(encoding="utf-8"), "user": brief}


def call_model(endpoint, model, system, user, timeout_s, gen_params) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        **gen_params,
    }
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _outside_fences(text: str) -> str:
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def response_text(reply: dict) -> tuple[str, str]:
    """llama.cpp --reasoning auto may split the think block out; re-wrap it inline."""
    msg = reply["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    if reasoning and "<think>" not in _outside_fences(content):
        return f"<think>{reasoning}</think>\n{content}", "rewrapped_reasoning_content"
    return content, "content_verbatim"


def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def slice_file_bundle(text: str) -> dict[str, str]:
    """Fallback: split the model's own `=== FILE: <path> ===` bundle into {path: content}."""
    files: dict[str, str] = {}
    marks = list(FILE_BLOCK.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        # ORDER MATTERS (caught by tests/test_po_spec_runner.py, 2026-08-21): strip the
        # `=== END FILE ===` marker FIRST. Otherwise the closing ``` is not at end-of-string when
        # the trailing-fence regex runs, and a code fence is written into the graded .feature file
        # — which the Gherkin parser would then reject for a reason that has nothing to do with
        # the model.
        body = re.sub(r"^===\s*END FILE\s*===\s*$", "", body, flags=re.MULTILINE)
        body = re.sub(r"^\s*```[a-zA-Z0-9]*\s*\n", "", body)
        body = re.sub(r"\n\s*```\s*\n?\s*$", "\n", body)
        files[m.group("path").strip()] = body.strip("\n") + "\n"
    return files


def tree_from_output(raw: str) -> tuple[dict[str, str], str]:
    """Preferred: the production post-processor. Fallback: the bundle slicer. Report which."""
    body = strip_think(raw)
    try:
        sys.path.insert(0, str(DEFAULT_PROMPTS_ROOT / "src"))
        from specialist_agent.roles.product_owner.modes.feature_spec import (  # noqa: E402
            postprocess_feature_spec,
        )
        from specialist_agent.modes.types import ModeRuntimeContext  # noqa: E402

        ctx = ModeRuntimeContext()  # type: ignore[call-arg]
        produced = postprocess_feature_spec(body, ctx)
        if isinstance(produced, dict) and produced:
            return {str(k): str(v) for k, v in produced.items()}, "postprocess_feature_spec"
    except Exception as exc:  # noqa: BLE001 — the fallback is legitimate, but it must be NAMED
        note = f"bundle_slicer (postprocess unavailable: {type(exc).__name__}: {str(exc)[:120]})"
        return slice_file_bundle(body), note
    return slice_file_bundle(body), "bundle_slicer (postprocess returned nothing)"


def write_tree(rep_dir: Path, files: dict[str, str]) -> list[str]:
    written = []
    for rel, content in files.items():
        rel = rel.lstrip("/")
        if ".." in Path(rel).parts:
            continue  # never write outside the rep dir
        p = rep_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        written.append(rel)
    return sorted(written)


def grade_rep(task_dir: Path, rep_dir: Path) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "test/", "-q"],
        cwd=task_dir,
        env={**os.environ, "PO_EVAL_OUTPUT_DIR": str(rep_dir.resolve())},
        capture_output=True,
        text=True,
    )
    (rep_dir / "grade.txt").write_text(proc.stdout[-4000:] + proc.stderr[-2000:], encoding="utf-8")
    return proc.returncode == 0


def run_rep(args, task: dict, task_dir: Path, rep: int, out_dir: Path) -> dict:
    rep_dir = out_dir / TASK_ID / f"rep{rep}"
    rep_dir.mkdir(parents=True, exist_ok=True)
    asm = assemble(task_dir, Path(args.prompts_root))
    gen = {k: v for k, v in {"temperature": args.temperature, "top_p": args.top_p,
                             "max_tokens": args.max_tokens}.items() if v is not None}
    record = {
        "task": TASK_ID, "rep": rep, "suite": task["task"].get("suite"),
        "schema": task["task"].get("schema"), "endpoint": args.endpoint, "model": args.model,
        "gen_params_sent": gen or "server defaults",
        "system_sha256": sha256_text(asm["system"]), "user_sha256": sha256_text(asm["user"]),
        "serving_prompt": SERVING_PROMPT,
        "prompts_root": prompts_root_identity(Path(args.prompts_root)),
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    if args.dry_run:
        (rep_dir / "prompt_system.txt").write_text(asm["system"], encoding="utf-8")
        (rep_dir / "prompt_user.txt").write_text(asm["user"], encoding="utf-8")
        record["dry_run"] = True
        (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
        return {"rep": rep, "status": "assembled"}

    timeout_s = int(task["task"].get("timeout_seconds", 1800))
    last = None
    for attempt in range(1, RETRIES_PER_REP + 2):
        try:
            t0 = time.monotonic()
            reply = call_model(args.endpoint, args.model, asm["system"], asm["user"], timeout_s, gen)
            raw, provenance = response_text(reply)
            files, tree_source = tree_from_output(raw)
            written = write_tree(rep_dir, files)
            (rep_dir / "response.txt").write_text(raw, encoding="utf-8")  # kept for diagnosis
            record.update(
                attempt=attempt, duration_s=round(time.monotonic() - t0, 1),
                response_provenance=provenance, tree_source=tree_source,
                files_written=written, server_model=reply.get("model"),
                finish_reason=reply["choices"][0].get("finish_reason"), usage=reply.get("usage"),
                finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )
            (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
            res = {"rep": rep, "status": "ok", "files": len(written), "tree_source": tree_source}
            if args.grade:
                res["passed"] = grade_rep(task_dir, rep_dir)
            return res
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException,
                json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            last = exc
            print(f"  rep{rep} attempt {attempt} failed: {exc!r}", file=sys.stderr)
    record.update(error=repr(last), finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat())
    (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
    return {"rep": rep, "status": "FAILED — re-run required"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--prompts-root", default=str(DEFAULT_PROMPTS_ROOT))
    ap.add_argument("--out", default=None)
    ap.add_argument("--rep", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--top-p", type=float, default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    args = ap.parse_args()

    task_dir = TASKS_DIR / TASK_ID
    task = load_task(task_dir)
    n_reps = int(task["task"].get("reps", 3))
    if args.rep is not None and not (1 <= args.rep <= n_reps):
        ap.error(f"--rep {args.rep} outside the pre-registered 1..{n_reps}")
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out) if args.out else REPO_ROOT / "runs" / "po-heldout-spec" / f"{stamp}-{args.model}"

    results = []
    for rep in ([args.rep] if args.rep else range(1, n_reps + 1)):
        print(f"→ {TASK_ID} rep{rep}")
        results.append(run_rep(args, task, task_dir, rep, out_dir))

    summary = {"endpoint": args.endpoint, "model_alias": args.model, "task": TASK_ID,
               "reps": results, "at": _dt.datetime.now(_dt.timezone.utc).isoformat()}
    (out_dir / "run_summary.json").write_text(json.dumps(summary, indent=2))
    for r in results:
        print(f"  rep{r['rep']}: {r['status']}"
              + (f" | files {r.get('files')} via {r.get('tree_source')}" if r.get("files") else "")
              + (f" | graded {'PASS' if r.get('passed') else 'FAIL'}" if "passed" in r else ""))
    print(f"\nrun dir: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
