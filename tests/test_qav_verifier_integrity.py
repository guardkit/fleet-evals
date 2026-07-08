"""Verifier integrity for the QAV held-out suite (FEAT-EVAL-QAV, WS2 B12).

Additive sibling of the frozen integrity files (all stay byte-identical). The
frozen task discovery globs ``tasks/po-held-*`` only, so the ``qav-held-*``
family is invisible to it BY CONSTRUCTION. This file owns:

  - Oracle / broken-fixture / good-fixture discovery for the ``qav-held-*``
    tasks (the three-sided proof, frozen rules (a)/(b)/(c) applied verbatim);
  - the instruments: authored bundles (parse + the evidence floor + identity
    agreement + CoachEvidenceBundle schema fidelity), the pre-registered
    expectation registries (1:1 with the bundle dirs; DC classes admissible;
    every must-reject row's signal anchor demonstrably fires on the Oracle);
  - the SINGLE-REGISTRATION completeness check: qav-held-001 registers exactly
    the four REAL gold negatives (GN-1..GN-4) with their documented DC classes
    and real ground-truth sources — the mirror of the coach suite's
    disjointness tripwire (presence here, absence there);
  - the B11 fidelity drift guard: each gold-negative bundle's evidence matches
    ``adf qav.gold_negatives`` field-for-field, and the pinned CoachEvidenceBundle
    field set matches ``adf qav.contracts`` — skipped (not silently passed) when
    the sibling repo is absent;
  - fixture floor lists (grow, never shrink).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from harness import qav_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
QAV_TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("qav-held-*") if (p / "task.toml").exists())

FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

BROKEN_CASES = [
    (task_id, fixture.name)
    for task_id in QAV_TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]
GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in QAV_TASK_IDS
    for fixture in sorted((GOOD_FIXTURES_DIR / task_id).glob("*"))
    if fixture.is_dir()
]

FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) .*::(\w+)", re.MULTILINE)

# adf sibling repo (READ-ONLY input) — importable only when checked out next door.
_ADF_SRC = REPO_ROOT.parent / "agentic-dataset-factory" / "src"
_ADF_PRESENT = (_ADF_SRC / "qav" / "gold_negatives.py").is_file()


def _load_adf(module: str):
    """Load a `qav.*` module from the sibling adf repo without polluting the
    session's import path permanently."""
    if str(_ADF_SRC) not in sys.path:
        sys.path.insert(0, str(_ADF_SRC))
    return importlib.import_module(module)


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


# --- Three-sided proof (frozen rules (a)/(b)/(c), applied to qav-held-*) -----------

def test_qav_task_family_present():
    assert QAV_TASK_IDS == [
        "qav-held-001-gold-negatives",
        "qav-held-002-honest-green",
    ]


