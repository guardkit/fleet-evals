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
        "the PINNED input must be untagged — it is the baseline the spec-preservation "
        "gate compares against (until 2026-08-22 the reason given here was 'Step 11 "
        "tagging is the answer sheet's job'; Step 11 is retired, the assertion is not — "
        "see tasks/po-held-008-feature-plan/STEP-11-NOTE.md)"
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
    (frozen rule (c), applied to tree-shaped artifacts).

    2026-08-22: this used to say `code == 0` and, on any other code, report
    "gate REJECTED a legitimate answer sheet". There are now THREE outcomes, not
    two, and calling the third one a rejection would send the reader to the wrong
    place entirely:

        0   every bar ran and passed        — the fixture proves what it claims
        40  a bar COULD NOT BE MEASURED     — proves nothing either way
        else the gate genuinely rejected it — the verifier is broken

    A pass-side proof that could not measure part of the exam is not a pass-side
    proof, so 40 still fails this test. It fails with the truth on it.
    """
    from harness.could_not_measure import EXIT_COULD_NOT_MEASURE

    code, out = run_gate(task_id, REPO_ROOT / "tests" / "good_fixtures" / task_id / fixture_name)
    if code == EXIT_COULD_NOT_MEASURE:
        block = out.split("COULD NOT MEASURE", 1)[-1][:1500]
        raise AssertionError(
            f"{task_id}/{fixture_name}: the gate did NOT reject this sheet — it could not "
            f"MEASURE part of it, so this fixture proves nothing about the axes that stepped "
            f"aside. This is the honest reading of a real gap, not a regression to undo by "
            f"loosening the check. See docs/research/ideas/po-heldout-spec-extension-scope.md "
            f"§11.6 for the ruling that closes it.\nCOULD NOT MEASURE{block}"
        )
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate answer sheet:\n{out}"


def test_the_007_grade_cannot_exit_zero_when_a_check_skips():
    """THE SAME TRAP AS 008's, CLOSED IN 007 TOO — proved on the real fixtures.

    po-held-007's three quality-bar-seed checks step aside when the graded tree
    carries no `qa/pass-bar-seed-*.yaml`. Every runner grades a rep by pytest's
    exit code, and pytest exits 0 when a test skips, so those three axes were
    written down as PASSED while measuring nothing.

    Measured on this repo's own assets before the fix: all six registered GOOD
    fixtures returned `14 passed, 3 skipped`, exit 0. This test pins the fix
    against the same fixtures, so the trap cannot come back unnoticed.
    """
    from harness.could_not_measure import EXIT_COULD_NOT_MEASURE

    seedless = REPO_ROOT / "tests" / "good_fixtures" / "po-held-007-feature-spec" / "frontier-baseline"
    assert not (seedless / "qa").exists(), (
        "this test needs a tree with NO quality-bar seed; frontier-baseline has grown one — "
        "point it at another seedless fixture, or delete this test if none is left"
    )
    code, out = run_gate("po-held-007-feature-spec", seedless)
    assert code == EXIT_COULD_NOT_MEASURE, (
        f"a 007 grade that skipped three checks exited {code} — the skip-scores-green trap "
        f"is back:\n{out[-3000:]}"
    )
    assert "COULD NOT MEASURE" in out, out[-3000:]
    for node in ("test_seed_wellformed", "test_criteria_observability", "test_negative_path_honesty"):
        assert node in out, f"the grade did not NAME the unmeasured check {node}:\n{out[-3000:]}"


def test_the_007_oracle_still_measures_every_axis():
    """The other half of the same claim: the frozen gold answer DOES carry a seed,
    so the Oracle run measures all seventeen axes and exits 0. If this ever starts
    returning 40, the exam has lost the only tree it can fully grade."""
    code, out = run_gate("po-held-007-feature-spec", None)  # default output dir = solution/
    assert code == 0, f"the 007 Oracle no longer measures every axis (exit {code}):\n{out[-3000:]}"


# --- Fixture floors (§2.7: the battery may grow, never shrink) ---------------------

FLOOR_BROKEN_007 = {
    "stub-sheet", "wrapped-step", "missing-summary", "extra-files",
    "implementation-language", "missing-why", "missing-category-tag",
    "header-drift", "manifest-enum-drift", "confident-assumptions",
    "summary-count-mismatch", "unlicensed-invention", "unlicensed-all-groups",
    "stuffed-license", "annotation-missing", "dangling-scenario-ref", "bom-file",
    "digest-drift",   # 2026-08-21, the four-file re-cut
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
    # 2026-08-22, the re-pointed fifth bar (scenario coverage map). Six firing
    # demos, one per assertion the bar makes. The floor GROWS, never shrinks:
    # the three fixtures built for the retired @task check keep their names and
    # their place and now carry the equivalent coverage-map defect (see each
    # fixture's meta.json "amended" note).
    "no-coverage-map", "paraphrased-scenario-key", "unknown-verifier-home",
    "bare-toolchain-stamp", "feature-files-wrong-path", "routing-law-emitted",
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


# --- Instrument: the scenario coverage map (the re-pointed fifth bar) --------------
#
# Fixture-level proof that the bar can fail lives in the broken-fixture battery above
# (six firing demos + three re-pointed ones), and the frozen
# tests/test_verifier_integrity.py runs each of them. What is proved HERE is the
# things a whole-tree fixture is a clumsy way to prove: that the gate reads its
# vocabulary from guardkit rather than a copy, that the documented shorthand is
# accepted, and that the exact-title rule does not fire on a legitimate map.

def _spec_008() -> str:
    return (T008 / "input" / "features" / SLUG_008 / f"{SLUG_008}.feature").read_text(encoding="utf-8")


def _titles_008() -> list[str]:
    from guardkit.orchestrator.verifier_stamp import extract_scenario_titles
    return list(dict.fromkeys(extract_scenario_titles(_spec_008())))


def _valid_map(**overrides) -> dict:
    data = {
        "feature_files": [f"features/{SLUG_008}/{SLUG_008}.feature"],
        "scenarios": {t: {"verifier": "hurl"} for t in _titles_008()},
    }
    data.update(overrides)
    return data


def test_coverage_gate_reads_guardkits_own_vocabulary_not_a_copy():
    """A copied list of allowed verification homes would drift from the one the
    production loader enforces. The gate imports guardkit's, so it cannot."""
    from guardkit.orchestrator.verifier_stamp import VERIFIER_HOMES
    homes, extract = spec_gates._guardkit_routing_law()
    assert homes is VERIFIER_HOMES
    assert extract(_spec_008()) == _titles_008()


