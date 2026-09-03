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

# The runaway guard is a sibling harness module; the runners are run as scripts and loaded by
# file path in tests, so its own directory is what makes the import work in both.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from runaway_guard import (  # noqa: E402
    RunawayDetector,
    guard_record,
    stream_chat_completion,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = REPO_ROOT / "tasks"
TASK_ID = "po-held-007-feature-spec"
DEFAULT_ENDPOINT = "http://promaxgb10-41b1:9000/v1"
DEFAULT_PROMPTS_ROOT = REPO_ROOT.parent / "specialist-agent"
SERVING_PROMPT = "roles/product-owner/prompts/player_feature_spec.md"
# The pinned /feature-spec methodology template. Production puts it in the USER turn, and the system
# prompt tells the model it is there ("The request carries the full /feature-spec methodology template
# as reference data"). specialist-agent resolves it as the `feature-spec-methodology` TemplatePin from
# the guardkit package; this is the same file in the guardkit checkout.
DEFAULT_TEMPLATE_ROOT = REPO_ROOT.parent / "guardkit"
METHODOLOGY_TEMPLATE = "installer/core/commands/feature-spec.md"
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


def template_root_identity(template_root: Path) -> dict:
    """Same argument as prompts_root_identity: a grade must name the tree its bytes came from."""
    def _git(*a):
        try:
            return subprocess.run(["git", "-C", str(template_root), *a], capture_output=True,
                                  text=True, timeout=15).stdout.strip() or None
        except Exception:
            return None
    return {
        "path": str(template_root),
        "head": _git("rev-parse", "HEAD"),
        "branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(_git("status", "--porcelain", "--", METHODOLOGY_TEMPLATE)),
    }


def assemble(task_dir: Path, prompts_root: Path, template_root: Path, stack: str = "generic") -> dict:
    """Reproduce what PRODUCTION sends — not a simplification of it.

    2026-08-21 correction. This function used to return {system: player_feature_spec.md, user: brief}.
    That is not the serving shape. `build_feature_spec_input()` in
    specialist-agent/src/specialist_agent/roles/product_owner/modes/feature_spec.py assembles the user
    turn from LABELLED SECTIONS:

        ## Methodology template (reference — precedence rules in system prompt apply)
        {the pinned 944-line template}

        ## Approved input
        {the brief}

        ## Context documents        (only when present)

        ## Stack
        generic

    and 007's own instruction.md §Harness assembly says answer sheets come from the specialist-agent
    target-terminal harness invoking the pinned template with `--auto --stack generic --output
    features/` — explicitly NOT a simplified assembly.

    The omission mattered: the system prompt tells the model "The request carries the full
    /feature-spec methodology template as reference data", so sending only the brief graded the model
    against a request that contradicts its own instructions. This is the same defect class as the
    merged-gen gate replaying a training prompt production never sends — an instrument measuring a
    configuration that does not occur.
    """
    prompt_path = prompts_root / SERVING_PROMPT
    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"Serving prompt not found: {prompt_path} — pass --prompts-root at your "
            "specialist-agent checkout (provenance is pinned in task.toml)."
        )
    template_path = template_root / METHODOLOGY_TEMPLATE
    if not template_path.is_file():
        raise FileNotFoundError(
            f"Methodology template not found: {template_path} — pass --template-root at your "
            "guardkit checkout. Production puts this template in the user turn; grading without it "
            "measures a request production never sends."
        )
    brief = (task_dir / "input" / "brief.md").read_text(encoding="utf-8")
    sections = [
        "## Methodology template (reference — precedence rules in system prompt apply)\n\n"
        + template_path.read_text(encoding="utf-8"),
        "## Approved input\n\n" + brief,
        "## Stack\n\n" + stack,
    ]
    return {"system": prompt_path.read_text(encoding="utf-8"), "user": "\n\n".join(sections)}


