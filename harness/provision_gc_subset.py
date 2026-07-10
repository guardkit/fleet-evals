#!/usr/bin/env python3
"""Provision the pinned gc-heldout benchmark subset (FEAT-EVAL-GC, ASSUM-001/007).

Build-time, one-shot, re-runnable. Downloads the public benchmarks, applies the
pinned selection rule, and commits the fixed subset IN-REPO with per-row SHA-256
pins and licence/provenance records. The private-asset symlink farm
(link_assets.py + ASSETS.sha256) is deliberately untouched — this data is public
and permissively licensed (HumanEval MIT, MBPP CC BY 4.0).

Selection rule (pinned verbatim; freeze value ASSUM-001):
  ascending NUMERIC benchmark task-id; a row is excluded — with the exclusion
  recorded — iff its canonical solution fails under the pinned interpreter
  inside the gc sandbox (the same surface that grades candidates); the first
  25 survivors per benchmark are pinned.

Network is used HERE ONLY (build time). Nothing on the grading path fetches.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from harness import gc_rows, gc_sandbox  # noqa: E402

SUBSET_SIZE = 25

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"
MBPP_URL = "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl"

HUMANEVAL_FIELDS = ("prompt", "canonical_solution", "test", "entry_point")
MBPP_FIELDS = ("text", "code", "test_list", "test_setup_code")


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def latest_commit(repo: str, path: str) -> str:
    url = f"https://api.github.com/repos/{repo}/commits?path={path}&per_page=1"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        commits = json.loads(resp.read().decode("utf-8"))
    return commits[0]["sha"] if commits else "unknown"


def humaneval_rows() -> list[dict]:
    raw = gzip.decompress(fetch(HUMANEVAL_URL)).decode("utf-8")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    rows.sort(key=lambda r: int(r["task_id"].split("/")[1]))
    out = []
    for src in rows:
        row = {
            "row_id": f"HumanEval-{src['task_id'].split('/')[1]}",
            "benchmark": gc_rows.BENCHMARK_HUMANEVAL,
            "benchmark_task_id": src["task_id"],
        }
        row.update({k: src[k] for k in HUMANEVAL_FIELDS})
        out.append(row)
    return out


def mbpp_rows() -> list[dict]:
    raw = fetch(MBPP_URL).decode("utf-8")
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    rows.sort(key=lambda r: int(r["task_id"]))
    out = []
    for src in rows:
        row = {
            "row_id": f"mbpp-{src['task_id']}",
            "benchmark": gc_rows.BENCHMARK_MBPP,
            "benchmark_task_id": src["task_id"],
        }
        row.update({k: src.get(k) for k in MBPP_FIELDS})
        out.append(row)
    return out


def select_subset(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Apply the pinned selection rule. Returns (selected, exclusions)."""
    selected, exclusions = [], []
    for row in rows:
        if len(selected) == SUBSET_SIZE:
            break
        script = gc_rows.execution_script(row, gc_rows.canonical_candidate_program(row))
        result = gc_sandbox.run_program(script)
        if result.status == "pass":
            selected.append(row)
        else:
            exclusions.append({
                "benchmark_task_id": row["benchmark_task_id"],
                "reason": f"canonical solution FAILED under the pinned interpreter "
                          f"({result.reason}, exit={result.exit_code})",
                "stderr_tail": result.stderr.strip()[-300:],
            })
            print(f"  EXCLUDED {row['row_id']}: {result.reason}")
    if len(selected) < SUBSET_SIZE:
        raise SystemExit(f"only {len(selected)} survivors — refusing to pin a short subset")
    return selected, exclusions


def write_task_inputs(task_dir: Path, benchmark: str, selected: list[dict],
                      exclusions: list[dict], source: dict, field_subset: tuple,
                      provenance_md: str) -> None:
    rows_dir = task_dir / "input" / "rows"
    rows_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for row in selected:
        row_bytes = gc_rows.canonical_json_bytes(row)
        row_dir = rows_dir / row["row_id"]
        row_dir.mkdir(parents=True, exist_ok=True)
        (row_dir / "row.json").write_bytes(row_bytes)
        manifest_rows.append({
            "row_id": row["row_id"],
            "benchmark_task_id": row["benchmark_task_id"],
            "sha256": gc_rows.sha256_bytes(row_bytes),
        })
    manifest = {
        "suite": "gc-heldout",
        "task_id": task_dir.name,
        "benchmark": benchmark,
        "row_count": len(selected),
        "source": source,
        "selection_rule": (
            "ascending numeric benchmark task-id; a row is excluded (recorded below) iff "
            "its canonical solution fails under the pinned interpreter inside the gc "
            "sandbox; first 25 survivors pinned. No split carve-outs (ASSUM-001 verbatim)."
        ),
        "pinned_interpreter": "Python " + ".".join(map(str, sys.version_info[:3])),
        "sandbox": "harness/gc_sandbox.py (unshare -rn + python3 -I; ROW_TIMEOUT_S=10)",
        "field_subset": list(field_subset),
        "grader_side_fields_note": (
            "reference assertions are grader-side (gc_rows.reference_assertions); the "
            "candidate program never contains them"
        ),
        "exclusions": exclusions,
        "rows": manifest_rows,
    }
    (task_dir / "input" / "manifest.json").write_bytes(gc_rows.canonical_json_bytes(manifest))
    (task_dir / "input" / "PROVENANCE.md").write_text(provenance_md, encoding="utf-8")


