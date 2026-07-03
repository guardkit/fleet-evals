#!/usr/bin/env python3
"""Serving-faithful runner for the PO held-out suite (po-heldout-suite-scope.md).

Produces the rollouts the §5 gate grades: for each task under tasks/po-held-*,
assemble the model input exactly as the task's instruction.md "Runner assembly"
section pins it, call the model once per rep, and save the raw response
(think block included, nothing stripped) as response.txt in the rep directory,
next to a config.json rep record (§5 validity gate: per-rep config records).

stdlib only, like the graders. Python 3.11+ (tomllib).

Usage:
  python3 harness/run_po_eval.py --model po-ft-v1                # all 4 tasks × reps
  python3 harness/run_po_eval.py --model po-ft-v1 --dry-run      # assemble + record, no network
  python3 harness/run_po_eval.py --model po-ft-v1 --grade        # run + pytest-grade each rep
  python3 harness/run_po_eval.py --model po-ft-v1 --task po-held-002-extract-phase-b --rep 2
                                                                 # re-run one aborted rep (never skip)

Prompt sources live in the specialist-agent sibling checkout (provenance pinned
per task.toml); override with --prompts-root if your layout differs.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import http.client
import json
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "tasks"
DEFAULT_ENDPOINT = "http://promaxgb10-41b1:9000/v1"
DEFAULT_PROMPTS_ROOT = REPO_ROOT.parent / "specialist-agent"
MANIFEST_NAME = "MANIFEST.sha256"
RETRIES_PER_REP = 2  # transport retries; a rep that still fails is reported, never skipped


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_task(task_dir: Path) -> dict:
    with open(task_dir / "task.toml", "rb") as f:
        return tomllib.load(f)


def corpus_file_block(path: Path) -> str:
    # Rendering per instruction.md's "Runner assembly" (the red-teamed
    # contract), which pins the "## File: <filename>" header form. NOTE:
    # serving's full session additionally emits ## Mode / ## Docs Path
    # sections and `---` separators (session.py:1268-1369, doc_reader.py:260)
    # — instruction-literal is authoritative here by design.
    return f"## File: {path.name}\n\n{path.read_text(encoding='utf-8')}"


def corpus_blocks(corpus_dir: Path, only: list[str] | None = None) -> str:
    names = sorted(
        p.name for p in corpus_dir.iterdir() if p.is_file() and p.name != MANIFEST_NAME
    )
    if only is not None:
        missing = [n for n in only if n not in names]
        if missing:
            raise FileNotFoundError(
                f"cited_docs not present in {corpus_dir}: {missing}"
            )
        names = [n for n in names if n in only]
    return "\n\n".join(corpus_file_block(corpus_dir / n) for n in names)


def read_prompt(prompts_root: Path, rel: str) -> str:
    path = prompts_root / rel
    if not path.is_file():
        raise FileNotFoundError(
            f"Serving prompt not found: {path} — pass --prompts-root pointing at "
            "your specialist-agent checkout (provenance is pinned in task.toml)."
        )
    return path.read_text(encoding="utf-8")


def assemble(task_id: str, task_dir: Path, prompts_root: Path) -> dict:
    """Build {system, user, project} per the task's instruction.md Runner
    assembly section. Each branch transcribes that section literally — the
    instruction text is the red-teamed contract, so any change there must be
    mirrored here (and re-frozen)."""
    input_dir = task_dir / "input"
    corpus_dir = input_dir / "corpus"

    if task_id == "po-held-001-extract-phase-a":
        system = read_prompt(
            prompts_root, "roles/product-owner/prompts/player_extract_roadmap.md"
        )
        user = (
            "## Product Documentation\n\n"
            + corpus_blocks(corpus_dir)
            + "\n\n## Phase\nroadmap"
        )
        return {"system": system, "user": user, "project": "research"}

    if task_id == "po-held-002-extract-phase-b":
        system = read_prompt(
            prompts_root, "roles/product-owner/prompts/player_extract_features.md"
        )
        epic_plan_text = (input_dir / "epic_plan.json").read_text(encoding="utf-8")
        plan = json.loads(epic_plan_text)
        target = next(e for e in plan["epics"] if e["epic_id"] == "EPIC-006")
        user = (
            "## Epic Plan\n\n"
            + epic_plan_text
            + "\n\n## Product Documentation\n\n"
            + corpus_blocks(corpus_dir, only=list(target["cited_docs"]))
            + "\n\n## Phase\nfeatures\n\nEpic scope: EPIC-006"
        )
        return {"system": system, "user": user, "project": "research"}

    if task_id == "po-held-003-extract-full":
        system = read_prompt(
            prompts_root, "roles/product-owner/prompts/player_extract.md"
        )
        user = "## Product Documentation\n\n" + corpus_blocks(corpus_dir)
        return {"system": system, "user": user, "project": "research"}

    if task_id == "po-held-004-greenfield-discipline":
        system = read_prompt(
            prompts_root, "roles/product-owner/prompts/player_greenfield.md"
        )
        user = (input_dir / "brief.md").read_text(encoding="utf-8")
        return {"system": system, "user": user, "project": "roundroute"}

    raise ValueError(f"No runner assembly registered for task {task_id!r}")


def call_model(
    endpoint: str,
    model: str,
    system: str,
    user: str,
    timeout_s: int,
    gen_params: dict,
) -> dict:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
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
    """Text with ```-fenced regions removed — a literal <think> inside the
    JSON payload is content, not a think block (fence-aware, like the graders)."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def response_text(api_reply: dict) -> tuple[str, str]:
    """Reconstruct the raw serving text. llama.cpp with --reasoning auto may
    split the think block into message.reasoning_content; the serving contract
    (and the fence-aware graders) expect it inline, so re-wrap it."""
    msg = api_reply["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    if reasoning and "<think>" not in _outside_fences(content):
        return f"<think>{reasoning}</think>\n{content}", "rewrapped_reasoning_content"
    return content, "content_verbatim"


def probe_server(endpoint: str) -> dict:
    """One-time capture of what the server actually has loaded behind the
    alias (§9 drift mitigation: per-rep records must expose wrong quant/model;
    the CLI alias alone can't)."""
    try:
        req = urllib.request.Request(endpoint.rstrip("/") + "/models")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # capture-only; a failed probe is itself evidence
        return {"probe_error": str(exc)}


def grade_rep(task_dir: Path, rep_dir: Path) -> bool:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "test/", "-q"],
        cwd=task_dir,
        env={
            **__import__("os").environ,
            "PO_EVAL_OUTPUT_DIR": str(rep_dir.resolve()),
        },
        capture_output=True,
        text=True,
    )
    (rep_dir / "grade.txt").write_text(
        proc.stdout[-4000:] + proc.stderr[-2000:], encoding="utf-8"
    )
    return proc.returncode == 0


def run_rep(
    args, task_id: str, task: dict, task_dir: Path, rep: int, out_dir: Path
) -> dict:
    rep_dir = out_dir / task_id / f"rep{rep}"
    rep_dir.mkdir(parents=True, exist_ok=True)
    asm = assemble(task_id, task_dir, Path(args.prompts_root))
    manifest = task_dir / "input" / "corpus" / MANIFEST_NAME
    gen_params = {
        k: v
        for k, v in {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "max_tokens": args.max_tokens,
        }.items()
        if v is not None
    }
    record = {
        "task": task_id,
        "rep": rep,
        "suite": task["task"].get("suite"),
        "schema": task["task"].get("schema"),
        "project": asm["project"],
        "endpoint": args.endpoint,
        "model": args.model,
        "gen_params_sent": gen_params or "server defaults",
        "system_sha256": sha256_text(asm["system"]),
        "user_sha256": sha256_text(asm["user"]),
        "user_chars": len(asm["user"]),
        "corpus_manifest_sha256": (
            sha256_text(manifest.read_text(encoding="utf-8")) if manifest.is_file() else None
        ),
        "prompt_source": task.get("provenance", {}).get("instruction_source"),
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }

    if args.dry_run:
        (rep_dir / "prompt_user.txt").write_text(asm["user"], encoding="utf-8")
        (rep_dir / "prompt_system.txt").write_text(asm["system"], encoding="utf-8")
        record["dry_run"] = True
        (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
        return {"task": task_id, "rep": rep, "status": "assembled"}

    timeout_s = int(task["task"].get("timeout_seconds", 1800))
    last_err = None
    for attempt in range(1, RETRIES_PER_REP + 2):
        try:
            t0 = time.monotonic()
            reply = call_model(
                args.endpoint, args.model, asm["system"], asm["user"], timeout_s, gen_params
            )
            choice = reply["choices"][0]
            text, provenance = response_text(reply)
            record.update(
                attempt=attempt,
                duration_s=round(time.monotonic() - t0, 1),
                response_provenance=provenance,
                server_model=reply.get("model"),
                finish_reason=choice.get("finish_reason"),
                usage=reply.get("usage"),
                finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )
            (rep_dir / "response.txt").write_text(text, encoding="utf-8")
            (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
            result = {"task": task_id, "rep": rep, "status": "ok"}
            if args.grade:
                result["passed"] = grade_rep(task_dir, rep_dir)
            return result
        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            http.client.HTTPException,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
        ) as exc:
            last_err = exc
            print(f"  {task_id} rep{rep} attempt {attempt} failed: {exc!r}", file=sys.stderr)
    record.update(
        error=repr(last_err),
        finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
    )
    (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
    return {"task": task_id, "rep": rep, "status": "FAILED — re-run required (§5 validity gate)"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True, help="served model alias, e.g. po-ft-v1")
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--prompts-root", default=str(DEFAULT_PROMPTS_ROOT),
                    help="specialist-agent checkout holding the pinned serving prompts")
    ap.add_argument("--out", default=None, help="run dir (default runs/<utc-stamp>-<model>)")
    ap.add_argument("--task", action="append", default=None, help="restrict to task id (repeatable)")
    ap.add_argument("--rep", type=int, default=None, help="run only this rep number (for re-runs)")
    ap.add_argument("--dry-run", action="store_true", help="assemble + record, no model call")
    ap.add_argument("--grade", action="store_true", help="pytest-grade each rep after the call")
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--top-p", type=float, default=None)
    ap.add_argument("--max-tokens", type=int, default=None)
    args = ap.parse_args()

    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out) if args.out else REPO_ROOT / "runs" / f"{stamp}-{args.model}"
    task_dirs = []
    for d in sorted(TASKS_DIR.iterdir()):
        if not (d / "task.toml").is_file():
            continue
        if load_task(d)["task"].get("suite") != "po-heldout":
            continue  # this repo will host other suites (coach-ft); never mix runs
        task_dirs.append(d)
    if args.task:
        task_dirs = [d for d in task_dirs if d.name in set(args.task)]
        if not task_dirs:
            ap.error(f"no po-heldout task dirs match {args.task}")

    results = []
    for task_dir in task_dirs:
        task = load_task(task_dir)
        n_reps = int(task["task"].get("reps", 3))
        if args.rep is not None and not (1 <= args.rep <= n_reps):
            ap.error(
                f"--rep {args.rep} outside the pre-registered 1..{n_reps} for "
                f"{task_dir.name} — extra rollouts would be cherry-picking surface"
            )
        reps = [args.rep] if args.rep is not None else range(1, n_reps + 1)
        for rep in reps:
            print(f"→ {task_dir.name} rep{rep}")
            results.append(run_rep(args, task_dir.name, task, task_dir, rep, out_dir))

    # Merge into any existing summary so a --out re-run of one aborted rep
    # updates the run-level record instead of clobbering it (§5: aborted reps
    # are re-run in place, never skipped, and the record must show it).
    summary_path = out_dir / "run_summary.json"
    summary = (
        json.loads(summary_path.read_text(encoding="utf-8"))
        if summary_path.is_file()
        else {"endpoint": args.endpoint, "model_alias": args.model,
              "server_probes": [], "reps": {}}
    )
    summary.setdefault("server_probes", []).append(
        {"at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
         "probe": "dry-run" if args.dry_run else probe_server(args.endpoint)}
    )
    for r in results:
        summary["reps"][f"{r['task']}/rep{r['rep']}"] = r
    summary_path.write_text(json.dumps(summary, indent=2))

    print(json.dumps(results, indent=2))
    failed = [r for r in results if "FAILED" in r["status"]]
    ungraded_fail = [r for r in results if r.get("passed") is False]
    print(f"\nrun dir: {out_dir}")
    if failed:
        print(f"{len(failed)} rep(s) did not complete — re-run each with "
              f"--task <id> --rep <n> --out {out_dir}  (same run dir: the §5 "
              "validity gate forbids skipping or splitting them)")
    if args.grade:
        print(f"graded: {sum(1 for r in results if 'passed' in r)} reps, "
              f"{len(ungraded_fail)} failed their task gate")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
