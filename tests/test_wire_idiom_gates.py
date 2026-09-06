"""The wire-idiom exam row, proved on its frozen trees (no seat is driven here).

The defect this exam exists for (2026-09-06, planning run d08a58fc): given Rich's
fresh-database sentence, the spec seat wrote two of eight worked examples about the
database — "a new user can be created on a freshly created database", "simultaneous user
creations on a fresh database succeed" — and the routing law could not prove them, so a
person had to send a note. The three tasks ask whether the seat, given a wire-behaviour
sentence, writes every worked example as a request to the endpoint and its reply, so the
law stamps all of them by rule with no note from anyone.

What is proved here, without a model:
  - the gate reads guardkit's own lexer and rules, not a copy;
  - the three briefs carry this weekend's sentences word for word, the target named;
  - each task's solution/ (hand-written in the machine idiom) gets a home for every
    scenario, every one of them from the wire rule;
  - each task's broken/ (three examples rewritten in the schema idiom — a migration, a
    column, a table) fails the gate, and the findings name exactly those titles verbatim
    and the rule that would have been needed;
  - end to end, the real grade exits non-zero on broken/ with ONLY the wire-idiom gate
    failing, and exits 0 on solution/ printing the census line;
  - the four structural gates are po-held-007's own functions, not copies;
  - the frozen integrity test's registration is the task's own broken/ tree, linked.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from harness import spec_gates, wire_idiom_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS = REPO_ROOT / "tasks"
BROKEN_FIXTURES = REPO_ROOT / "tests" / "broken_fixtures"

WIRE_GATE = "test_every_worked_example_can_be_proven_by_rule"
FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) .*::(\w+)", re.MULTILINE)

# The three sentences of the 2026-09-06 spec, rule 27, word for word.
SENTENCES = {
    "po-held-011-wire-idiom-fresh-db": (
        "On a fresh database, creating a user with POST /users answers 201 and "
        "GET /users/count-by-domain answers 200 with the counts by domain, so a new "
        "deployment works without a hand-made column (today both fail because the users "
        "table has no deleted_at column, which the code expects)."
    ),
    "po-held-012-wire-idiom-add-endpoint": (
        "Add a GET /users/active-count endpoint that returns the number of active and "
        "inactive users as separate counts."
    ),
    "po-held-013-wire-idiom-extend-endpoint": (
        "Add pagination to GET /users with a default limit of 10."
    ),
}
TASK_IDS = list(SENTENCES)

# The titles each broken/ tree carries in the schema idiom — the gate must name these, and
# only these, verbatim.
SCHEMA_IDIOM_TITLES = {
    "po-held-011-wire-idiom-fresh-db": {
        "A new user can be created on a freshly created database",
        "The users table carries the deleted_at column after the migration",
        "Simultaneous user creations on a fresh database succeed",
    },
    "po-held-012-wire-idiom-add-endpoint": {
        "The users table has an is_active column",
        "Active rows are counted from the is_active column",
        "The migration can be rolled back without losing user rows",
    },
    "po-held-013-wire-idiom-extend-endpoint": {
        "The users table gains an index on created_at for paging",
        "The page query reads ten rows from the users table by default",
        "The migration leaves the existing users columns unchanged",
    },
}


def _feature_text(tree: Path) -> str:
    return spec_gates.spec_paths(tree)["feature"].read_text(encoding="utf-8")


def run_gate(task_id: str, output_dir: Path | None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PO_EVAL_OUTPUT_DIR"}
    if output_dir is not None:
        env["PO_EVAL_OUTPUT_DIR"] = str(output_dir)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TASKS / task_id / "test"), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    return proc.returncode, proc.stdout + proc.stderr


# --- the instrument reads guardkit, not a copy ------------------------------------

def test_gate_reads_guardkits_own_rules_not_a_copy():
    """If the rules move, this gate moves with them. A copied rule set would drift from
    the one the plan stage's pre-commit stamping enforces."""
    from guardkit.orchestrator import stamp_normalizer
    ctx_cls, classify, extract = wire_idiom_gates._guardkit_stamp_rules()
    assert ctx_cls is stamp_normalizer.NormalizeContext
    assert classify is stamp_normalizer.classify_scenario
    assert extract is stamp_normalizer.extract_scenario_blocks


