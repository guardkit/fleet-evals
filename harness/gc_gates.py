"""Grading + verdict harness for the gc-heldout suite (FEAT-EVAL-GC / OBS-7).

stdlib-only pure functions returning structured findings (the coach_gates /
qav_gates house style). Verdicts come from EXECUTED reference assertions in the
gc sandbox — never from text matching. Gate map (PROPOSED until the scope-doc
freeze; gc-heldout-suite-scope.md):

  G-G1  run validity + extraction contract — answer-sheet completeness; every
        response grades (unparseable/truncated = row FAIL, never INVALID);
        grader crashes surface as exceptions (harness defect), not row FAILs
  G-G2  HumanEval regression floor — solved >= baseline − REGRESSION_MARGIN_ROWS
  G-G3  MBPP regression floor — same rule, other benchmark
  G-G4  sandbox + pin integrity (standing, pre-grade) — content pins verified,
        sandbox self-test green; a failure BLOCKS GRADING, not the candidate

MATCHING-FAMILY RULE (structural, the coach-ft-v3 Q4_K_M vs Q4_K_XL lesson):
a candidate is only ever compared against a frozen baseline of its own
base + quant family; no matching record ⇒ grading is blocked with the gap
named and routed to "measure a baseline additively" — never a cross-family
comparison.
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from harness import gc_rows

# PROPOSED freeze values (single source; Rich freezes on the scope doc).
REGRESSION_MARGIN_ROWS = 2
REPS = 3
GENERATION_TIMEOUT_S = 300
TRANSPORT_RETRIES = 2  # per model call, then abort-and-report (RETRIES_PER_REP kin)

SUITE = "gc-heldout"
BASELINES_PATH = Path(__file__).resolve().parent / "gc_baselines.json"

_FENCE = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.DOTALL)

# Row FAIL reasons (G-G1 diagnostics; distinct surfaces, never conflated)
FAIL_TRUNCATED = "truncated-generation"
FAIL_NO_PROGRAM = "no-extractable-program"


class ExtractionError(ValueError):
    """No candidate program can be extracted from a model response."""


# --- Extraction contract (pinned) -----------------------------------------------------

def extract_program(text: str) -> str:
    """First fenced code block; else the raw text iff it parses as Python;
    else ExtractionError. Trailing prose after a fence is tolerated."""
    match = _FENCE.search(text)
    if match:
        return match.group(1)
    stripped = text.strip()
    if stripped:
        try:
            ast.parse(stripped)
            return stripped + "\n"
        except SyntaxError:
            pass
    raise ExtractionError("no fenced code block and the response is not parseable Python")


# --- G-G4: content pins ---------------------------------------------------------------

def verify_pins(task_dir: Path) -> list[str]:
    """Every pinned row's bytes hash to its manifest pin; the manifest and the
    on-disk row set agree; row ids are unique. Any finding blocks grading
    before a model is called."""
    findings: list[str] = []
    try:
        manifest = gc_rows.load_manifest(task_dir)
    except (OSError, ValueError) as exc:
        return [f"{task_dir.name}: manifest unreadable ({exc})"]
    ids = [entry["row_id"] for entry in manifest["rows"]]
    if len(ids) != len(set(ids)):
        findings.append(f"{task_dir.name}: duplicate row ids in manifest")
    for entry in manifest["rows"]:
        path = gc_rows.row_path(task_dir, entry["row_id"])
        if not path.is_file():
            findings.append(f"{entry['row_id']}: pinned row MISSING on disk")
            continue
        digest = gc_rows.sha256_bytes(path.read_bytes())
        if digest != entry["sha256"]:
            findings.append(
                f"{entry['row_id']}: content DRIFTED from its pin "
                f"(manifest {entry['sha256'][:12]}…, on disk {digest[:12]}…)"
            )
    rows_root = task_dir / "input" / "rows"
    on_disk = {p.name for p in rows_root.iterdir() if p.is_dir()} if rows_root.is_dir() else set()
    for stray in sorted(on_disk - set(ids)):
        findings.append(f"{stray}: row directory present but not pinned in the manifest")
    return findings


# --- Answer sheets (the PO_EVAL_OUTPUT_DIR contract) -----------------------------------

def load_candidate(output_dir: Path) -> dict:
    return json.loads((output_dir / "candidate.json").read_text(encoding="utf-8"))


def is_oracle(candidate: dict) -> bool:
    return bool(candidate.get("oracle"))


def family_key(candidate: dict) -> str:
    return f"{candidate['base_family']}/{candidate['quant']}"


def program_path(output_dir: Path, row_id: str) -> Path:
    return output_dir / "programs" / f"{row_id}.py"


def row_diagnostic(output_dir: Path, row_id: str) -> dict | None:
    path = output_dir / "rows" / f"{row_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def answer_sheet_findings(task_dir: Path, output_dir: Path) -> list[str]:
    """G-G1 (contract half): candidate record present and well-formed; every
    manifest row is addressed (a program, or a diagnostic recording why not);
    no foreign rows."""
    findings: list[str] = []
    try:
        candidate = load_candidate(output_dir)
    except (OSError, ValueError) as exc:
        return [f"candidate.json missing/unparseable in {output_dir} ({exc}) — "
                "per-rep records are incomplete (INVALID, not a candidate failure)"]
    if not is_oracle(candidate):
        for field in ("model_id", "base_family", "quant"):
            if not candidate.get(field):
                findings.append(
                    f"candidate.json lacks {field!r} — the matching-family rule "
                    "cannot be applied without it"
                )
    row_ids = set(gc_rows.manifest_row_ids(task_dir))
    for row_id in sorted(row_ids):
        if not program_path(output_dir, row_id).is_file() and row_diagnostic(output_dir, row_id) is None:
            findings.append(
                f"{row_id}: neither a program nor a diagnostic record — "
                "the rep's records are incomplete for this row"
            )
    programs_root = output_dir / "programs"
    on_sheet = {p.stem for p in programs_root.glob("*.py")} if programs_root.is_dir() else set()
    for stray in sorted(on_sheet - row_ids):
        findings.append(f"{stray}: program present for a row that is not in the pinned manifest")
    return findings


# --- Grading by execution (G-G1 body; feeds G-G2/G-G3) ---------------------------------

def grade_rows(task_dir: Path, output_dir: Path, run=None) -> dict[str, dict]:
    """One definite verdict per pinned row, from executed reference assertions.

    Row FAIL surfaces (all distinct, all recorded):
      - truncated-generation (finish_reason == "length"; diagnostic, pre-execution)
      - no-extractable-program (nothing to execute)
      - execution: <reason> (the program ran and failed its assertions/limits)
    A bug in the grader itself raises — pytest ERROR, the harness-defect route.
    """
    if run is None:
        from harness import gc_sandbox
        run = gc_sandbox.run_program
    grades: dict[str, dict] = {}
    for row_id in gc_rows.manifest_row_ids(task_dir):
        diagnostic = row_diagnostic(output_dir, row_id)
        if diagnostic and diagnostic.get("finish_reason") == "length":
            grades[row_id] = {"status": "fail", "reason": FAIL_TRUNCATED}
            continue
        path = program_path(output_dir, row_id)
        if not path.is_file():
            detail = (diagnostic or {}).get("extraction", "no program file")
            grades[row_id] = {"status": "fail", "reason": FAIL_NO_PROGRAM, "detail": detail}
            continue
        row = gc_rows.load_row(task_dir, row_id)
        script = gc_rows.execution_script(row, path.read_text(encoding="utf-8"))
        result = run(script)
        if result.status == "pass":
            grades[row_id] = {"status": "pass", "reason": "ok"}
        else:
            grades[row_id] = {"status": "fail", "reason": f"execution: {result.reason}"}
    return grades


def solved_count(grades: dict[str, dict]) -> int:
    return sum(1 for g in grades.values() if g["status"] == "pass")


# --- Matching-family baselines + regression floor (G-G2/G-G3) ---------------------------

def load_baselines(path: Path | None = None) -> dict:
    return json.loads((path or BASELINES_PATH).read_text(encoding="utf-8"))


def resolve_baseline(candidate: dict, task_id: str, baselines: dict) -> tuple[int | None, list[str]]:
    """STRUCTURAL matching-family rule. Returns (baseline_solved, findings);
    findings non-empty ⇒ grading is blocked for this candidate."""
    key = family_key(candidate)
    family = baselines.get("families", {}).get(key)
    if family is None:
        return None, [
            f"no frozen baseline for family {key!r} — grading is BLOCKED. "
            f"Measure this family's base-model baseline additively first "
            f"(docs/runbooks/gc-heldout-baseline-run.md); a cross-family "
            f"comparison is never performed (the coach-ft-v3 Q4_K_M vs Q4_K_XL lesson)."
        ]
    benchmark = family.get("benchmarks", {}).get(task_id)
    if benchmark is None:
        return None, [
            f"family {key!r} has no baseline record for {task_id} — grading is "
            f"BLOCKED; complete the family's baseline additively."
        ]
    return int(benchmark["baseline_solved"]), []


def regression_floor_findings(
    task_dir: Path, grades: dict[str, dict], candidate: dict,
    baselines: dict | None = None, margin: int = REGRESSION_MARGIN_ROWS,
) -> list[str]:
    """G-G2/G-G3 for one rep. Oracle sheets must solve every row (§3.5: a task
    whose Oracle fails is a broken verifier). Candidates must solve at least
    baseline − margin rows of the matching family's baseline; failing rows are
    NAMED (the NO-DEPLOY record requires them)."""
    total = len(grades)
    solved = solved_count(grades)
    failed_rows = sorted(r for r, g in grades.items() if g["status"] != "pass")
    if is_oracle(candidate):
        if solved != total:
            return [
                f"ORACLE solved {solved}/{total} — broken verifier, not a hard task; "
                f"failing rows: {failed_rows}"
            ]
        return []
    if baselines is None:
        baselines = load_baselines()
    baseline_solved, findings = resolve_baseline(candidate, task_dir.name, baselines)
    if findings:
        return findings
    floor = baseline_solved - margin
    if solved < floor:
        return [
            f"{task_dir.name}: solved {solved} < floor {floor} "
            f"(baseline {baseline_solved} − margin {margin}) — regression beyond the "
            f"frozen margin; lost rows: {failed_rows}"
        ]
    return []


# --- Run-level pre-registered verdict ---------------------------------------------------

DISPOSITIONS = {
    "G-G1": "serving/harness defect route — fix transport/extraction/records and re-grade; "
            "not a training-data verdict",
    "G-G2": "NO-DEPLOY — forgetting measured on HumanEval; failing rows named in RESULTS",
    "G-G3": "NO-DEPLOY — forgetting measured on MBPP; failing rows named in RESULTS",
    "G-G4": "BLOCK GRADING — repair harness/pins, then grade (candidate unjudged)",
}

FLOOR_GATE_BY_TASK = {
    "gc-held-001-humaneval": "G-G2",
    "gc-held-002-mbpp": "G-G3",
}


def apply_pre_registered_verdict(rep_reports: list[dict]) -> dict:
    """rep_reports: one entry per (task, rep) with keys task_id, rep,
    contract_findings (G-G1), floor_findings (G-G2/G-G3). All REPS reps of both
    tasks must be present and clean — 3/3, per benchmark. Returns the verdict
    with failing gates and their pre-registered dispositions."""
    expected = {(t, r) for t in FLOOR_GATE_BY_TASK for r in range(1, REPS + 1)}
    seen = {(e["task_id"], e["rep"]) for e in rep_reports}
    failures: dict[str, list[str]] = {}
    if seen != expected:
        missing = sorted(expected - seen)
        failures.setdefault("G-G1", []).append(
            f"run INVALID: missing rep records {missing} — re-run in place, never skip"
        )
    for entry in rep_reports:
        label = f"{entry['task_id']} rep {entry['rep']}"
        for finding in entry.get("contract_findings", []):
            failures.setdefault("G-G1", []).append(f"{label}: {finding}")
        for finding in entry.get("floor_findings", []):
            gate = FLOOR_GATE_BY_TASK[entry["task_id"]]
            failures.setdefault(gate, []).append(f"{label}: {finding}")
    verdict = "PASS" if not failures else "FAIL"
    return {
        "verdict": verdict,
        "failures": failures,
        "dispositions": {gate: DISPOSITIONS[gate] for gate in failures},
    }


# --- Transport retries (runner-side; ASSUM-011) ------------------------------------------

class TransportAborted(RuntimeError):
    """A model call failed TRANSPORT_RETRIES + 1 times — the rep aborts and
    reports; no fabricated or empty response is ever graded."""

    def __init__(self, attempts: int, last_error: BaseException):
        super().__init__(
            f"transport failed after {attempts} attempts "
            f"({type(last_error).__name__}: {last_error}) — rep aborts; "
            f"re-run in place (INVALID, not a failure)"
        )
        self.attempts = attempts
        self.last_error = last_error


def with_transport_retries(call, retries: int = TRANSPORT_RETRIES):
    """Run ``call()`` with the pinned retry posture: ``retries`` retries after
    the first failure, then abort-and-report via TransportAborted."""
    last: BaseException | None = None
    attempts = retries + 1
    for _ in range(attempts):
        try:
            return call()
        except Exception as exc:  # noqa: BLE001 — transport layer: record, retry, then abort
            last = exc
    raise TransportAborted(attempts, last)


# --- Output-dir ownership (the qav §5 rule generalized) ---------------------------------

def output_dir_findings(out_dir: Path) -> list[str]:
    """A gc-heldout run refuses to start against another suite's records."""
    findings: list[str] = []
    config = out_dir / "config.json"
    if config.is_file():
        try:
            suite = json.loads(config.read_text(encoding="utf-8")).get("suite")
        except ValueError:
            suite = None
        if suite != SUITE:
            findings.append(
                f"{out_dir} already holds run records for suite {suite!r} — refusing "
                f"to reuse another suite's output directory"
            )
    if (out_dir / "verdicts").is_dir():
        findings.append(
            f"{out_dir} contains a verdicts/ tree (bundle-judgment suite records) — "
            f"refusing to reuse another suite's output directory"
        )
    return findings
