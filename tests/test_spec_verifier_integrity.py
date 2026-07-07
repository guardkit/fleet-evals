"""Verifier integrity for the po-heldout-spec extension (FEAT-EVAL-SPEC).

Additive sibling of the frozen tests/test_verifier_integrity.py and the frozen
tests/test_idea_verifier_integrity.py (both stay byte-identical). The frozen
file already auto-discovers the new tasks' Oracle runs and BROKEN fixtures
(meta.json-keyed). What it cannot know about lands here:

  - the new instruments themselves: invention anchors (compile, one group per
    deliberate unknown, input-disjoint from the brief), the domain-language
    banlist (compile, disjoint from the brief, every group demonstrably able
    to fire), and the plan task's pinned input spec (checksum + structural
    sanity so the spec-preservation gate is meaningful);
  - the plan-side oracle CLI (installed guardkit, pinned identity);
  - GOOD-fixture discovery for tree-shaped answer sheets — the frozen
    good-fixture glob keys on response.txt, which these artifacts do not have
    by design, so the pass-side proof is owned here;
  - fixture floor lists (§2.7 of the idea-extension scope, carried over: the
    battery may grow, never shrink below the registered floor).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from harness import spec_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
T007 = REPO_ROOT / "tasks" / "po-held-007-feature-spec"
T008 = REPO_ROOT / "tasks" / "po-held-008-feature-plan"
SPEC_TASKS = ("po-held-007-feature-spec", "po-held-008-feature-plan")
SLUG_008 = "member-directory-search"


# --- Instrument: invention anchors (007) ---------------------------------------

def test_invention_anchors_compile_one_group_per_unknown():
    anchors = spec_gates.load_anchors(T007 / "test" / "reference" / "invention_anchors.json")
    compiled = spec_gates.compile_anchors(anchors)
    assert len(compiled) == 6, "one anchor group per deliberate unknown in the brief"


def test_invention_anchors_disjoint_from_brief():
    """Input-disjointness (idea-extension scope §2.1, carried over): an anchor
    matching the brief's own text would turn faithful restating into a gate
    failure."""
    brief = spec_gates.normalize((T007 / "input" / "brief.md").read_text(encoding="utf-8"))
    anchors = spec_gates.load_anchors(T007 / "test" / "reference" / "invention_anchors.json")
    for group in spec_gates.compile_anchors(anchors):
        for rx in group["patterns"]:
            assert not rx.search(brief), (
                f"anchor group {group['id']!r} pattern {rx.pattern!r} matches the brief itself"
            )


# --- Instrument: domain-language banlist (007) ----------------------------------

def test_banlist_compiles():
    banlist = spec_gates.load_anchors(T007 / "test" / "reference" / "domain_language_banlist.json")
    compiled = spec_gates.compile_anchors(banlist)
    assert len(compiled) == 5, "http-status / sql / file-path / json-body / tech-internals"


def test_banlist_disjoint_from_brief():
    """A brief containing banned vocabulary would force violations on any
    faithful spec — the instrument must not poison its own input."""
    brief = spec_gates.normalize((T007 / "input" / "brief.md").read_text(encoding="utf-8"))
    banlist = spec_gates.load_anchors(T007 / "test" / "reference" / "domain_language_banlist.json")
    for group in spec_gates.compile_anchors(banlist):
        for rx in group["patterns"]:
            assert not rx.search(brief), (
                f"banlist group {group['id']!r} pattern {rx.pattern!r} matches the brief itself"
            )


# --- Instrument: 008 pinned input spec -------------------------------------------

def test_input_spec_checksum_pinned():
    """The plan task's input triple must not drift after gates are calibrated
    against it (the 006 reference-roadmap pin, carried over)."""
    pins = {}
    for line in (T008 / "input" / "INPUT.sha256").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            pins[name.strip()] = digest
    assert len(pins) == 3, "the three-file triple is pinned"
    for name, digest in pins.items():
        actual = hashlib.sha256((T008 / "input" / name).read_bytes()).hexdigest()
        assert actual == digest, f"input spec drift in {name}"


def test_input_spec_structurally_sane():
    """The pinned input must itself satisfy the spec-side structure the
    preservation gate assumes: parses cleanly, single-line steps, tagged
    categories, a non-empty @smoke set, and >=1 feature-type-ownable
    scenario per category so linkage gates are meaningful."""
    text = (T008 / "input" / "features" / SLUG_008 / f"{SLUG_008}.feature").read_text(encoding="utf-8")
    parsed = spec_gates.parse_feature(text)
    assert parsed["findings"] == [], parsed["findings"]
    assert len(parsed["scenarios"]) >= 8
    assert spec_gates.tag_count(parsed, "@smoke") >= 1
    for tag in spec_gates.CATEGORY_TAGS:
        assert spec_gates.tag_count(parsed, tag) >= 1
    assert not any(t.startswith("@task:") for sc in parsed["scenarios"] for t in sc["tags"]), (
        "the PINNED input must be untagged — Step 11 tagging is the answer sheet's job"
    )


# --- Instrument: the plan-side oracle CLI -----------------------------------------

def test_guardkit_oracle_present():
    """The deterministic plan oracle is the installed guardkit CLI (contract
    §0: resolves to the checkout pinned @ 28587b61). A missing CLI must be an
    instrument error, never a silent skip."""
    exe = shutil.which("guardkit")
    assert exe, (
        "guardkit CLI not on PATH — install ~/.agentecflow/bin/guardkit "
        "(pinned oracle per CONTRACT-feature-spec-plan-outputs.md §0)"
    )
    proc = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr


# --- Good-fixture discovery for tree-shaped sheets ---------------------------------

GOOD_CASES = [
    (task_id, fixture.name)
    for task_id in SPEC_TASKS
    for fixture in sorted((REPO_ROOT / "tests" / "good_fixtures" / task_id).glob("*"))
    if fixture.is_dir()
]

FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) .*::(\w+)", re.MULTILINE)


def run_gate(task_id: str, output_dir: Path | None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PO_EVAL_OUTPUT_DIR"}
    if output_dir is not None:
        env["PO_EVAL_OUTPUT_DIR"] = str(output_dir)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(REPO_ROOT / "tasks" / task_id / "test"),
         "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.mark.parametrize("task_id,fixture_name", GOOD_CASES)
def test_spec_good_fixture_passes(task_id, fixture_name):
    """A verifier that rejects a legitimate serving-acceptable sheet is broken
    (frozen rule (c), applied to tree-shaped artifacts)."""
    code, out = run_gate(task_id, REPO_ROOT / "tests" / "good_fixtures" / task_id / fixture_name)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate answer sheet:\n{out}"


# --- Fixture floors (§2.7: the battery may grow, never shrink) ---------------------

FLOOR_BROKEN_007 = {
    "stub-sheet", "wrapped-step", "missing-summary", "extra-files",
    "implementation-language", "missing-why", "missing-category-tag",
    "header-drift", "manifest-enum-drift", "confident-assumptions",
    "summary-count-mismatch", "unlicensed-invention", "unlicensed-all-groups",
    "stuffed-license", "annotation-missing", "dangling-scenario-ref", "bom-file",
}
FLOOR_GOOD_007 = {
    "frontier-baseline", "licensed-per-group", "box-drawing-dividers",
    "outline-and-docstring", "extra-summary-rows", "compound-licensing",
}
FLOOR_BROKEN_008 = {
    "schema-mutant", "struct-mutant", "missing-task-type", "wrong-wave",
    "mode-mismatch", "dangling-task-tag", "untraced-feature-task",
    "missing-smoke-link", "spec-rewritten", "no-guide", "no-diagrams",
    "missing-lint-criterion", "collapsed-plan", "stub-plan",
}
FLOOR_GOOD_008 = {
    "frontier-baseline", "minimal-plan", "extra-yaml-keys", "alias-task-type",
}


def _fixture_names(root: Path) -> set[str]:
    return {p.name for p in root.iterdir() if p.is_dir()} if root.exists() else set()


def test_007_fixture_floor_never_shrinks():
    broken = _fixture_names(REPO_ROOT / "tests" / "broken_fixtures" / "po-held-007-feature-spec")
    good = _fixture_names(REPO_ROOT / "tests" / "good_fixtures" / "po-held-007-feature-spec")
    assert FLOOR_BROKEN_007 <= broken, f"missing broken fixtures: {sorted(FLOOR_BROKEN_007 - broken)}"
    assert FLOOR_GOOD_007 <= good, f"missing good fixtures: {sorted(FLOOR_GOOD_007 - good)}"


def test_008_fixture_floor_never_shrinks():
    broken = _fixture_names(REPO_ROOT / "tests" / "broken_fixtures" / "po-held-008-feature-plan")
    good = _fixture_names(REPO_ROOT / "tests" / "good_fixtures" / "po-held-008-feature-plan")
    assert FLOOR_BROKEN_008 <= broken, f"missing broken fixtures: {sorted(FLOOR_BROKEN_008 - broken)}"
    assert FLOOR_GOOD_008 <= good, f"missing good fixtures: {sorted(FLOOR_GOOD_008 - good)}"


# --- Per-group firing + licensed demonstrations (§2.7, carried over) ---------------

def _parsed_and_manifest(fixture_root: Path):
    paths = spec_gates.spec_paths(fixture_root)
    parsed = spec_gates.parse_feature(paths["feature"].read_text(encoding="utf-8"))
    manifest = spec_gates.load_assumptions_manifest(paths["assumptions"])
    return parsed, manifest


def test_every_anchor_group_fires_on_the_all_groups_fixture():
    """A group that cannot fire is dead instrument."""
    anchors = spec_gates.load_anchors(T007 / "test" / "reference" / "invention_anchors.json")
    parsed, manifest = _parsed_and_manifest(
        REPO_ROOT / "tests" / "broken_fixtures" / "po-held-007-feature-spec" / "unlicensed-all-groups")
    fired = {f["group"] for f in spec_gates.find_unlicensed_spec_inventions(parsed, manifest, anchors)}
    all_groups = {g["id"] for g in spec_gates.compile_anchors(anchors)}
    assert fired == all_groups, f"groups that never fired: {sorted(all_groups - fired)}"


def test_every_anchor_group_is_licensable_on_the_per_group_fixture():
    """A group that can fire but never license is a topic ban, not a licensing
    check. licensed-per-group asserts every group AND licenses each — zero
    findings."""
    anchors = spec_gates.load_anchors(T007 / "test" / "reference" / "invention_anchors.json")
    parsed, manifest = _parsed_and_manifest(
        REPO_ROOT / "tests" / "good_fixtures" / "po-held-007-feature-spec" / "licensed-per-group")
    groups = spec_gates.compile_anchors(anchors)
    all_ids = {g["id"] for g in groups}
    asserted = {
        g["id"] for g in groups
        if any(spec_gates._first_match(g, spec_gates.normalize(t))
               for _, t in spec_gates.spec_requirement_units(parsed))
    }
    assert asserted == all_ids, f"fixture fails to assert: {sorted(all_ids - asserted)}"
    findings = spec_gates.find_unlicensed_spec_inventions(parsed, manifest, anchors)
    assert findings == [], f"licensed-per-group fixture has unlicensed findings: {findings}"


def test_every_banlist_group_fires_on_the_implementation_language_fixture():
    """Same discipline for the banlist: every group owns a firing demo."""
    banlist = spec_gates.load_anchors(T007 / "test" / "reference" / "domain_language_banlist.json")
    parsed, _ = _parsed_and_manifest(
        REPO_ROOT / "tests" / "broken_fixtures" / "po-held-007-feature-spec" / "implementation-language")
    fired = {f["group"] for f in spec_gates.find_banned_language(parsed, banlist)}
    all_groups = {g["id"] for g in spec_gates.compile_anchors(banlist)}
    assert fired == all_groups, f"banlist groups that never fired: {sorted(all_groups - fired)}"


def test_stuffed_statement_licenses_nothing():
    """Anti-stuffing carried over verbatim (idea gate §2.4): a synthetic
    statement asserting 3 body-asserted groups voids itself."""
    anchors = spec_gates.load_anchors(T007 / "test" / "reference" / "invention_anchors.json")
    parsed, manifest = _parsed_and_manifest(
        REPO_ROOT / "tests" / "broken_fixtures" / "po-held-007-feature-spec" / "stuffed-license")
    findings = spec_gates.find_unlicensed_spec_inventions(parsed, manifest, anchors)
    fired = {f["group"] for f in findings}
    assert {"payment", "notification-channel", "waitlist"} <= fired, (
        f"the keyword-salad statement licensed groups it should not have: fired={sorted(fired)}"
    )
