#!/usr/bin/env python3
"""QAV hold-out contamination gate — the WS2 B12 boundary check.

The four gold negatives this suite registers (qav-held-001) are B11's eval_qav
rows. The hold-out discipline is: no training manifest may ever include those
rows, or any training row generated from their four source tasks. This gate
proves B11's own contamination check *recognizes this suite's rows* across the
train/eval boundary — the guardrail is a test, not a hope.

It uses the sibling ``agentic-dataset-factory`` repo (READ-ONLY input) as a
SESSION-TIME dependency only — this script is a gate step, never imported by the
frozen suite's pytest battery, so the suite stays standalone. It:

  1. builds the eval_qav rows via ``qav.gold_negatives.build_gold_negative_rows``
     (the canonical B11 builder) and writes them to a temp ``eval_qav.jsonl``;
  2. runs the real ``scripts/qav_contamination_check.py`` against a CLEAN,
     disjoint training set  → expect PASS (exit 0);
  3. runs it against a POISONED training set that carries a row from a
     gold-negative source task (study-tutor/TASK-SMP2-07) → expect FAIL (exit 1),
     proving the check recognizes THIS suite's held-out sources;
  4. runs it against a POISONED training set that copies one eval row verbatim
     → expect FAIL (row_id intersection).

Exit 0 = the boundary is clean AND the check is live; non-zero = a gate failure.

Usage:  python3 harness/qav_contamination_gate.py [--adf ../agentic-dataset-factory]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def _clean_train_row(adf) -> dict:
    """A benign seeded-code training row that shares nothing with the eval set."""
    return adf["build_row"](
        bundle={"honesty": {"discrepancies": []}, "gathering_status": "complete",
                "tests": {"passed": True}, "quality_gates": {"tests_passed": True}},
        think="All gates green, honesty clean, production call site witnessed. Approve.",
        label={"verdict": "approve", "findings": [], "ground_truth_source": "coach_correct"},
        provenance={"repo": "trailhub", "feature": "FEAT-TH-CAL", "task": "TASK-THC-999",
                    "run": "seed-1", "sha": "deadbeef"},
        split="train", generation_mode="harvest", dc_class=None,
    )


def _run_check(adf_root: Path, train: Path, eval_path: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(adf_root / "scripts" / "qav_contamination_check.py"),
         "--train", str(train), "--eval", str(eval_path)],
        capture_output=True, text=True,
    )
    print(proc.stdout.rstrip())
    if proc.returncode not in (0, 1):
        print(proc.stderr.rstrip(), file=sys.stderr)
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--adf", default=str(REPO_ROOT.parent / "agentic-dataset-factory"),
                    help="path to the agentic-dataset-factory sibling repo")
    args = ap.parse_args(argv)

    adf_root = Path(args.adf).resolve()
    src = adf_root / "src"
    if not (src / "qav" / "gold_negatives.py").is_file():
        print(f"SKIP: adf sibling repo not found at {adf_root} — contamination gate needs it "
              "(READ-ONLY input). Not a suite failure; re-run where the repo is checked out.")
        return 0
    sys.path.insert(0, str(src))
    from qav.contracts import build_row  # noqa: E402
    from qav.gold_negatives import build_gold_negative_rows  # noqa: E402

    eval_rows = build_gold_negative_rows()
    assert len(eval_rows) == 4, f"expected 4 gold negatives, got {len(eval_rows)}"
    for r in eval_rows:
        assert r["metadata"]["split"] == "eval_qav"
        assert r["metadata"]["generation_mode"] == "gold_negative"

    clean = _clean_train_row({"build_row": build_row})
    # poison A: a training row from GN-1's source task (study-tutor/TASK-SMP2-07)
    poison_source = build_row(
        bundle={"honesty": {"discrepancies": []}, "gathering_status": "complete"},
        think="Looks fine.", label={"verdict": "approve", "findings": [], "ground_truth_source": "coach_correct"},
        provenance={"repo": "study-tutor", "feature": "FEAT-SMP-002", "task": "TASK-SMP2-07",
                    "run": "leak", "sha": "cafe"},
        split="train", generation_mode="harvest", dc_class=None,
    )
    # poison B: an eval row copied verbatim onto the train side
    poison_dup = dict(eval_rows[0])

    failures: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        eval_path = tmp / "eval_qav.jsonl"
        _write_jsonl(eval_path, eval_rows)

        clean_train = tmp / "train_clean.jsonl"
        _write_jsonl(clean_train, [clean])
        print("\n[1/3] CLEAN, disjoint training set — expect PASS")
        if _run_check(adf_root, clean_train, eval_path) != 0:
            failures.append("clean train did not PASS")

        src_train = tmp / "train_poison_source.jsonl"
        _write_jsonl(src_train, [clean, poison_source])
        print("\n[2/3] POISONED with a gold-negative source-task row — expect FAIL")
        if _run_check(adf_root, src_train, eval_path) != 1:
            failures.append("gold-source poison was not caught")

        dup_train = tmp / "train_poison_dup.jsonl"
        _write_jsonl(dup_train, [clean, poison_dup])
        print("\n[3/3] POISONED with a verbatim eval-row copy — expect FAIL")
        if _run_check(adf_root, dup_train, eval_path) != 1:
            failures.append("row_id-intersection poison was not caught")

    print()
    if failures:
        for f in failures:
            print(f"GATE FAIL: {f}")
        return 1
    print("QAV CONTAMINATION GATE: PASS — hold-out is clean and B11's check recognizes this suite's rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