def call_model(endpoint, model, system, user, timeout_s, gen_params, runaway_guard=True) -> tuple[dict, dict | None]:
    """Return (reply, guard outcome). With the guard on the reply is streamed and stopped the
    moment it starts repeating itself; with it off this is byte-for-byte the old single POST.

    The streamed reply is folded back into the non-streaming shape before it is returned, so
    response_text() below reads it unchanged — same text, same provenance string.
    """
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        **gen_params,
    }
    if runaway_guard:
        outcome = stream_chat_completion(endpoint, body, timeout_s, RunawayDetector())
        return outcome["reply"], outcome
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8")), None


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
    """A server may split the think block out of the content; re-wrap it inline.

    Two servers, two field names for the same thing: llama.cpp (--reasoning auto) puts the
    separated thinking in message.reasoning_content, vLLM v0.25.0 puts it in message.reasoning.
    Read either — reasoning_content first, then reasoning — and name the field that was used in
    the provenance string, so each rep's config.json records where its thinking came from.
    Before this, a vLLM reply's thinking block was dropped without a trace.
    """
    msg = reply["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning, source = "", ""
    for field in ("reasoning_content", "reasoning"):
        value = msg.get(field) or ""
        if value:
            reasoning, source = value, field
            break
    if reasoning and "<think>" not in _outside_fences(content):
        return f"<think>{reasoning}</think>\n{content}", f"rewrapped_{source}"
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


def tree_from_output(raw: str, prompts_root: Path = DEFAULT_PROMPTS_ROOT) -> tuple[dict[str, str], str]:
    """Preferred: the production post-processor. Fallback: the bundle slicer. Report which."""
    body = strip_think(raw)
    try:
        sys.path.insert(0, str(DEFAULT_PROMPTS_ROOT / "src"))
        from specialist_agent.roles.product_owner.modes.feature_spec import (  # noqa: E402
            postprocess_feature_spec,
        )
        from specialist_agent.modes.types import ModeRuntimeContext  # noqa: E402

        # 2026-08-23: this was ModeRuntimeContext() with no arguments, which raises TypeError, so
        # EVERY rep silently fell back to the bundle slicer. postprocess_feature_spec reads nothing
        # from the context (ctx.templates is used by the ASSEMBLER, not the postprocessor), so a
        # minimal instance is enough — and using the real postprocessor is what makes the F1
        # quality-bar-seed axes MEASURABLE instead of skipped. See po-lane-state §21.
        ctx = ModeRuntimeContext(
            role_config=None,
            role_dir=prompts_root,
            templates={},
            output_path="features/",
            project_name="fleet-evals",
        )
        produced = postprocess_feature_spec(body, ctx)
        if isinstance(produced, dict) and produced:
            return {str(k): str(v) for k, v in produced.items()}, "postprocess_feature_spec"
    except Exception as exc:  # noqa: BLE001 — the fallback is legitimate, but it must be NAMED
        note = f"bundle_slicer (postprocess unavailable: {type(exc).__name__}: {str(exc)[:120]})"
        return slice_file_bundle(body), note
    return slice_file_bundle(body), "bundle_slicer (postprocess returned nothing)"


def _place(rel: str, slug: str | None) -> str:
    """Where production's postprocessor would put this block.

    2026-08-21: the model emits BARE filenames — `=== FILE: kiln-firing-slot-booking.feature ===` —
    exactly as its training rows do. Production runs with `--output features/` and the pinned layout
    is `{--output}/{kebab-case-feature-name}/`, so the postprocessor lands them in
    features/<slug>/. Writing them flat (what this runner did) produced a rep dir with no features/
    directory at all, and every gate then failed on layout — a HARNESS defect reported as a model
    failure. A model-authored path that already names a directory is honoured as-is.
    """
    rel = rel.lstrip("/")
    if "/" in rel or slug is None:
        return rel
    # The additive QA sidecar lands in qa/, NOT beside the spec files — the F1 gate globs
    # $PO_EVAL_OUTPUT_DIR/qa/pass-bar-seed-*.yaml (test_gate_po_held_007_f1_seed.py:76).
    if rel.startswith("pass-bar-seed"):
        return f"qa/{rel}"
    # validation.json is the postprocessor's own report, not a graded artefact
    if rel == "validation.json":
        return rel
    return f"features/{slug}/{rel}"


def write_tree(rep_dir: Path, files: dict[str, str]) -> list[str]:
    written = []
    # the slug is the .feature block's stem — the same value the contract keys every name off
    slug = next((Path(n).stem for n in files if n.endswith(".feature") and "/" not in n.lstrip("/")),
                None)
    for rel, content in files.items():
        rel = _place(rel, slug)
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
    asm = assemble(task_dir, Path(args.prompts_root), Path(args.template_root))
    gen = {k: v for k, v in {"temperature": args.temperature, "top_p": args.top_p,
                             "max_tokens": args.max_tokens}.items() if v is not None}
    record = {
        "task": TASK_ID, "rep": rep, "suite": task["task"].get("suite"),
        "schema": task["task"].get("schema"), "endpoint": args.endpoint, "model": args.model,
        "gen_params_sent": gen or "server defaults",
        "system_sha256": sha256_text(asm["system"]), "user_sha256": sha256_text(asm["user"]),
        "serving_prompt": SERVING_PROMPT,
        "prompts_root": prompts_root_identity(Path(args.prompts_root)),
        "template_root": template_root_identity(Path(args.template_root)),
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    }
    if args.dry_run:
        (rep_dir / "prompt_system.txt").write_text(asm["system"], encoding="utf-8")
        (rep_dir / "prompt_user.txt").write_text(asm["user"], encoding="utf-8")
        record["dry_run"] = True
        record["runaway_guard"] = guard_record(args.runaway_guard, None)
        (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
        return {"rep": rep, "status": "assembled"}

    timeout_s = int(task["task"].get("timeout_seconds", 1800))
    last = None
    for attempt in range(1, RETRIES_PER_REP + 2):
        try:
            t0 = time.monotonic()
            reply, guard = call_model(args.endpoint, args.model, asm["system"], asm["user"],
                                      timeout_s, gen, runaway_guard=args.runaway_guard)
            raw, provenance = response_text(reply)
            # A reply the guard cut short is still read, written and graded exactly as any other
            # — it fails, quickly and honestly — but the receipt must say plainly that the text is
            # a fragment we stopped, not the answer the model finished.
            aborted = bool(guard and guard.get("aborted"))
            if aborted:
                print(f"  rep{rep} RUNAWAY: {guard['rule']} — connection closed after "
                      f"{guard['tokens_received']} tokens", file=sys.stderr)
            files, tree_source = tree_from_output(raw)
            written = write_tree(rep_dir, files)
            (rep_dir / "response.txt").write_text(raw, encoding="utf-8")  # kept for diagnosis
            record.update(
                attempt=attempt, duration_s=round(time.monotonic() - t0, 1),
                response_provenance="runaway_aborted" if aborted else provenance,
                runaway_guard=guard_record(args.runaway_guard, guard),
                tree_source=tree_source,
                files_written=written, server_model=reply.get("model"),
                finish_reason=reply["choices"][0].get("finish_reason"), usage=reply.get("usage"),
                finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
            )
            if aborted:
                # what the text WOULD have been called had it finished, kept beside the abort
                record["text_provenance"] = provenance
            (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
            res = {"rep": rep, "status": "runaway aborted" if aborted else "ok",
                   "files": len(written), "tree_source": tree_source}
            if args.grade:
                res["passed"] = grade_rep(task_dir, rep_dir)
            return res
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException,
                json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            last = exc
            print(f"  rep{rep} attempt {attempt} failed: {exc!r}", file=sys.stderr)
    record.update(error=repr(last), runaway_guard=guard_record(args.runaway_guard, None),
                  finished_at=_dt.datetime.now(_dt.timezone.utc).isoformat())
    (rep_dir / "config.json").write_text(json.dumps(record, indent=2))
    return {"rep": rep, "status": "FAILED — re-run required"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--prompts-root", default=str(DEFAULT_PROMPTS_ROOT))
    ap.add_argument("--template-root", default=str(DEFAULT_TEMPLATE_ROOT),
                    help="guardkit checkout holding the pinned /feature-spec methodology "
                         "template. Production puts it in the user turn; omitting it grades "
                         "a request production never sends.")
    ap.add_argument("--out", default=None)
    ap.add_argument("--rep", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--top-p", type=float, default=None)
    # 2026-08-21: this defaulted to None, so NO cap was sent and the server ran to EOS or the full
    # 131K context. A single repetition loop then burned 27,000+ tokens at 34 t/s before anyone
    # noticed. Production caps registered modes at PLAYER_REGISTERED_MODE_MAX_COMPLETION_TOKENS =
    # 16384 (specialist-agent agents/player.py:61) and its own docstring cites a "live iter-2 260k-char
    # runaway" as the reason. Grading unbounded is both unfaithful to production and unbounded in cost.
    ap.add_argument("--max-tokens", type=int, default=16384,
                    help="Completion budget. Default 16384 = production's registered-mode cap.")
    # 2026-09-03: a rep generated to that ceiling for 17 minutes writing the same 19 scenarios
    # eleven times, and only then could be graded. On by default; the state is written into every
    # rep's config.json because every run before today used no guard at all, and a frozen exam's
    # comparability has to be readable off the receipt rather than remembered.
    ap.add_argument("--runaway-guard", dest="runaway_guard", action="store_true", default=True,
                    help="Stream the reply and stop it once it repeats itself (default on).")
    ap.add_argument("--no-runaway-guard", dest="runaway_guard", action="store_false",
                    help="Read the reply in one non-streaming response, as runs before "
                         "2026-09-03 did.")
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
