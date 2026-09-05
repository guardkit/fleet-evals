"""The revise-path grader, proved on three answers: honoured, ignored, over-edited.

The defect this exists for (2026-09-05): Rich sent "drop example 3, seven exactly is the
rule" back on a spec card, the seat returned the same six worked examples with example 3
reworded, its coach scored 1.0, and the second card was identical to the first. So the
FIRST thing to prove about this grader is that it fails the answer that really happened —
a gate with no fixture proving it fires is not a gate.

Three answers per note, and each has to land differently:
  honoured    -> PASS, no reasons
  ignored     -> FAIL, and the reason says the note was not acted on
  over-edited -> FAIL, and the reason says something else moved

The reasons are checked as ENGLISH, not as codes: a person reads them off a card.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from harness import revise_gates, spec_gates

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS = REPO_ROOT / "tasks"
GOOD = REPO_ROOT / "tests" / "good_fixtures"
BROKEN = REPO_ROOT / "tests" / "broken_fixtures"

T009 = "po-held-009-spec-revise-drop-example"
T010 = "po-held-010-spec-revise-one-word"

# (task, answer name, tree, expected verdict)
ANSWERS = [
    (T009, "honoured", GOOD / T009 / "note-honoured", True),
    (T009, "ignored", BROKEN / T009 / "note-ignored", False),
    (T009, "over-edited", BROKEN / T009 / "over-edited", False),
    (T010, "honoured", GOOD / T010 / "word-honoured", True),
    (T010, "ignored", BROKEN / T010 / "word-ignored", False),
    (T010, "over-edited", BROKEN / T010 / "over-edited", False),
]


def grade_tree(task_id: str, tree: Path) -> dict:
    note = revise_gates.load_note(TASKS / task_id)
    prior = revise_gates.digest_sentences(
        spec_gates.load_digest(spec_gates.spec_paths(TASKS / task_id / "input" / "prior")["digest"])
    )
    paths = spec_gates.spec_paths(tree)
    produced = revise_gates.digest_sentences(spec_gates.load_digest(paths["digest"]))
    scenarios = spec_gates.parse_feature(paths["feature"].read_text(encoding="utf-8"))["scenarios"]
    return revise_gates.grade(prior, produced, len(scenarios), note)


# --- the headline: PASS / FAIL / FAIL ------------------------------------------

@pytest.mark.parametrize("task_id,name,tree,expected", ANSWERS,
                         ids=[f"{t.split('-')[2]}-{n}" for t, n, _p, _e in ANSWERS])
def test_verdict(task_id, name, tree, expected):
    result = grade_tree(task_id, tree)
    assert result["passed"] is expected, (
        f"{task_id}/{name}: expected {'PASS' if expected else 'FAIL'}, got "
        f"{'PASS' if result['passed'] else 'FAIL'}\n" + "\n".join(result["reasons"]))


@pytest.mark.parametrize("task_id,name,tree,expected", ANSWERS,
                         ids=[f"{t.split('-')[2]}-{n}" for t, n, _p, _e in ANSWERS])
def test_a_pass_gives_no_reasons_and_a_fail_gives_them(task_id, name, tree, expected):
    result = grade_tree(task_id, tree)
    assert bool(result["reasons"]) is (not expected)


# --- the reasons are English a person can act on -------------------------------

def test_the_ignored_answer_is_told_the_note_was_not_acted_on():
    """The real 2026-09-05 answer: six examples back, number three reworded."""
    reasons = grade_tree(T009, BROKEN / T009 / "note-ignored")["reasons"]
    joined = " ".join(reasons)
    assert "should now have 5 sentences. It has 6." in joined
    assert "reworded version of it" in joined
    assert "no fewer than seven" in joined
    assert all(r[0].isupper() and r.rstrip().endswith((".", '"')) for r in reasons), reasons


def test_the_over_edited_answer_is_told_which_sentence_moved():
    reasons = grade_tree(T009, BROKEN / T009 / "over-edited")["reasons"]
    joined = " ".join(reasons)
    assert "Example 2 was not mentioned in the note" in joined
    assert "The list shows the oldest loan first" in joined, "the reason quotes what it read"
    assert "The list is ordered by date" in joined, "and what it now reads"


def test_the_one_word_note_is_not_satisfied_by_an_unchanged_list():
    reasons = grade_tree(T010, BROKEN / T010 / "word-ignored")["reasons"]
    joined = " ".join(reasons)
    assert "Example 2 is unchanged" in joined
    assert "oldest loan first" in joined


def test_a_reason_never_speaks_in_codes():
    """Rich reads these. No defect keys, no check names, no register codes."""
    for task_id, _name, tree, _expected in ANSWERS:
        for reason in grade_tree(task_id, tree)["reasons"]:
            for jargon in ("note_honoured", "nothing_else_changed", "list_and_spec_agree",
                           "defect", "digest", "assert", "None", "{"):
                assert jargon not in reason, f"{task_id}: {reason!r} contains {jargon!r}"


# --- the grader's own edges ----------------------------------------------------

def test_a_dropped_example_that_is_simply_gone_passes_and_a_paraphrase_does_not():
    note = revise_gates.load_note(TASKS / T009)
    prior = ["One.", "Two.", "A member who has borrowed more than seven tools still sees at "
                             "least seven of them in the list.", "Four."]
    honoured = ["One.", "Two.", "Four."]
    paraphrased = ["One.", "Two.", "A member who has borrowed more than seven tools is shown at "
                                   "least seven of them in the list."]
    assert revise_gates.grade(prior, honoured, 3, note)["passed"]
    assert not revise_gates.grade(prior, paraphrased, 3, note)["passed"]


def test_the_list_and_the_specification_have_to_agree_on_how_many_examples():
    note = revise_gates.load_note(TASKS / T009)
    prior = ["One.", "Two.", "Three.", "Four."]
    produced = ["One.", "Two.", "Four."]
    ok = revise_gates.grade(prior, produced, 3, note)
    drifted = revise_gates.grade(prior, produced, 4, note)
    assert ok["passed"]
    assert not drifted["passed"]
    assert "specification file has 4 worked examples" in " ".join(drifted["reasons"])


def test_a_task_without_a_note_is_refused_rather_than_graded_as_a_pass():
    with pytest.raises(ValueError, match="no .revise. table"):
        revise_gates.load_note(TASKS / "po-held-007-feature-spec")


def test_the_note_in_the_prompt_is_the_note_in_the_grade():
    """Both come from task.toml, and the instruction a reader sees quotes the same words —
    the 2026-09-05 defect was a note that reached the model and changed nothing, so a note
    that says two different things in two places is the last thing this exam needs."""
    for task_id in (T009, T010):
        note = revise_gates.load_note(TASKS / task_id)
        instruction = (TASKS / task_id / "instruction.md").read_text(encoding="utf-8")
        assert note["note"] in instruction, (
            f"{task_id}: instruction.md does not quote the note in its own task.toml")


def test_the_runner_puts_the_prior_spec_and_the_note_in_the_prompt():
    """A revise rep whose prompt does not carry the unaccepted spec is measuring a request
    production never sends — the same defect class as grading 007 without the template."""
    sys.path.insert(0, str(REPO_ROOT / "harness"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_po_spec_eval", REPO_ROOT / "harness" / "run_po_spec_eval.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    task_dir = TASKS / T009
    task = module.load_task(task_dir)
    user = module.assemble(task_dir, Path(module.DEFAULT_PROMPTS_ROOT),
                           Path(module.DEFAULT_TEMPLATE_ROOT), task=task)["user"]
    assert "The prior submission was NOT accepted. Resolve this feedback:" in user
    assert task["revise"]["note"] in user
    assert "tool-loan-history_digest.yaml" in user, "the four files that came back are in the prompt"
    assert "still sees at least seven of them" in user, "including the example the note is about"


def test_the_deploy_gate_can_name_both_revise_tasks():
    gate = (REPO_ROOT / "harness" / "run_po_deploy_gate.sh").read_text(encoding="utf-8")
    for task_id in (T009, T010):
        assert task_id in gate, f"{task_id} is not named in the deploy gate"


@pytest.mark.parametrize("task_id", [T009, T010])
def test_the_oracle_passes_its_own_gate(task_id):
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TASKS / task_id / "test"), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, cwd=REPO_ROOT,
        env={k: v for k, v in __import__("os").environ.items() if k != "PO_EVAL_OUTPUT_DIR"},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
