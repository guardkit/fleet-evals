"""Verifier integrity for the dcl-heldout suite (Phase D / D4).

Additive sibling of the frozen integrity files (all stay byte-identical). The
frozen task-discovery globs (``po-held-*``, ``coach-held-*``, ``qav-held-*``,
``arch-held-*``, ``gc-held-*``) are blind to the ``dcl-held-*`` family BY
CONSTRUCTION. This file owns:

  - the three-sided proof (frozen rules (a)/(b)/(c)): every task's Oracle passes
    its own gate on a bare run; every broken answer sheet fails its owning
    test(s); every good answer sheet passes;
  - the vendored-checker integrity: the ONE checker home at ``harness/dcl/bin/``
    verifies ``sha256sum -c`` and is byte-identical to ``spike/dcl-authoring/bin/``
    (the promotion source) — proven, not asserted;
  - fixture floor lists (grow, never shrink).

Fixtures here are ANSWER SHEETS (the PO_EVAL_OUTPUT_DIR contract): a directory
holding a single ``response.dcl`` (the candidate DCL), plus ``meta.json`` naming
the test(s) a broken sheet must fail.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
DCL_TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("dcl-held-*") if (p / "task.toml").exists())

FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

BIN_DIR = REPO_ROOT / "harness" / "dcl" / "bin"
SPIKE_BIN_DIR = REPO_ROOT / "spike" / "dcl-authoring" / "bin"
VENDORED_BLOBS = ("dcl.wasm", "wasm_exec.js", "LICENSE", "NOTICE")

BROKEN_CASES = [
    (task_id, fixture.name)
    for task_id in DCL_TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]
GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in DCL_TASK_IDS
    for fixture in sorted((GOOD_FIXTURES_DIR / task_id).glob("*"))
    if fixture.is_dir()
]

FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) .*::(\w+)", re.MULTILINE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


# --- Three-sided proof (frozen rules (a)/(b)/(c), applied to dcl-held-*) --------------

def test_dcl_task_family_present():
    assert DCL_TASK_IDS == [
        "dcl-held-001-author-stats",
        "dcl-held-002-author-version",
        "dcl-held-003-author-uptime",
        "dcl-held-004-repair-diagnostics",
    ]


@pytest.mark.parametrize("task_id", DCL_TASK_IDS)
def test_dcl_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task: the
    reference DCL must grade PASS on a bare run (compile-clean + the floors)."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", BROKEN_CASES)
def test_dcl_broken_fixture_fails_its_owner(task_id, fixture_name):
    """(b) A verifier that cannot fail a known-bad answer sheet is broken. The
    gate must exit non-zero AND the exact test(s) meta.json names must fail."""
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
def test_dcl_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate answer sheet is broken too."""
    code, out = run_gate(task_id, GOOD_FIXTURES_DIR / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate sheet:\n{out}"


# --- Vendored-checker integrity (the ONE checker home) -------------------------------

def test_vendored_bin_sha256sums_verify():
    """`sha256sum -c` over the vendored blobs' pinned digests holds."""
    proc = subprocess.run(
        ["sha256sum", "-c", "SHA256SUMS"],
        cwd=BIN_DIR, capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"sha256sum -c failed:\n{proc.stdout}\n{proc.stderr}"


def test_vendored_bin_is_byte_identical_to_spike():
    """The promoted checker home is byte-identical to spike/dcl-authoring/bin/
    (the promotion source) — additivity: the spike copy is untouched."""
    for name in VENDORED_BLOBS + ("SHA256SUMS", "dcl-check.mjs"):
        harness_file = BIN_DIR / name
        spike_file = SPIKE_BIN_DIR / name
        assert harness_file.is_file(), f"missing vendored {name} in harness/dcl/bin/"
        assert spike_file.is_file(), f"missing source {name} in spike/dcl-authoring/bin/"
        assert _sha256(harness_file) == _sha256(spike_file), (
            f"{name}: harness copy is not byte-identical to the spike source"
        )


def test_vendored_bin_sha256sums_match_recorded_digests():
    """Each vendored blob hashes to the digest recorded in SHA256SUMS."""
    recorded = {}
    for line in (BIN_DIR / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, name = line.split()
        recorded[name] = digest
    for name in VENDORED_BLOBS:
        assert name in recorded, f"{name} not pinned in SHA256SUMS"
        assert _sha256(BIN_DIR / name) == recorded[name], f"{name}: digest drift from SHA256SUMS"


# --- Frozen globs stay blind ---------------------------------------------------------

def test_frozen_task_globs_stay_blind_to_dcl_tasks():
    """The frozen suites' discovery globs cannot see dcl-held-* (additive-only
    proof by construction)."""
    for pattern in ("po-held-*", "coach-held-*", "qav-held-*", "arch-held-*", "gc-held-*"):
        overlap = {p.name for p in TASKS_DIR.glob(pattern)} & set(DCL_TASK_IDS)
        assert overlap == set()


# --- Fixture floors (the battery may grow, never shrink) -----------------------------

FLOOR_BROKEN = {
    "dcl-held-001-author-stats": {"invented-actor-kind", "undeclared-outcome", "valid-but-not-a-capability"},
    "dcl-held-002-author-version": {"invented-actor-kind", "undeclared-outcome", "valid-but-not-a-capability"},
    "dcl-held-003-author-uptime": {"invented-actor-kind", "undeclared-outcome", "valid-but-not-a-capability"},
    "dcl-held-004-repair-diagnostics": {"still-broken-actor-kind", "renamed-capability"},
}
FLOOR_GOOD = {
    "dcl-held-001-author-stats": {"minimal-capability"},
    "dcl-held-002-author-version": {"minimal-capability"},
    "dcl-held-003-author-uptime": {"minimal-capability"},
    "dcl-held-004-repair-diagnostics": {"clean-repair"},
}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


@pytest.mark.parametrize("task_id", DCL_TASK_IDS)
def test_dcl_fixture_floor_never_shrinks(task_id):
    broken = _fixture_names(FIXTURES_DIR / task_id)
    good = _fixture_names(GOOD_FIXTURES_DIR / task_id)
    broken_floor = FLOOR_BROKEN[task_id]
    good_floor = FLOOR_GOOD[task_id]
    assert broken_floor <= broken, f"{task_id}: missing broken fixtures {sorted(broken_floor - broken)}"
    assert good_floor <= good, f"{task_id}: missing good fixtures {sorted(good_floor - good)}"
