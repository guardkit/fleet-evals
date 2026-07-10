"""Verifier integrity for the gc-heldout suite (FEAT-EVAL-GC / OBS-7).

Additive sibling of the frozen integrity files (all stay byte-identical). The
frozen task discovery globs (``po-held-*``, ``coach-held-*``, ``qav-held-*``,
``arch-held-*``) are blind to the ``gc-held-*`` family BY CONSTRUCTION. This
file owns:

  - the three-sided proof (frozen rules (a)/(b)/(c) verbatim): the Oracle —
    every pinned row's canonical solution — passes both tasks' full gate
    battery by execution; every broken fixture fails its owning test; every
    good fixture passes;
  - the instruments: manifest/pin integrity on the committed 25+25 subset
    (counts, per-row SHA-256 pins, row-id uniqueness ACROSS the suite,
    exclusion + licence/provenance records), the pin-drift demonstration on a
    corrupted copy, and the baselines-file shape (additive family growth; the
    synthetic integrity-fixture family is an instrument, never a grading
    target);
  - fixture floor lists (grow, never shrink).

Fixtures here are ANSWER SHEETS (the PO_EVAL_OUTPUT_DIR contract), generated
mechanically from the Oracle programs at build time.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from harness import gc_gates, gc_rows

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
GC_TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("gc-held-*") if (p / "task.toml").exists())

FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

BROKEN_CASES = [
    (task_id, fixture.name)
    for task_id in GC_TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]
GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in GC_TASK_IDS
    for fixture in sorted((GOOD_FIXTURES_DIR / task_id).glob("*"))
    if fixture.is_dir()
]

FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) .*::(\w+)", re.MULTILINE)


def run_gate(task_id: str, output_dir: Path | None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PO_EVAL_OUTPUT_DIR"}
    if output_dir is not None:
        env["PO_EVAL_OUTPUT_DIR"] = str(output_dir)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TASKS_DIR / task_id / "test"),
         "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    return proc.returncode, proc.stdout + proc.stderr


# --- Three-sided proof (frozen rules (a)/(b)/(c), applied to gc-held-*) --------------

def test_gc_task_family_present():
    assert GC_TASK_IDS == [
        "gc-held-001-humaneval",
        "gc-held-002-mbpp",
    ]


@pytest.mark.parametrize("task_id", GC_TASK_IDS)
def test_gc_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task:
    the canonical benchmark solutions must grade PASS on every row, by
    execution in the sandbox."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", BROKEN_CASES)
def test_gc_broken_fixture_fails_its_owner(task_id, fixture_name):
    """(b) A verifier that cannot fail a known-bad answer sheet is broken."""
    fixture_dir = FIXTURES_DIR / task_id / fixture_name
    meta = json.loads((fixture_dir / "meta.json").read_text(encoding="utf-8"))
    code, out = run_gate(task_id, fixture_dir)
    assert code != 0, f"{task_id}/{fixture_name}: gate PASSED a known-bad answer sheet"
    failed = set(FAILED_LINE.findall(out))
    missing = [t for t in meta["expect_fail"] if t not in failed]
    assert not missing, (
        f"{task_id}/{fixture_name}: expected {meta['expect_fail']} to fail, "
        f"but only {sorted(failed)} failed:\n{out}"
    )


@pytest.mark.parametrize("task_id,fixture_name", GOOD_CASES)
def test_gc_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate answer sheet is broken too —
    including sheets with rows lost inside the frozen margin and sheets where
    an extraction failure is a clean row FAIL."""
    code, out = run_gate(task_id, GOOD_FIXTURES_DIR / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate sheet:\n{out}"


# --- Instruments: manifests, pins, provenance, baselines ------------------------------

@pytest.mark.parametrize("task_id", GC_TASK_IDS)
def test_manifest_pins_hold_on_the_committed_subset(task_id):
    task_dir = TASKS_DIR / task_id
    assert gc_gates.verify_pins(task_dir) == []
    manifest = gc_rows.load_manifest(task_dir)
    assert manifest["row_count"] == len(manifest["rows"]) == 25


def test_row_ids_unique_across_the_whole_suite():
    """Row identity must be unambiguous across the two benchmark subsets."""
    all_ids: list[str] = []
    for task_id in GC_TASK_IDS:
        all_ids.extend(gc_rows.manifest_row_ids(TASKS_DIR / task_id))
    assert len(all_ids) == 50
    assert len(set(all_ids)) == 50, "row-id collision across the suite"


@pytest.mark.parametrize("task_id", GC_TASK_IDS)
def test_selection_and_licence_provenance_recorded(task_id):
    """The subset's selection rule, exclusions, licence, and upstream source
    are pre-registered in the manifest + PROVENANCE.md (ASSUM-001/007)."""
    task_dir = TASKS_DIR / task_id
    manifest = gc_rows.load_manifest(task_dir)
    assert "ascending numeric benchmark task-id" in manifest["selection_rule"]
    assert isinstance(manifest["exclusions"], list)
    assert manifest["source"]["license"] in ("MIT", "CC BY 4.0")
    assert manifest["source"]["upstream_commit"]
    assert manifest["pinned_interpreter"].startswith("Python 3.")
    provenance = (task_dir / "input" / "PROVENANCE.md").read_text(encoding="utf-8")
    assert "Contamination residual (pre-registered)" in provenance


def test_pin_drift_blocks_grading_on_a_corrupted_copy(tmp_path):
    """One drifted byte in a pinned row is caught and NAMED before grading."""
    task_id = "gc-held-001-humaneval"
    victim = gc_rows.manifest_row_ids(TASKS_DIR / task_id)[0]
    copy = tmp_path / task_id
    shutil.copytree(TASKS_DIR / task_id / "input", copy / "input")
    path = gc_rows.row_path(copy, victim)
    path.write_bytes(path.read_bytes().replace(b"def", b"dEf", 1))
    findings = gc_gates.verify_pins(copy)
    assert findings and victim in findings[0] and "DRIFTED" in findings[0]


def test_baselines_file_grows_additively_and_flags_instruments():
    """Families are added additively by the baseline runbook; the synthetic
    integrity-fixture family must stay flagged as an instrument and every
    family must cover both benchmarks with integer solved counts."""
    baselines = gc_gates.load_baselines()
    families = baselines["families"]
    assert "integrity-fixture/NONE" in families
    assert families["integrity-fixture/NONE"].get("instrument") is True
    for key, family in families.items():
        assert "/" in key, f"family key {key!r} must be <base_family>/<quant>"
        for task_id in GC_TASK_IDS:
            benchmark = family["benchmarks"].get(task_id)
            assert benchmark is not None, f"{key}: missing benchmark record for {task_id}"
            assert isinstance(benchmark["baseline_solved"], int)


def test_frozen_task_globs_stay_blind_to_gc_tasks():
    """The frozen suites' discovery globs cannot see gc-held-* (additive-only
    proof by construction)."""
    for pattern in ("po-held-*", "coach-held-*", "qav-held-*", "arch-held-*"):
        overlap = {p.name for p in TASKS_DIR.glob(pattern)} & set(GC_TASK_IDS)
        assert overlap == set()


# --- Fixture floors (the battery may grow, never shrink) ------------------------------

FLOOR_BROKEN_GC1 = {
    "regressed-beyond-margin", "missing-candidate-record",
    "unknown-baseline-family", "foreign-row-injected",
}
FLOOR_GOOD_GC1 = {"within-margin", "extraction-fail-row-within-margin"}
FLOOR_BROKEN_GC2 = {"regressed-beyond-margin", "truncated-rows-regress"}
FLOOR_GOOD_GC2 = {"within-margin"}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_gc_fixture_floor_never_shrinks():
    for task_id, broken_floor, good_floor in (
        ("gc-held-001-humaneval", FLOOR_BROKEN_GC1, FLOOR_GOOD_GC1),
        ("gc-held-002-mbpp", FLOOR_BROKEN_GC2, FLOOR_GOOD_GC2),
    ):
        broken = _fixture_names(FIXTURES_DIR / task_id)
        good = _fixture_names(GOOD_FIXTURES_DIR / task_id)
        assert broken_floor <= broken, f"{task_id}: missing broken fixtures {sorted(broken_floor - broken)}"
        assert good_floor <= good, f"{task_id}: missing good fixtures {sorted(good_floor - good)}"