@pytest.mark.parametrize("task_id", QAV_TASK_IDS)
def test_qav_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", BROKEN_CASES)
def test_qav_broken_fixture_fails_its_owner(task_id, fixture_name):
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
def test_qav_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate verdict sheet is broken too."""
    code, out = run_gate(task_id, GOOD_FIXTURES_DIR / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate sheet:\n{out}"


# --- Instruments: bundles, registries, anchors -------------------------------------

@pytest.mark.parametrize("task_id", QAV_TASK_IDS)
def test_bundles_parse_and_carry_the_field_floor(task_id):
    task_dir = TASKS_DIR / task_id
    ids = qav_gates.bundle_ids(task_dir)
    assert ids, f"{task_id}: no bundles"
    findings = []
    for bundle_id in ids:
        bundle = qav_gates.load_bundle(task_dir, bundle_id)
        findings.extend(qav_gates.bundle_shape_findings(bundle, bundle_id))
    assert findings == [], findings


@pytest.mark.parametrize("task_id", QAV_TASK_IDS)
def test_expected_registry_matches_bundles(task_id):
    """The pre-registered expectations and the bundle set agree 1:1; every row's
    verdict is a legal enum; every reject row's class is admissible;
    ground_truth_source is real (operator/merge/live-gate) on the gold-negative
    task and 'seeded' on the authored-analogue task."""
    task_dir = TASKS_DIR / task_id
    expected = qav_gates.expected_rows(task_dir)
    assert set(expected) == set(qav_gates.bundle_ids(task_dir))
    is_gold_task = task_id == "qav-held-001-gold-negatives"
    for bundle_id, row in expected.items():
        assert row["verdict"] in qav_gates.VERDICTS, bundle_id
        if is_gold_task:
            assert row["ground_truth_source"] in qav_gates.REAL_GROUND_TRUTH_SOURCES, bundle_id
        else:
            assert row["ground_truth_source"] == "seeded", bundle_id
        if row["verdict"] == "reject":
            assert row["dc_class"] in qav_gates.ADMISSIBLE_DC_CLASSES, bundle_id


@pytest.mark.parametrize("task_id", QAV_TASK_IDS)
def test_signal_anchor_per_reject_row_fires_on_the_oracle(task_id):
    """Every must-reject row owns exactly one anchor group (id = bundle id) and
    the Oracle verdict demonstrates it can fire; approve rows own none."""
    task_dir = TASKS_DIR / task_id
    anchors = qav_gates.load_anchors(task_dir / "test" / "reference" / "signal_anchors.json")
    groups = {g["id"]: g for g in qav_gates.compile_anchors(anchors)}
    expected = qav_gates.expected_rows(task_dir)
    reject_ids = {b for b, row in expected.items() if row["verdict"] == "reject"}
    assert set(groups) == reject_ids, "anchor groups must map 1:1 to must-reject bundles"
    for bundle_id in sorted(reject_ids):
        verdict = qav_gates.load_verdict(task_dir / "solution", bundle_id)
        locus = qav_gates.normalize(qav_gates.verdict_locus_text(verdict))
        assert qav_gates._first_match(groups[bundle_id], locus), (
            f"{task_id}/{bundle_id}: Oracle locus never fires its own signal anchor — dead instrument"
        )


def test_admissible_dc_pin():
    """The Phase-1 admissible DC set stays pinned to adf OUTPUT-CONTRACT.md §3
    verbatim — drift fragments the shared Coach/QAV class vocabulary."""
    assert qav_gates.ADMISSIBLE_DC_CLASSES == ("DC-03", "DC-05", "DC-08", "DC-12", "DC-14")


# --- Single-registration completeness (the mirror of coach's disjointness tripwire) --

def test_all_four_gold_negatives_registered():
    """qav-held-001 registers EXACTLY the four real gold negatives with their
    documented DC classes and real ground-truth sources, and each bundle's
    identity fields match the pinned source (repo/feature/task). This suite is
    the single registration the coach-heldout tripwire defers to."""
    task_dir = TASKS_DIR / "qav-held-001-gold-negatives"
    expected = qav_gates.expected_rows(task_dir)
    assert set(expected) == set(qav_gates.GOLD_NEGATIVE_SOURCES) == {"GN-1", "GN-2", "GN-3", "GN-4"}
    for gid, row in expected.items():
        src = qav_gates.GOLD_NEGATIVE_SOURCES[gid]
        assert row["verdict"] == "reject" and row.get("gold_negative") is True, gid
        assert row["dc_class"] == src["dc_class"], gid
        assert row["ground_truth_source"] in qav_gates.REAL_GROUND_TRUTH_SOURCES, gid
        assert row["source"] == {"repo": src["repo"], "feature": src["feature"], "task": src["task"]}, gid
        bundle = qav_gates.load_bundle(task_dir, gid)
        assert bundle["feature_id"] == src["feature"] and bundle["task_id"] == src["task"], gid


# --- B11 fidelity drift guards (skipped, not passed, when adf is absent) -------------

@pytest.mark.skipif(not _ADF_PRESENT, reason="adf sibling repo not checked out — fidelity drift guard skipped")
def test_gold_negative_bundles_match_adf_field_for_field():
    """Each on-disk gold-negative bundle's evidence (minus identity fields) equals
    adf ``qav.gold_negatives`` GoldNegative.reconstructed_bundle exactly, and its
    feature/task match — so the suite can never silently drift from B11's rows."""
    gn_mod = _load_adf("qav.gold_negatives")
    by_id = {gn.gn_id: gn for gn in gn_mod.GOLD_NEGATIVES}
    task_dir = TASKS_DIR / "qav-held-001-gold-negatives"
    for gid in ("GN-1", "GN-2", "GN-3", "GN-4"):
        gn = by_id[gid]
        bundle = qav_gates.load_bundle(task_dir, gid)
        evidence = {k: v for k, v in bundle.items() if k not in qav_gates.QAV_ID_FIELDS}
        assert evidence == gn.reconstructed_bundle, f"{gid}: bundle drifted from adf reconstructed_bundle"
        assert bundle["feature_id"] == gn.feature and bundle["task_id"] == gn.task, gid


@pytest.mark.skipif(not _ADF_PRESENT, reason="adf sibling repo not checked out — schema pin skipped")
def test_pinned_bundle_field_set_matches_adf():
    """The pinned CoachEvidenceBundle field set equals adf ``qav.contracts``
    BUNDLE_FIELDS — the schema fidelity check keys on the real dataclass shape."""
    contracts = _load_adf("qav.contracts")
    assert frozenset(qav_gates.PINNED_COACH_BUNDLE_FIELDS) == contracts.BUNDLE_FIELD_SET
    assert qav_gates.PINNED_BUNDLE_SCHEMA_SHA == contracts.PINNED_BUNDLE_SCHEMA_SHA


# --- Fixture floors (the battery may grow, never shrink) ---------------------------

FLOOR_BROKEN_Q1 = {
    "approves-a-gold-negative", "wrong-class", "generic-locus",
    "reject-empty-findings", "missing-verdict-file",
}
FLOOR_GOOD_Q1 = {"paraphrase-loci", "extra-keys"}
FLOOR_BROKEN_Q2 = {"false-blocks-the-ugly-green", "catch-floor-lost"}
FLOOR_GOOD_Q2 = {"minimal-correct"}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_qav_fixture_floor_never_shrinks():
    for task_id, broken_floor, good_floor in (
        ("qav-held-001-gold-negatives", FLOOR_BROKEN_Q1, FLOOR_GOOD_Q1),
        ("qav-held-002-honest-green", FLOOR_BROKEN_Q2, FLOOR_GOOD_Q2),
    ):
        broken = _fixture_names(FIXTURES_DIR / task_id)
        good = _fixture_names(GOOD_FIXTURES_DIR / task_id)
        assert broken_floor <= broken, f"{task_id}: missing broken fixtures {sorted(broken_floor - broken)}"
        assert good_floor <= good, f"{task_id}: missing good fixtures {sorted(good_floor - good)}"
