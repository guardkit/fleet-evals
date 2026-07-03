"""Per-rollout JSON emission for the phase-ablation study (FEAT-ABL-003).

Reads a Harbor trial directory (or a whole job directory of trials) and emits
one JSON record per rollout, schema::

    {task, arm, rep, reward, retrieval_items, config_hash, wallclock, tokens}

Sources, per trial dir:
  - ``result.json``             — Harbor's TrialResult: task name, reward,
                                  timings, token totals.
  - ``agent/rollout-meta.json`` — written by AutoBuildAgent: arm, config hash,
                                  command wallclock, exit code.
  - ``agent/retrieval.jsonl``   — retrieval log copied out of the container.
                                  SEAM(ABL-001): produced by guardkit only
                                  once FEAT-ABL-001 lands; absent →
                                  ``retrieval_items: null`` (never 0, so
                                  "no log" is distinguishable from "log with
                                  zero items" for the ABL-006 validity
                                  guardrail: >=1 item per on-arm rollout).

Usage (local only, per DF-001 — writes stdout or a local file, no network)::

    python3 -m adapter.rollout_record <trial-dir | job-dir> [-o rollouts.jsonl]

``rep`` assignment: when scanning a job dir, trials are grouped by
(task, arm) and numbered 1..K in ``started_at`` order — matching Harbor's
``-k`` repetition policy. For a single trial dir, pass ``--rep`` or it
defaults to 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

RESULTS_NAME = "result.json"
META_RELPATH = Path("agent") / "rollout-meta.json"
RETRIEVAL_RELPATH = Path("agent") / "retrieval.jsonl"


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def count_retrieval_items(path: Path) -> int | None:
    """Count retrieved items in the ABL-001 retrieval log.

    Expected line schema (SEAM(ABL-001) — confirm when it lands in
    guardkit/knowledge/query_logger.py): one JSON object per line carrying
    ``items: [{id, score}, ...]``. Returns None when the log is absent or
    unreadable, the summed item count otherwise.
    """
    if not path.is_file():
        return None
    total = 0
    parsed_any = False
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        parsed_any = True
        items = obj.get("items")
        if isinstance(items, list):
            total += len(items)
    return total if parsed_any else None


def _reward(results: dict[str, Any] | None) -> float | int | None:
    if not results:
        return None
    rewards = (results.get("verifier_result") or {}).get("rewards") or {}
    if "reward" in rewards:
        return rewards["reward"]
    return next(iter(rewards.values()), None)


def _timing_seconds(timing: dict[str, Any] | None) -> float | None:
    if not timing or not timing.get("started_at") or not timing.get("finished_at"):
        return None
    try:
        start = datetime.fromisoformat(timing["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(timing["finished_at"].replace("Z", "+00:00"))
    except ValueError:
        return None
    return round((end - start).total_seconds(), 3)


def _wallclock(
    meta: dict[str, Any] | None, results: dict[str, Any] | None
) -> float | None:
    """Command wallclock from the adapter, else Harbor's agent-execution phase."""
    if meta and meta.get("wallclock_sec") is not None:
        return meta["wallclock_sec"]
    if results:
        return _timing_seconds(results.get("agent_execution"))
    return None


def _tokens(results: dict[str, Any] | None) -> dict[str, Any] | None:
    """Token totals from Harbor's AgentContext.

    SEAM(ABL-001/guardkit): all-null until guardkit autobuild emits usage and
    AutoBuildAgent.run() populates the context token fields.
    """
    agent_result = (results or {}).get("agent_result") or {}
    tokens = {
        "input": agent_result.get("n_input_tokens"),
        "cache": agent_result.get("n_cache_tokens"),
        "output": agent_result.get("n_output_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
    }
    return tokens if any(v is not None for v in tokens.values()) else None


def record_from_trial(trial_dir: Path, rep: int = 1) -> dict[str, Any]:
    """Build the per-rollout record for one Harbor trial directory."""
    results = _load_json(trial_dir / RESULTS_NAME)
    meta = _load_json(trial_dir / META_RELPATH)
    return {
        "task": (results or {}).get("task_name"),
        "arm": (meta or {}).get("arm"),
        "rep": rep,
        "reward": _reward(results),
        "retrieval_items": count_retrieval_items(trial_dir / RETRIEVAL_RELPATH),
        "config_hash": (meta or {}).get("config_hash"),
        "wallclock": _wallclock(meta, results),
        "tokens": _tokens(results),
    }


def is_trial_dir(path: Path) -> bool:
    """A trial dir holds a TrialResult ``result.json`` (has ``task_name``).

    The parse guard matters: Harbor job dirs carry an *aggregate*
    ``result.json`` of a different shape one level up.
    """
    results = _load_json(path / RESULTS_NAME)
    return bool(results) and "task_name" in results


def iter_trial_dirs(root: Path) -> Iterable[Path]:
    """Yield trial dirs under *root* (root itself, or its direct children)."""
    if is_trial_dir(root):
        yield root
        return
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        if is_trial_dir(child):
            yield child


def _started_at(trial_dir: Path) -> str:
    results = _load_json(trial_dir / RESULTS_NAME) or {}
    return results.get("started_at") or ""


def build_records(root: Path, rep: int | None = None) -> list[dict[str, Any]]:
    """Records for all trials under *root*, with reps assigned per (task, arm)."""
    trial_dirs = sorted(iter_trial_dirs(root), key=_started_at)
    records: list[dict[str, Any]] = []
    rep_counter: dict[tuple[Any, Any], int] = {}
    for trial_dir in trial_dirs:
        record = record_from_trial(trial_dir)
        if rep is not None:
            record["rep"] = rep
        else:
            key = (record["task"], record["arm"])
            rep_counter[key] = rep_counter.get(key, 0) + 1
            record["rep"] = rep_counter[key]
        records.append(record)
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m adapter.rollout_record",
        description="Emit per-rollout JSON from Harbor trial/job directories "
        "(local only, per DF-001).",
    )
    parser.add_argument(
        "root",
        type=Path,
        help="A Harbor trial dir (contains results.json) or a job dir of trials.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSONL here instead of stdout.",
    )
    parser.add_argument(
        "--rep",
        type=int,
        default=None,
        help="Force this rep number instead of inferring per (task, arm).",
    )
    args = parser.parse_args(argv)

    if not args.root.is_dir():
        parser.error(f"not a directory: {args.root}")
    records = build_records(args.root, rep=args.rep)
    if not records:
        parser.error(f"no trial dirs (with {RESULTS_NAME}) found under {args.root}")

    lines = "\n".join(json.dumps(r, sort_keys=False) for r in records) + "\n"
    if args.output:
        args.output.write_text(lines)
    else:
        sys.stdout.write(lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