def test_context_is_the_target_repository_with_an_http_surface():
    """Rule 28: rules only, the repository declared as having an HTTP surface — the same
    context the stamping gets on api_test. Read from each task's table, and the
    default when there is no table."""
    for task_id in TASK_IDS:
        ctx = wire_idiom_gates.load_context(TASKS / task_id)
        assert ctx.repo_has_http_surface is True
        assert "api_test" in ctx.http_surface_evidence
        assert not ctx.plan_test_refs, "no plan names test nodes in this exam — R8 never fires"
    assert wire_idiom_gates.load_context(None).repo_has_http_surface is True


# --- the briefs and the task tables -------------------------------------------------

@pytest.mark.parametrize("task_id", TASK_IDS)
def test_brief_carries_the_sentence_verbatim_and_names_the_target(task_id):
    """Rule 27: each brief is one of this weekend's sentences, word for word, with the
    api_test repository named as the target and nothing else added."""
    brief = (TASKS / task_id / "input" / "brief.md").read_text(encoding="utf-8")
    assert SENTENCES[task_id] in brief, f"{task_id}: the brief does not carry the sentence verbatim"
    assert "api_test" in brief, f"{task_id}: the brief does not name the target repository"
    leftover = brief.replace(SENTENCES[task_id], "").replace("Target repository: api_test", "").strip()
    assert leftover == "", f"{task_id}: the brief carries more than the sentence and the target: {leftover!r}"


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_task_table_is_the_ruled_shape(task_id):
    """Rule 27: suite po-heldout-wire-idiom, mode feature-spec, phase auto, the four-file
    contract, reps 3; graded by pytest over PO_EVAL_OUTPUT_DIR like its siblings."""
    with open(TASKS / task_id / "task.toml", "rb") as f:
        task = tomllib.load(f)
    t = task["task"]
    assert t["id"] == task_id
    assert t["suite"] == "po-heldout-wire-idiom"
    assert t["mode"] == "feature-spec"
    assert t["phase"] == "auto"
    assert t["schema"] == "feature-spec-four-file-contract"
    assert t["reps"] == 3
    assert task["grading"]["command"] == "python3 -m pytest test/ -q"
    assert task["grading"]["output_env"] == "PO_EVAL_OUTPUT_DIR"
    assert task["wire_idiom"]["target_repository"] == "api_test"
    assert task["wire_idiom"]["repo_has_http_surface"] is True


# --- the solution trees: every example has a home, all from the wire rule -----------

@pytest.mark.parametrize("task_id", TASK_IDS)
def test_solution_every_worked_example_has_a_home(task_id):
    ctx = wire_idiom_gates.load_context(TASKS / task_id)
    text = _feature_text(TASKS / task_id / "solution")
    assert wire_idiom_gates.wire_idiom_findings(text, ctx) == []


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_solution_is_entirely_in_the_endpoint_idiom(task_id):
    """The hand-written oracle is the machine idiom throughout: every scenario stamped by
    the wire rule, none by any other rule, none refused. The census the results document
    reads must say so."""
    ctx = wire_idiom_gates.load_context(TASKS / task_id)
    census = wire_idiom_gates.wire_rule_census(_feature_text(TASKS / task_id / "solution"), ctx)
    assert census["scenarios"] >= 8, census
    assert census["by_wire_rule"] == census["scenarios"], census
    assert census["refused"] == [], census
    assert set(census["by_rule"]) == {wire_idiom_gates.WIRE_RULE}, census


# --- the broken trees: the gate fires and names the titles ---------------------------

@pytest.mark.parametrize("task_id", TASK_IDS)
def test_broken_names_each_schema_idiom_title_verbatim(task_id):
    """A gate with no fixture proving it fires is not a gate. The findings name exactly
    the three schema-idiom titles, word for word, and the rule that was needed."""
    ctx = wire_idiom_gates.load_context(TASKS / task_id)
    findings = wire_idiom_gates.wire_idiom_findings(_feature_text(TASKS / task_id / "broken"), ctx)
    assert {f["scenario"] for f in findings} == SCHEMA_IDIOM_TITLES[task_id], findings
    for f in findings:
        assert f["defect"] == "worked_example_cannot_be_proven_by_rule"
        assert f["rule_needed"].startswith(wire_idiom_gates.WIRE_RULE)
        assert f["how_to_write_it"] == wire_idiom_gates.HOW_TO_WRITE_IT


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_broken_census_counts_the_refusals(task_id):
    """The softer measure on the broken tree: five stamped by the wire rule, three refused,
    and the census line names the refused titles so a receipt shows which ones."""
    ctx = wire_idiom_gates.load_context(TASKS / task_id)
    census = wire_idiom_gates.wire_rule_census(_feature_text(TASKS / task_id / "broken"), ctx)
    assert census["scenarios"] == 8
    assert census["by_wire_rule"] == 5
    assert set(census["refused"]) == SCHEMA_IDIOM_TITLES[task_id]
    line = wire_idiom_gates.census_line("x", census)
    assert "5 stamped by the wire rule" in line and "3 refused" in line
    for title in SCHEMA_IDIOM_TITLES[task_id]:
        assert title in line


