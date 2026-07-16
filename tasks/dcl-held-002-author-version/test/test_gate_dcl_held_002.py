"""Gate battery for dcl-held-002-author-version (dcl-heldout / D4).

The grade = the DCL compiler itself, via harness.dcl_gates over the ONE vendored
WASM checker (harness/dcl/bin/). Asserts the candidate `response.dcl`:
  - G1: compiles (ok:true) with ZERO error diagnostics and typed exit 0, and
  - G2: clears the STRUCTURAL FLOOR (capability + intent + outcome + lifecycle).
The false-green guard proves the grader fails a known-bad file.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from harness import dcl_gates  # noqa: E402


def test_checker_available():
    assert dcl_gates.checker_available(), "node + harness/dcl/bin/ checker must be available"


def test_candidate_exists(response_path):
    assert response_path.is_file(), f"no candidate DCL at {response_path}"


def test_candidate_compiles_zero_errors(response_path):
    """G1: the candidate DCL compiles clean (ok:true, zero errors, exit 0)."""
    findings = dcl_gates.compile_findings(response_path)
    assert findings == [], f"G1 compile gate: {findings}"


def test_candidate_structural_floor(response_path):
    """G2: a light structural floor — capability + intent + outcome + lifecycle."""
    source = response_path.read_text(encoding="utf-8")
    findings = dcl_gates.structural_findings(source)
    assert findings == [], f"G2 structural floor: {findings}"


def test_broken_fixture_is_rejected():
    """FALSE-GREEN GUARD: the known-bad fixture MUST fail — ok:false, exit 1."""
    fixture = Path(__file__).resolve().parent / "fixtures" / "broken.dcl"
    assert fixture.is_file(), f"missing known-bad fixture {fixture}"
    findings = dcl_gates.rejects(fixture)
    assert findings == [], f"false-green guard: {findings}"
