"""Gate battery for dcl-held-004-repair-diagnostics (dcl-heldout / D4).

The task: given a broken `.dcl` (input/broken.dcl) and the checker's verbatim
diagnostics (input/diagnostics.json), produce a compile-clean REPAIR that
preserves the declared capability semantics. The grade, via harness.dcl_gates
over the ONE vendored WASM checker (harness/dcl/bin/), asserts the candidate
`response.dcl`:
  - G1: compiles (ok:true) with ZERO error diagnostics and typed exit 0, and
  - SEMANTIC-PRESERVATION FLOOR: the repair still DECLARES the same
    capability / intent / outcome / event names it is repairing — a rename or
    drop of the capability being repaired fails LOUD (it is not a repair).

The false-green guard here is the task's own broken input: the compile gate MUST
reject input/broken.dcl (else the gate greens everything and is void).
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness import dcl_gates  # noqa: E402

TASK_DIR = Path(__file__).resolve().parents[1]

# The declarations the repair must preserve (feature facts — the capability being
# repaired). A repair that renames or drops any of these has changed the declared
# semantics and is not a valid repair.
PRESERVED_DECLARATIONS = (
    ("capability", "GetStats"),
    ("intent", "StatsRequest"),
    ("outcome", "StatsRetrieved"),
    ("event", "StatsRetrievedEvent"),
)


def test_checker_available():
    assert dcl_gates.checker_available(), "node + harness/dcl/bin/ checker must be available"


def test_candidate_exists(response_path):
    assert response_path.is_file(), f"no candidate repair at {response_path}"


def test_repair_compiles_zero_errors(response_path):
    """G1: the repaired DCL compiles clean (ok:true, zero errors, exit 0)."""
    findings = dcl_gates.compile_findings(response_path)
    assert findings == [], f"G1 compile gate: {findings}"


def test_repair_preserves_declared_semantics(response_path):
    """SEMANTIC-PRESERVATION FLOOR: the repair still declares the same
    capability / intent / outcome / event names it is repairing."""
    source = response_path.read_text(encoding="utf-8")
    findings = dcl_gates.declaration_findings(source, PRESERVED_DECLARATIONS)
    assert findings == [], f"semantic-preservation floor: {findings}"


def test_broken_input_is_rejected():
    """FALSE-GREEN GUARD: the task's own broken input MUST fail the compile gate
    — ok:false, at least one error, exit 1. If it passes, the gate is void."""
    broken = TASK_DIR / "input" / "broken.dcl"
    assert broken.is_file(), f"missing broken input {broken}"
    findings = dcl_gates.rejects(broken)
    assert findings == [], f"false-green guard: {findings}"
