"""Gate battery for gc-held-002-mbpp (G-G1/G-G3 + the standing G-G4)."""
from harness import gc_gates, gc_rows, gc_sandbox


def test_input_pins_intact(task_dir):
    """G-G4 (standing, pre-grade): every pinned row matches its recorded
    SHA-256; a drifted row blocks grading and is NAMED."""
    assert gc_gates.verify_pins(task_dir) == []


def test_sandbox_isolation_available():
    """G-G4: the sandbox proves every isolation leg before any candidate code
    runs — unavailable isolation refuses loudly, never degrades."""
    gc_sandbox.ensure_available()


def test_answer_sheet_contract(task_dir, output_dir):
    """G-G1 (contract): candidate record well-formed; every pinned row is
    addressed (program or diagnostic); no foreign rows."""
    assert gc_gates.answer_sheet_findings(task_dir, output_dir) == []


def test_rows_grade_by_execution(task_dir, grades):
    """G-G1 (body): every pinned row reaches a definite verdict from executed
    reference assertions; extraction/truncation failures are row FAILs with
    recorded reasons — never a crash, never INVALID."""
    row_ids = set(gc_rows.manifest_row_ids(task_dir))
    assert set(grades) == row_ids
    bad = {r: g for r, g in grades.items()
           if g.get("status") not in ("pass", "fail") or not g.get("reason")}
    assert bad == {}, f"rows without a definite recorded verdict: {bad}"


def test_regression_floor(task_dir, grades, candidate):
    """G-G3: Oracle sheets must solve every row; candidates must be within the
    frozen margin of their OWN base+quant family's baseline (matching-family
    rule structural — a missing baseline blocks with the gap named)."""
    assert gc_gates.regression_floor_findings(task_dir, grades, candidate) == []