def write_oracle(task_dir: Path, selected: list[dict]) -> None:
    programs = task_dir / "solution" / "programs"
    programs.mkdir(parents=True, exist_ok=True)
    for row in selected:
        (programs / f"{row['row_id']}.py").write_text(
            gc_rows.canonical_candidate_program(row), encoding="utf-8")
    (task_dir / "solution" / "candidate.json").write_bytes(gc_rows.canonical_json_bytes({
        "model_id": "oracle-canonical-solutions",
        "oracle": True,
        "note": "the benchmark's own solutions in candidate-program form; the gate "
                "battery must grade every row PASS (house rule §3.5: a task whose "
                "Oracle fails is a broken verifier, not a hard task)",
    }))
    (task_dir / "solution" / "PROVENANCE.md").write_text(
        "# Oracle provenance\n\nPrograms are the pinned rows' canonical solutions "
        "(`gc_rows.canonical_candidate_program`), written by "
        "`harness/provision_gc_subset.py` at subset-pin time. Reference assertions are "
        "grader-side and never part of a candidate program.\n", encoding="utf-8")


def verify(task_dir: Path) -> None:
    """Post-write re-verification: pins hold and every Oracle program passes."""
    manifest = gc_rows.load_manifest(task_dir)
    for entry in manifest["rows"]:
        row_bytes = gc_rows.row_path(task_dir, entry["row_id"]).read_bytes()
        assert gc_rows.sha256_bytes(row_bytes) == entry["sha256"], entry["row_id"]
        row = json.loads(row_bytes)
        program = (task_dir / "solution" / "programs" / f"{entry['row_id']}.py").read_text(encoding="utf-8")
        result = gc_sandbox.run_program(gc_rows.execution_script(row, program))
        assert result.status == "pass", f"{entry['row_id']}: oracle failed post-write ({result.reason})"
    print(f"  VERIFIED {task_dir.name}: {manifest['row_count']} rows, pins intact, oracle green")


HUMANEVAL_PROVENANCE = """\
# Provenance — gc-held-001-humaneval pinned subset

- **Source:** HumanEval (`openai/human-eval`, `data/HumanEval.jsonl.gz`), retrieved {date}
  from {url} @ upstream commit `{commit}`.
- **Licence:** MIT. Copyright (c) 2021 OpenAI.
  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to the following
  conditions: The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
  WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
  OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
- **Changes:** 25-row subset per the pinned selection rule (manifest.json); rows
  re-serialized to this repo's canonical row.json form (field subset recorded in the
  manifest); reference tests held grader-side.
- **Contamination residual (pre-registered):** these rows are public data present in
  base-model pretraining; the suite reports RELATIVE regression only, never absolute
  capability.
"""

MBPP_PROVENANCE = """\
# Provenance — gc-held-002-mbpp pinned subset

- **Source:** MBPP — Mostly Basic Python Problems (Austin et al., 2021,
  "Program Synthesis with Large Language Models"), `google-research/google-research`,
  `mbpp/mbpp.jsonl`, retrieved {date} from {url} @ upstream commit `{commit}`.
- **Licence:** CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
  Attribution: Google Research, MBPP dataset. This subset is redistributed under the
  same licence with changes noted below.
- **Changes:** 25-row subset per the pinned selection rule (manifest.json); rows
  re-serialized to this repo's canonical row.json form (field subset recorded in the
  manifest — `challenge_test_list` not carried); the benchmark's reference asserts are
  shown to the model in the prompt (the standard MBPP convention, ASSUM-009) and
  executed grader-side.
- **Contamination residual (pre-registered):** these rows are public data present in
  base-model pretraining; the suite reports RELATIVE regression only, never absolute
  capability.
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skip-fetch-commit", action="store_true",
                    help="skip the GitHub API provenance-commit lookup")
    args = ap.parse_args()

    gc_sandbox.ensure_available()
    date = datetime.date.today().isoformat()

    print("HumanEval: fetching + selecting...")
    he_commit = "unknown" if args.skip_fetch_commit else latest_commit(
        "openai/human-eval", "data/HumanEval.jsonl.gz")
    he_selected, he_excl = select_subset(humaneval_rows())
    he_dir = REPO_ROOT / "tasks" / "gc-held-001-humaneval"
    write_task_inputs(
        he_dir, gc_rows.BENCHMARK_HUMANEVAL, he_selected, he_excl,
        {"url": HUMANEVAL_URL, "upstream_commit": he_commit, "license": "MIT",
         "retrieved": date},
        HUMANEVAL_FIELDS,
        HUMANEVAL_PROVENANCE.format(date=date, url=HUMANEVAL_URL, commit=he_commit),
    )
    write_oracle(he_dir, he_selected)
    verify(he_dir)

    print("MBPP: fetching + selecting...")
    mbpp_commit = "unknown" if args.skip_fetch_commit else latest_commit(
        "google-research/google-research", "mbpp/mbpp.jsonl")
    mbpp_selected, mbpp_excl = select_subset(mbpp_rows())
    mbpp_dir = REPO_ROOT / "tasks" / "gc-held-002-mbpp"
    write_task_inputs(
        mbpp_dir, gc_rows.BENCHMARK_MBPP, mbpp_selected, mbpp_excl,
        {"url": MBPP_URL, "upstream_commit": mbpp_commit, "license": "CC BY 4.0",
         "retrieved": date},
        MBPP_FIELDS,
        MBPP_PROVENANCE.format(date=date, url=MBPP_URL, commit=mbpp_commit),
    )
    write_oracle(mbpp_dir, mbpp_selected)
    verify(mbpp_dir)

    all_ids = gc_rows.manifest_row_ids(he_dir) + gc_rows.manifest_row_ids(mbpp_dir)
    assert len(all_ids) == len(set(all_ids)) == 2 * SUBSET_SIZE, "row-id collision"
    print(f"DONE: {2 * SUBSET_SIZE} rows pinned, ids unique across the suite")


if __name__ == "__main__":
    main()