# --- end to end: the real grade over the real trees ----------------------------------

@pytest.mark.parametrize("task_id", TASK_IDS)
def test_the_grade_fails_the_broken_tree_on_the_wire_gate_alone(task_id):
    """PO_EVAL_OUTPUT_DIR pointing at broken/: exit non-zero, the wire-idiom gate is the
    one that failed, the four reused structural gates and the census check still passed
    (so the failure is attributable), and the refused titles are in the output."""
    from harness.could_not_measure import EXIT_COULD_NOT_MEASURE

    code, out = run_gate(task_id, TASKS / task_id / "broken")
    assert code not in (0, EXIT_COULD_NOT_MEASURE), out[-3000:]
    failed = set(FAILED_LINE.findall(out))
    assert failed == {WIRE_GATE}, f"expected only {WIRE_GATE} to fail, got {sorted(failed)}:\n{out[-3000:]}"
    for title in SCHEMA_IDIOM_TITLES[task_id]:
        assert title in out, f"the grade did not name the refused title {title!r}:\n{out[-3000:]}"


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_the_grade_passes_the_solution_tree_and_prints_the_census(task_id):
    """The default tree (solution/): exit 0 — every bar ran and passed, nothing skipped —
    and the census line is the last thing printed, where a tail-truncated receipt keeps it."""
    code, out = run_gate(task_id, None)
    assert code == 0, f"{task_id}: the Oracle failed its own gate (exit {code}):\n{out[-3000:]}"
    assert "COULD NOT MEASURE" not in out
    assert "8 stamped by the wire rule" in out and "0 refused" in out, out[-2000:]


# --- the four structural gates are po-held-007's own, not copies ----------------------

def test_reused_gates_are_po_held_007s_own_functions():
    gates = wire_idiom_gates.po_held_007_gates(REPO_ROOT)
    assert set(gates) == set(wire_idiom_gates.REUSED_007_GATES)
    expected_file = str(TASKS / "po-held-007-feature-spec" / "test" / "test_gate_po_held_007.py")
    for name, fn in gates.items():
        assert fn.__code__.co_filename == expected_file, f"{name} is not 007's own function"
    # loaded once, handed out again
    assert wire_idiom_gates.po_held_007_gates(REPO_ROOT)["test_digest_conforms"] is gates["test_digest_conforms"]


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_task_module_binds_the_reused_gates_and_defines_no_copy(task_id):
    """Rule 29: reused by import, not copied. The task's test module binds the four names
    from po-held-007 and defines none of them itself."""
    number = task_id.split("-")[2]  # po-held-011-… -> 011
    module = TASKS / task_id / "test" / f"test_gate_po_held_{number}.py"
    source = module.read_text(encoding="utf-8")
    for name in wire_idiom_gates.REUSED_007_GATES:
        assert f"def {name}(" not in source, f"{task_id}: {name} is copied, not imported"
        assert f'{name} = _reused["{name}"]' in source, f"{task_id}: {name} is not bound from po-held-007"


# --- the frozen integrity test's registration ---------------------------------------

@pytest.mark.parametrize("task_id", TASK_IDS)
def test_registered_broken_fixture_is_the_tasks_own_broken_tree(task_id):
    """tests/test_verifier_integrity.py enumerates every po-held-* task and requires a
    broken fixture with a meta.json naming the test that owns the defect. The fixture's
    features/ is a link to the task's broken/ tree, so the two cannot drift."""
    import json
    fixture = BROKEN_FIXTURES / task_id / "schema-idiom"
    meta = json.loads((fixture / "meta.json").read_text(encoding="utf-8"))
    assert meta["expect_fail"] == [WIRE_GATE]
    features = fixture / "features"
    assert features.is_symlink(), "the registration links to the task's broken/ tree rather than copying it"
    assert features.resolve() == (TASKS / task_id / "broken" / "features").resolve()
    assert spec_gates.spec_layout_findings(fixture) == []
