"""Verifier integrity for the arch-heldout suite (FEAT-EVAL-ARCH).

Additive sibling of the frozen tests/test_verifier_integrity.py, the frozen
tests/test_idea_verifier_integrity.py, and tests/test_spec_verifier_integrity.py
(all stay byte-identical). The frozen file's task discovery globs
``tasks/po-held-*`` only, so the arch-held-* family is invisible to it BY
CONSTRUCTION — the frozen parametrization cannot change. Everything the
frozen files would have owned therefore lands here:

  - Oracle / broken-fixture / good-fixture discovery for the arch-held-*
    tasks (the three-sided proof, frozen rules (a)/(b)/(c) applied verbatim);
  - the new instrument: the seeded-flaw anchors (compile, one group per
    seeded flaw, goals/manifest-disjoint so restating the inputs earns
    nothing, every group demonstrably catchable on the Oracle);
  - the taxonomy pin (review pattern enum = definitions.yaml @ ed2cfe5 ids
    + MISSING_SEAM, no drift);
  - fixture floor lists (idea-extension scope §2.7, carried over: the
    battery may grow, never shrink below the registered floor).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from harness import arch_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
ARCH_TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("arch-held-*") if (p / "task.toml").exists())
T001 = TASKS_DIR / "arch-held-001-adversarial-review"

FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

BROKEN_CASES = [
    (task_id, fixture.name)
    for task_id in ARCH_TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]
GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in ARCH_TASK_IDS
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


# --- Three-sided proof (frozen rules (a)/(b)/(c), applied to arch-held-*) ---------

def test_arch_task_family_present():
    assert ARCH_TASK_IDS == [
        "arch-held-001-adversarial-review",
        "arch-held-002-sound-design-review",
    ]


@pytest.mark.parametrize("task_id", ARCH_TASK_IDS)
def test_arch_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", BROKEN_CASES)
def test_arch_broken_fixture_fails_its_owner(task_id, fixture_name):
    """(b) A verifier that cannot fail a known-bad review is also broken."""
    fixture_dir = FIXTURES_DIR / task_id / fixture_name
    meta = json.loads((fixture_dir / "meta.json").read_text(encoding="utf-8"))
    code, out = run_gate(task_id, fixture_dir)
    assert code != 0, f"{task_id}/{fixture_name}: gate PASSED a known-bad review"
    failed = set(FAILED_LINE.findall(out))
    missing = [t for t in meta["expect_fail"] if t not in failed]
    assert not missing, (
        f"{task_id}/{fixture_name}: expected {meta['expect_fail']} to fail, "
        f"but only {sorted(failed)} failed:\n{out}"
    )


@pytest.mark.parametrize("task_id,fixture_name", GOOD_CASES)
def test_arch_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate review is broken too."""
    code, out = run_gate(task_id, GOOD_FIXTURES_DIR / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate review:\n{out}"


# --- Instrument: the seeded-flaw anchors -------------------------------------------

def _anchors() -> dict:
    return arch_gates.load_anchors(T001 / "test" / "reference" / "flaw_anchors.json")


def test_flaw_anchors_compile_one_group_per_seeded_flaw():
    compiled = arch_gates.compile_anchors(_anchors())
    assert {g["id"] for g in compiled} == {
        "phantom-reconciliation", "missing-notification-seam",
        "replica-scale-assumption", "gamification-creep",
    }, "one anchor group per seeded flaw in input/design.md"


@pytest.mark.parametrize("input_name", ["goals.md", "repo-manifest.json"])
def test_flaw_anchors_disjoint_from_review_inputs(input_name):
    """A review that merely restates the goals or the manifest must earn
    nothing (kin of the idea-extension input-disjointness rule): no alternate
    may match the non-design inputs. design.md is exempt by construction —
    it CONTAINS the flaws the anchors describe."""
    text = arch_gates.normalize((T001 / "input" / input_name).read_text(encoding="utf-8"))
    for group in arch_gates.compile_anchors(_anchors()):
        for rx in group["patterns"]:
            assert not rx.search(text), (
                f"anchor group {group['id']!r} pattern {rx.pattern!r} matches {input_name}"
            )


def test_every_flaw_group_fires_on_the_oracle():
    """A group that cannot fire is dead instrument; the Oracle is the
    catchability demonstration (one finding per flaw, no stuffing)."""
    review = arch_gates.load_review(T001 / "solution")
    fired = arch_gates.fired_groups(review, _anchors())
    all_ids = {g["id"] for g in arch_gates.compile_anchors(_anchors())}
    assert fired == all_ids, f"groups that never fired: {sorted(all_ids - fired)}"


def test_stuffed_finding_credits_nothing():
    """Anti-stuffing carried from the frozen idea gate (§2.4, threshold
    imported): the stuffed-finding fixture's keyword salad fires >2 groups in
    one finding and therefore credits zero."""
    review = arch_gates.load_review(
        FIXTURES_DIR / "arch-held-001-adversarial-review" / "stuffed-finding")
    assert arch_gates.fired_groups(review, _anchors()) == set()
    # sanity: without the stuffing rule the same finding would credit >2 groups
    unbounded = arch_gates.fired_groups(review, _anchors(), stuffing_max=99)
    assert len(unbounded) > 2, "fixture no longer stuffed — rebuild it"


def test_taxonomy_pin():
    """The review pattern enum stays pinned: the 7 definitions.yaml
    detection_patterns ids (specialist-agent @ ed2cfe5) + MISSING_SEAM (this
    suite's addition for the player.md flow-trace duty). Drift here silently
    fragments every downstream aggregation over pattern ids."""
    assert arch_gates.DETECTION_PATTERNS == (
        "PHANTOM", "UNGROUNDED", "SCOPE_CREEP", "MISSING_TRADEOFF",
        "SOURCE_COLLAPSE", "DOMAIN_DILUTION", "UNSTATED_ASSUMPTION",
        "MISSING_SEAM",
    )


def test_002_inputs_shared_with_001():
    """goals + manifest are byte-identical across the pair — the two tasks
    differ ONLY in the design under review, so a verdict split between them
    isolates judgment, not input drift."""
    t002 = TASKS_DIR / "arch-held-002-sound-design-review"
    for name in ("goals.md", "repo-manifest.json"):
        assert (T001 / "input" / name).read_bytes() == (t002 / "input" / name).read_bytes(), name
    assert (T001 / "input" / "design.md").read_bytes() != (t002 / "input" / "design.md").read_bytes()


# --- Fixture floors (§2.7: the battery may grow, never shrink) ---------------------

FLOOR_BROKEN_001 = {
    "accepts-without-stress-test", "partial-catch", "stuffed-finding",
    "invalid-pattern-id", "malformed-json",
}
FLOOR_GOOD_001 = {"paraphrase-catch", "extra-advisory-finding"}
FLOOR_BROKEN_002 = {"fabricated-blocker", "hedged-approve"}
FLOOR_GOOD_002 = {"minimal-approve", "approve-with-notes"}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_arch_fixture_floor_never_shrinks():
    for task_id, broken_floor, good_floor in (
        ("arch-held-001-adversarial-review", FLOOR_BROKEN_001, FLOOR_GOOD_001),
        ("arch-held-002-sound-design-review", FLOOR_BROKEN_002, FLOOR_GOOD_002),
    ):
        broken = _fixture_names(FIXTURES_DIR / task_id)
        good = _fixture_names(GOOD_FIXTURES_DIR / task_id)
        assert broken_floor <= broken, f"{task_id}: missing broken fixtures {sorted(broken_floor - broken)}"
        assert good_floor <= good, f"{task_id}: missing good fixtures {sorted(good_floor - good)}"