def test_coverage_gate_passes_a_correct_map():
    """The pass side. A map naming the pinned spec and stamping every scenario
    with an allowed home has nothing to report."""
    assert spec_gates.coverage_map_findings(
        _valid_map(), _spec_008(),
        expected_feature_files={f"features/{SLUG_008}/{SLUG_008}.feature"},
    ) == []


def test_coverage_gate_accepts_the_documented_bare_string_shorthand():
    """guardkit's parse_scenario_stamp accepts `"<title>": hurl` as shorthand for
    `{verifier: hurl}`. A gate that rejected it would fail a plan for writing
    something the schema documents as legal."""
    data = _valid_map()
    data["scenarios"] = {t: "hurl" for t in _titles_008()}
    assert spec_gates.coverage_map_findings(data, _spec_008()) == []


def test_coverage_gate_rejects_a_key_that_is_not_a_title_and_shows_the_nearest_one():
    """A key that is not verbatim is rejected, whether it is a mis-copy of a real
    title or a scenario the plan invented — the gate deliberately does NOT claim
    to tell those apart (see `_closest_title`), it reports the nearest real title
    and lets a reader decide in one look."""
    titles = _titles_008()

    mis_copied = titles[4].replace("minimum length", "minimum allowed length")
    assert mis_copied not in titles
    data = _valid_map()
    data["scenarios"] = {(mis_copied if k == titles[4] else k): v
                         for k, v in data["scenarios"].items()}
    hits = [f for f in spec_gates.coverage_map_findings(data, _spec_008())
            if f["defect"] == "scenario_title_not_in_the_specification"]
    assert len(hits) == 1 and hits[0]["key"] == mis_copied
    assert hits[0]["nearest_title_in_the_spec"] == titles[4]
    # the mis-copy leaves the real scenario with nowhere to be proved — the point
    assert {"defect": "scenario_unstamped", "scenario": titles[4]} in \
        spec_gates.coverage_map_findings(data, _spec_008())

    invented = "Searching by employer returns matching members"
    assert invented not in titles
    data = _valid_map()
    data["scenarios"][invented] = {"verifier": "hurl"}
    hits = [f for f in spec_gates.coverage_map_findings(data, _spec_008())
            if f["defect"] == "scenario_title_not_in_the_specification"]
    assert len(hits) == 1 and hits[0]["key"] == invented


