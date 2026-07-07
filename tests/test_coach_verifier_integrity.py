"""Verifier integrity for the coach-heldout suite (FEAT-EVAL-COACH).

Additive sibling of the frozen integrity files (all stay byte-identical).
The frozen task discovery globs ``tasks/po-held-*`` only, so the
coach-held-* family is invisible to it BY CONSTRUCTION. This file owns:

  - Oracle / broken-fixture / good-fixture discovery for the coach-held-*
    tasks (the three-sided proof, frozen rules (a)/(b)/(c) applied verbatim);
  - the instruments: authored bundles (parse + the B-min-kin field floor +
    id agreement), the pre-registered expectation registries (1:1 with the
    bundle dirs; DC classes admissible; every must-reject row's signal
    anchor demonstrably fires on the Oracle verdict);
  - the FEAT-EVAL-QAV disjointness tripwire: this suite's rows are CLASS
    KIN of the four real Coach escapes — the real rows are WS2 B12's gold
    negatives (single registration) and must never be reproduced here, so
    the row markers are mechanically banned from every bundle/verdict;
  - fixture floor lists (§2.7 carried over: grow, never shrink).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from harness import coach_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
COACH_TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("coach-held-*") if (p / "task.toml").exists())

FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

BROKEN_CASES = [
    (task_id, fixture.name)
    for task_id in COACH_TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]
GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in COACH_TASK_IDS
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


# --- Three-sided proof (frozen rules (a)/(b)/(c), applied to coach-held-*) --------

def test_coach_task_family_present():
    assert COACH_TASK_IDS == [
        "coach-held-001-escape-kin",
        "coach-held-002-catch-and-green",
    ]


@pytest.mark.parametrize("task_id", COACH_TASK_IDS)
def test_coach_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", BROKEN_CASES)
def test_coach_broken_fixture_fails_its_owner(task_id, fixture_name):
    """(b) A verifier that cannot fail a known-bad verdict sheet is broken."""
    fixture_dir = FIXTURES_DIR / task_id / fixture_name
    meta = json.loads((fixture_dir / "meta.json").read_text(encoding="utf-8"))
    code, out = run_gate(task_id, fixture_dir)
    assert code != 0, f"{task_id}/{fixture_name}: gate PASSED a known-bad verdict sheet"
    failed = set(FAILED_LINE.findall(out))
    missing = [t for t in meta["expect_fail"] if t not in failed]
    assert not missing, (
        f"{task_id}/{fixture_name}: expected {meta['expect_fail']} to fail, "
        f"but only {sorted(failed)} failed:\n{out}"
    )


@pytest.mark.parametrize("task_id,fixture_name", GOOD_CASES)
def test_coach_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate verdict sheet is broken too."""
    code, out = run_gate(task_id, GOOD_FIXTURES_DIR / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate sheet:\n{out}"


# --- Instruments: bundles, registries, anchors --------------------------------------

@pytest.mark.parametrize("task_id", COACH_TASK_IDS)
def test_bundles_parse_and_carry_the_field_floor(task_id):
    task_dir = TASKS_DIR / task_id
    ids = coach_gates.bundle_ids(task_dir)
    assert ids, f"{task_id}: no bundles"
    findings = []
    for bundle_id in ids:
        bundle = coach_gates.load_bundle(task_dir, bundle_id)
        findings.extend(coach_gates.bundle_shape_findings(bundle, bundle_id))
    assert findings == [], findings


@pytest.mark.parametrize("task_id", COACH_TASK_IDS)
def test_expected_registry_matches_bundles(task_id):
    """The pre-registered expectations and the bundle set agree 1:1; every
    row's verdict is a legal enum; every reject row's class is admissible;
    ground_truth_source is 'seeded' (all bundles are authored analogues)."""
    task_dir = TASKS_DIR / task_id
    expected = coach_gates.expected_rows(task_dir)
    assert set(expected) == set(coach_gates.bundle_ids(task_dir))
    for bundle_id, row in expected.items():
        assert row["verdict"] in coach_gates.VERDICTS, bundle_id
        assert row["ground_truth_source"] == "seeded", bundle_id
        if row["verdict"] == "reject":
            assert row["dc_class"] in coach_gates.ADMISSIBLE_DC_CLASSES, bundle_id


@pytest.mark.parametrize("task_id", COACH_TASK_IDS)
def test_signal_anchor_per_reject_row_fires_on_the_oracle(task_id):
    """Every must-reject row owns exactly one anchor group (id = bundle id)
    and the Oracle verdict demonstrates it can fire; approve rows own none."""
    task_dir = TASKS_DIR / task_id
    anchors = coach_gates.load_anchors(task_dir / "test" / "reference" / "signal_anchors.json")
    groups = {g["id"]: g for g in coach_gates.compile_anchors(anchors)}
    expected = coach_gates.expected_rows(task_dir)
    reject_ids = {b for b, row in expected.items() if row["verdict"] == "reject"}
    assert set(groups) == reject_ids, "anchor groups must map 1:1 to must-reject bundles"
    for bundle_id in sorted(reject_ids):
        verdict = coach_gates.load_verdict(task_dir / "solution", bundle_id)
        locus = coach_gates.normalize(coach_gates.verdict_locus_text(verdict))
        assert coach_gates._first_match(groups[bundle_id], locus), (
            f"{task_id}/{bundle_id}: Oracle locus never fires its own signal anchor — dead instrument"
        )


def test_admissible_dc_pin():
    """The Phase-1 admissible DC set stays pinned to adf OUTPUT-CONTRACT.md §3
    verbatim — drift fragments the shared Coach/QAV class vocabulary."""
    assert coach_gates.ADMISSIBLE_DC_CLASSES == ("DC-03", "DC-05", "DC-08", "DC-12", "DC-14")


# --- FEAT-EVAL-QAV (WS2 B12) disjointness tripwire ----------------------------------

B12_ROW_MARKERS = re.compile(
    r"smp-?00[23]|dd4f|\b10ac\b|\bgn-?[1-4]\b|study-tutor", re.IGNORECASE
)


def test_no_b12_gold_negative_row_leaks():
    """This suite's rows are CLASS KIN of the four real escapes; the real
    rows (the FEAT-EVAL-QAV gold negatives, single registration with WS2
    B12) must never be reproduced here. Their identifying markers are banned
    from every bundle, verdict, and fixture."""
    scan_roots = [TASKS_DIR / t / sub for t in COACH_TASK_IDS for sub in ("input", "solution")]
    scan_roots += [FIXTURES_DIR / t for t in COACH_TASK_IDS]
    scan_roots += [GOOD_FIXTURES_DIR / t for t in COACH_TASK_IDS]
    hits = []
    for root in scan_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file():
                m = B12_ROW_MARKERS.search(path.read_text(encoding="utf-8", errors="replace"))
                if m:
                    hits.append(f"{path.relative_to(REPO_ROOT)}: {m.group(0)!r}")
    assert hits == [], f"B12 gold-negative row markers leaked into kin rows: {hits}"


# --- Fixture floors (§2.7: the battery may grow, never shrink) ---------------------

FLOOR_BROKEN_C1 = {
    "approves-the-seam", "wrong-class", "generic-locus",
    "reject-empty-findings", "missing-verdict-file",
}
FLOOR_GOOD_C1 = {"paraphrase-loci", "extra-keys"}
FLOOR_BROKEN_C2 = {"false-blocks-the-greens", "regression-lost"}
FLOOR_GOOD_C2 = {"minimal-correct"}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_coach_fixture_floor_never_shrinks():
    for task_id, broken_floor, good_floor in (
        ("coach-held-001-escape-kin", FLOOR_BROKEN_C1, FLOOR_GOOD_C1),
        ("coach-held-002-catch-and-green", FLOOR_BROKEN_C2, FLOOR_GOOD_C2),
    ):
        broken = _fixture_names(FIXTURES_DIR / task_id)
        good = _fixture_names(GOOD_FIXTURES_DIR / task_id)
        assert broken_floor <= broken, f"{task_id}: missing broken fixtures {sorted(broken_floor - broken)}"
        assert good_floor <= good, f"{task_id}: missing good fixtures {sorted(good_floor - good)}"
