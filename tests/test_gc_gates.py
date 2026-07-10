"""Unit battery for harness/gc_gates.py + gc_rows.py (FEAT-EVAL-GC).

Pins the extraction contract, the spec's margin boundary table, the structural
matching-family rule, the truncation-vs-execution diagnostic split, and the
output-dir ownership rule. Synthetic mini-tasks keep this battery fast; the
committed 25-row subsets are exercised by tests/test_gc_verifier_integrity.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import gc_gates, gc_rows
from harness.gc_gates import ExtractionError

# --- Synthetic mini-task helpers ------------------------------------------------------

ROWS = [
    {
        "row_id": "HumanEval-9001",
        "benchmark": "HumanEval",
        "benchmark_task_id": "HumanEval/9001",
        "prompt": 'def add(a, b):\n    """Return a + b."""\n',
        "canonical_solution": "    return a + b\n",
        "test": "def check(candidate):\n    assert candidate(1, 2) == 3\n    assert candidate(-1, 1) == 0\n",
        "entry_point": "add",
    },
    {
        "row_id": "HumanEval-9002",
        "benchmark": "HumanEval",
        "benchmark_task_id": "HumanEval/9002",
        "prompt": 'def double(x):\n    """Return 2 * x."""\n',
        "canonical_solution": "    return 2 * x\n",
        "test": "def check(candidate):\n    assert candidate(3) == 6\n",
        "entry_point": "double",
    },
    {
        "row_id": "mbpp-9003",
        "benchmark": "MBPP",
        "benchmark_task_id": 9003,
        "text": "Write a function neg(x) that returns -x.",
        "code": "def neg(x):\n    return -x\n",
        "test_list": ["assert neg(2) == -2", "assert neg(-5) == 5"],
        "test_setup_code": "",
    },
]


def make_task(tmp_path: Path, name: str = "gc-held-001-humaneval") -> Path:
    task_dir = tmp_path / name
    manifest_rows = []
    for row in ROWS:
        row_bytes = gc_rows.canonical_json_bytes(row)
        row_dir = task_dir / "input" / "rows" / row["row_id"]
        row_dir.mkdir(parents=True)
        (row_dir / "row.json").write_bytes(row_bytes)
        manifest_rows.append({
            "row_id": row["row_id"],
            "benchmark_task_id": row["benchmark_task_id"],
            "sha256": gc_rows.sha256_bytes(row_bytes),
        })
    manifest = {"suite": "gc-heldout", "task_id": name, "rows": manifest_rows}
    (task_dir / "input" / "manifest.json").write_bytes(gc_rows.canonical_json_bytes(manifest))
    return task_dir


def make_sheet(tmp_path: Path, task_dir: Path, *, oracle: bool = False,
               family: tuple[str, str] = ("test-base", "Q4_K_XL"),
               sabotage: set[str] = frozenset(), drop: set[str] = frozenset(),
               diagnostics: dict[str, dict] | None = None) -> Path:
    sheet = tmp_path / "sheet"
    (sheet / "programs").mkdir(parents=True, exist_ok=True)
    candidate = {"oracle": True, "model_id": "oracle-canonical-solutions"} if oracle else {
        "model_id": "unit-test-candidate", "lineage": "synthetic",
        "base_family": family[0], "quant": family[1],
    }
    (sheet / "candidate.json").write_bytes(gc_rows.canonical_json_bytes(candidate))
    for row in ROWS:
        if row["row_id"] in drop:
            continue
        program = gc_rows.canonical_candidate_program(row)
        if row["row_id"] in sabotage:
            program = program.replace("return", "return 1 +")
        (sheet / "programs" / f"{row['row_id']}.py").write_text(program, encoding="utf-8")
    for row_id, diagnostic in (diagnostics or {}).items():
        rows_dir = sheet / "rows"
        rows_dir.mkdir(exist_ok=True)
        (rows_dir / f"{row_id}.json").write_bytes(gc_rows.canonical_json_bytes(diagnostic))
    return sheet


BASELINES = {"families": {"test-base/Q4_K_XL": {"benchmarks": {
    "gc-held-001-humaneval": {"baseline_solved": 3},
}}}}


# --- Extraction contract ---------------------------------------------------------------

def test_single_fence_with_trailing_prose_extracts_the_fence():
    text = "Here you go:\n```python\ndef f():\n    return 1\n```\nHope that helps!"
    assert gc_gates.extract_program(text) == "def f():\n    return 1\n"


def test_first_of_multiple_fences_wins():
    text = "```python\nA = 1\n```\nand also\n```python\nB = 2\n```"
    assert gc_gates.extract_program(text) == "A = 1\n"


def test_py_fence_and_bare_fence_both_extract():
    assert gc_gates.extract_program("```py\nx = 1\n```") == "x = 1\n"
    assert gc_gates.extract_program("```\nx = 2\n```") == "x = 2\n"


def test_bare_parseable_code_is_accepted():
    assert gc_gates.extract_program("def g():\n    return 2\n") == "def g():\n    return 2\n"


def test_prose_only_raises_extraction_error():
    with pytest.raises(ExtractionError):
        gc_gates.extract_program("I am not able to write code today, sorry.")


# --- Margin boundary table (spec Scenario Outline, verbatim) ----------------------------

@pytest.mark.parametrize("baseline,candidate_solved,expect_pass", [
    (20, 20, True),
    (20, 18, True),
    (20, 17, False),
])
def test_margin_boundary_table(tmp_path, baseline, candidate_solved, expect_pass):
    task_dir = make_task(tmp_path)
    grades = {f"row-{i}": {"status": "pass" if i < candidate_solved else "fail",
                           "reason": "x"} for i in range(20)}
    baselines = {"families": {"test-base/Q4_K_XL": {"benchmarks": {
        "gc-held-001-humaneval": {"baseline_solved": baseline}}}}}
    candidate = {"model_id": "m", "base_family": "test-base", "quant": "Q4_K_XL"}
    findings = gc_gates.regression_floor_findings(task_dir, grades, candidate, baselines)
    assert (findings == []) is expect_pass, findings


def test_floor_failure_names_the_lost_rows(tmp_path):
    task_dir = make_task(tmp_path)
    grades = {"row-a": {"status": "fail", "reason": "execution: nonzero-exit"},
              "row-b": {"status": "fail", "reason": "execution: timeout"},
              "row-c": {"status": "fail", "reason": gc_gates.FAIL_NO_PROGRAM},
              "row-d": {"status": "pass", "reason": "ok"}}
    baselines = {"families": {"test-base/Q4_K_XL": {"benchmarks": {
        "gc-held-001-humaneval": {"baseline_solved": 4}}}}}
    candidate = {"model_id": "m", "base_family": "test-base", "quant": "Q4_K_XL"}
    findings = gc_gates.regression_floor_findings(task_dir, grades, candidate, baselines)
    assert findings and "row-a" in findings[0] and "row-c" in findings[0]


# --- Matching-family rule (structural) ---------------------------------------------------

def test_unknown_family_blocks_and_names_the_gap(tmp_path):
    task_dir = make_task(tmp_path)
    candidate = {"model_id": "m", "base_family": "never-measured", "quant": "Q4_K_M"}
    findings = gc_gates.regression_floor_findings(
        task_dir, {"r": {"status": "pass", "reason": "ok"}}, candidate, BASELINES)
    assert findings, "missing family must block"
    assert "never-measured/Q4_K_M" in findings[0]
    assert "additively" in findings[0]
    assert "cross-family" in findings[0]


def test_same_base_different_quant_is_a_different_family(tmp_path):
    task_dir = make_task(tmp_path)
    candidate = {"model_id": "m", "base_family": "test-base", "quant": "Q4_K_M"}
    findings = gc_gates.regression_floor_findings(
        task_dir, {"r": {"status": "pass", "reason": "ok"}}, candidate, BASELINES)
    assert findings and "test-base/Q4_K_M" in findings[0], (
        "a Q4_K_M candidate must never be compared against the Q4_K_XL baseline"
    )


def test_oracle_must_solve_every_row(tmp_path):
    task_dir = make_task(tmp_path)
    grades = {"r1": {"status": "pass", "reason": "ok"},
              "r2": {"status": "fail", "reason": "execution: nonzero-exit"}}
    findings = gc_gates.regression_floor_findings(task_dir, grades, {"oracle": True})
    assert findings and "broken verifier" in findings[0] and "r2" in findings[0]


# --- Grading by execution: diagnostics stay distinct -------------------------------------

def test_grade_rows_oracle_all_pass_via_real_sandbox(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True)
    grades = gc_gates.grade_rows(task_dir, sheet)
    assert gc_gates.solved_count(grades) == len(ROWS)


def test_sabotaged_row_fails_by_execution_not_text(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True, sabotage={"HumanEval-9001"})
    grades = gc_gates.grade_rows(task_dir, sheet)
    assert grades["HumanEval-9001"]["status"] == "fail"
    assert grades["HumanEval-9001"]["reason"].startswith("execution:")
    assert grades["HumanEval-9002"]["status"] == "pass"


def test_truncated_generation_is_a_distinct_diagnostic(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True,
                       diagnostics={"HumanEval-9001": {"finish_reason": "length"}})
    grades = gc_gates.grade_rows(task_dir, sheet)
    assert grades["HumanEval-9001"] == {"status": "fail", "reason": gc_gates.FAIL_TRUNCATED}
    assert grades["HumanEval-9002"]["status"] == "pass", "the run proceeds to the next row"


def test_missing_program_with_diagnostic_is_a_row_fail_not_a_crash(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True, drop={"mbpp-9003"},
                       diagnostics={"mbpp-9003": {"extraction": "prose-only response"}})
    grades = gc_gates.grade_rows(task_dir, sheet)
    assert grades["mbpp-9003"]["status"] == "fail"
    assert grades["mbpp-9003"]["reason"] == gc_gates.FAIL_NO_PROGRAM
    assert grades["mbpp-9003"]["detail"] == "prose-only response"


def test_grader_crash_propagates_as_exception(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True)

    def crashing_run(script):
        raise RuntimeError("grader bug")

    with pytest.raises(RuntimeError, match="grader bug"):
        gc_gates.grade_rows(task_dir, sheet, run=crashing_run)


# --- Answer-sheet contract (G-G1) ---------------------------------------------------------

def test_missing_candidate_record_is_a_contract_finding(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True)
    (sheet / "candidate.json").unlink()
    findings = gc_gates.answer_sheet_findings(task_dir, sheet)
    assert findings and "candidate.json" in findings[0]


def test_unaddressed_row_is_a_contract_finding(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True, drop={"HumanEval-9002"})
    findings = gc_gates.answer_sheet_findings(task_dir, sheet)
    assert any("HumanEval-9002" in f for f in findings)


def test_foreign_row_is_a_contract_finding(tmp_path):
    task_dir = make_task(tmp_path)
    sheet = make_sheet(tmp_path, task_dir, oracle=True)
    (sheet / "programs" / "HumanEval-31337.py").write_text("x = 1\n", encoding="utf-8")
    findings = gc_gates.answer_sheet_findings(task_dir, sheet)
    assert any("HumanEval-31337" in f for f in findings)


# --- Pin integrity (G-G4) -------------------------------------------------------------------

def test_pins_intact_on_a_clean_task(tmp_path):
    assert gc_gates.verify_pins(make_task(tmp_path)) == []


def test_drifted_row_is_named_and_blocks(tmp_path):
    task_dir = make_task(tmp_path)
    path = gc_rows.row_path(task_dir, "HumanEval-9001")
    path.write_text(path.read_text(encoding="utf-8").replace("a + b", "a - b"), encoding="utf-8")
    findings = gc_gates.verify_pins(task_dir)
    assert findings and "HumanEval-9001" in findings[0] and "DRIFTED" in findings[0]


def test_unpinned_row_directory_is_named(tmp_path):
    task_dir = make_task(tmp_path)
    stray = task_dir / "input" / "rows" / "HumanEval-666"
    stray.mkdir()
    (stray / "row.json").write_text("{}", encoding="utf-8")
    findings = gc_gates.verify_pins(task_dir)
    assert findings and "HumanEval-666" in findings[0]


# --- Output-dir ownership (qav §5 rule generalized) -------------------------------------------

def test_foreign_suite_config_refused(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "config.json").write_text(json.dumps({"suite": "coach-heldout"}), encoding="utf-8")
    findings = gc_gates.output_dir_findings(out)
    assert findings and "coach-heldout" in findings[0]


def test_bundle_judgment_verdicts_tree_refused(tmp_path):
    out = tmp_path / "out"
    (out / "verdicts").mkdir(parents=True)
    assert gc_gates.output_dir_findings(out)


def test_fresh_and_own_suite_dirs_accepted(tmp_path):
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    assert gc_gates.output_dir_findings(fresh) == []
    own = tmp_path / "own"
    own.mkdir()
    (own / "config.json").write_text(json.dumps({"suite": "gc-heldout"}), encoding="utf-8")
    assert gc_gates.output_dir_findings(own) == []


# --- Run-level verdict ------------------------------------------------------------------------

def _clean_reports():
    return [{"task_id": t, "rep": r, "contract_findings": [], "floor_findings": []}
            for t in gc_gates.FLOOR_GATE_BY_TASK for r in (1, 2, 3)]


def test_clean_run_passes_the_pre_registered_verdict():
    assert gc_gates.apply_pre_registered_verdict(_clean_reports())["verdict"] == "PASS"


def test_one_bad_rep_fails_the_owning_benchmark_gate_with_disposition():
    reports = _clean_reports()
    reports[4]["floor_findings"] = ["solved 20 < floor 23"]  # mbpp rep
    verdict = gc_gates.apply_pre_registered_verdict(reports)
    assert verdict["verdict"] == "FAIL"
    assert set(verdict["failures"]) == {"G-G3"}
    assert "NO-DEPLOY" in verdict["dispositions"]["G-G3"]


def test_missing_rep_is_invalid_via_g_g1():
    reports = _clean_reports()[:-1]
    verdict = gc_gates.apply_pre_registered_verdict(reports)
    assert verdict["verdict"] == "FAIL"
    assert any("INVALID" in f for f in verdict["failures"]["G-G1"])
    assert "re-run in place" in verdict["failures"]["G-G1"][0]


# --- Transport retries (abort-and-report; ASSUM-011) --------------------------------------------

def test_transport_succeeds_within_the_pinned_retries():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return {"ok": True}

    assert gc_gates.with_transport_retries(flaky) == {"ok": True}
    assert calls["n"] == 3, "2 retries after the first failure is the pinned posture"


def test_transport_aborts_and_reports_after_pinned_retries():
    def always_down():
        raise ConnectionError("endpoint unreachable")

    with pytest.raises(gc_gates.TransportAborted) as excinfo:
        gc_gates.with_transport_retries(always_down)
    assert excinfo.value.attempts == gc_gates.TRANSPORT_RETRIES + 1
    assert "re-run in place" in str(excinfo.value)


# --- Prompt contract (hash-recorded per rep) ---------------------------------------------------

def test_prompts_are_deterministic_and_hashable():
    he_row, mbpp_row = ROWS[0], ROWS[2]
    assert gc_rows.user_prompt(he_row) == gc_rows.user_prompt(he_row)
    assert "def add(a, b):" in gc_rows.user_prompt(he_row)
    assert "assert neg(2) == -2" in gc_rows.user_prompt(mbpp_row), (
        "MBPP rows include the benchmark's reference asserts (ASSUM-009)"
    )
    hashes = gc_rows.prompt_hashes(he_row)
    assert set(hashes) == {"system_sha256", "user_sha256"}
    assert len(hashes["user_sha256"]) == 64