def test_coverage_gate_agrees_with_guardkits_own_loader_on_every_stamp_it_rejects():
    """The strongest check available without a live model: for each stamp the gate
    rejects, guardkit's own ScenarioStamp must reject it too. If the exam and the
    production loader ever disagree about what a valid stamp is, the exam is wrong."""
    from guardkit.orchestrator.verifier_stamp import parse_scenario_stamp
    bad_stamps = [
        {"verifier": "manual"},                    # not one of the eight homes
        {"verifier": "toolchain"},                 # toolchain with no named test
        {"verifier": "hurl", "typo_key": "x"},     # unknown key (extra='forbid')
    ]
    title = _titles_008()[0]
    for stamp in bad_stamps:
        data = _valid_map()
        data["scenarios"][title] = stamp
        gate_findings = spec_gates.coverage_map_findings(data, _spec_008())
        assert gate_findings, f"the exam accepted a stamp guardkit rejects: {stamp}"
        with pytest.raises(ValueError):
            parse_scenario_stamp(stamp, scenario=title)


def test_coverage_gate_flags_a_plan_that_switches_the_law_on():
    data = _valid_map(routing_law="enforced")
    defects = {f["defect"] for f in spec_gates.coverage_map_findings(data, _spec_008())}
    assert "routing_law_emitted_by_the_plan" in defects


def test_smoke_scenarios_are_named_separately_when_left_out():
    """The pinned spec marks two scenarios @smoke. Dropping one must produce both
    a general finding and a smoke-specific one, so the loss cannot be skimmed past."""
    tags = spec_gates.spec_scenario_tags(_spec_008())
    smoke = [t for t, tg in tags.items() if "@smoke" in tg]
    assert len(smoke) == 2, smoke
    data = _valid_map()
    del data["scenarios"][smoke[0]]
    findings = spec_gates.coverage_map_findings(data, _spec_008())
    assert {"defect": "smoke_scenario_unstamped", "scenario": smoke[0]} in findings
    assert {"defect": "scenario_unstamped", "scenario": smoke[0]} in findings


def test_the_grade_cannot_exit_zero_when_a_check_skips():
    """THE TRAP THIS LANE EXISTS TO CLOSE, proved end to end.

    Every runner decides whether a graded run passed by looking at pytest's exit
    code, and pytest exits 0 when a test skips. A bar that stepped aside was
    therefore written down as a pass. The 008 grade now refuses to exit 0 if
    anything skipped. Proved by running the real gate over the real reference
    answer with one extra check that cannot measure anything.
    """
    import shutil as _shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "task"
        _shutil.copytree(T008, staged, ignore=_shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        (staged / "test" / "test_zz_cannot_measure.py").write_text(
            "import pytest\n\n\ndef test_a_bar_with_nothing_to_grade():\n"
            "    pytest.skip('the thing this bar grades is not in the tree')\n",
            encoding="utf-8",
        )
        env = {k: v for k, v in os.environ.items() if k != "PO_EVAL_OUTPUT_DIR"}
        env["PYTHONPATH"] = str(REPO_ROOT)
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "test/", "-q", "-p", "no:cacheprovider"],
            cwd=staged, capture_output=True, text=True, env=env,
        )
    assert proc.returncode != 0, (
        "a grade that skipped a check exited 0 — the skip-scores-green trap is back:\n"
        + proc.stdout[-3000:]
    )
    assert "COULD NOT MEASURE" in proc.stdout, proc.stdout[-3000:]
