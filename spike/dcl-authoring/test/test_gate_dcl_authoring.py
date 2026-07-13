"""Gate battery for spike/dcl-authoring (DCL SPIKE, S4).

The grade = the DCL compiler itself. We shell out to the vendored WASM checker
(bin/dcl-check.mjs) — the deterministic, offline, LLM-free semantic analyzer the
eval doc §2 proved on this box — and assert the candidate `response.dcl`:
  - compiles (ok:true) with ZERO error diagnostics, and
  - clears a light STRUCTURAL FLOOR (the blocks a /stats capability must carry).

The compiler is a *free deterministic grader*: the thing a hand-built suite would
have to author, DCL ships. The false-green guard (test_broken_fixture_is_rejected)
proves the grader actually fails a known-bad file — a grader that greens everything
is worthless, so we pin that it does not.

SPIKE-CLASS — NOT a frozen suite, no thresholds implied; freeze = Rich's call
post-spike.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

# The blocks a well-formed /stats capability must carry. `outcome` matches both the
# singular `outcome X` form (used by the /stats capability) and the `outcomes {` block
# form (used by the repo README example) — a substring floor, not a parser.
REQUIRED_BLOCKS = ("capability ", "intent ", "outcome", "lifecycle")


def _run_checker(bin_dir: Path, dcl_path: Path) -> tuple[dict, int]:
    """Run bin/dcl-check.mjs on a .dcl file; return (parsed envelope, exit code)."""
    node = shutil.which("node")
    assert node, "node is required to run the vendored WASM checker (bin/dcl-check.mjs)"
    proc = subprocess.run(
        [node, str(bin_dir / "dcl-check.mjs"), str(dcl_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as e:  # pragma: no cover - defensive
        raise AssertionError(
            f"checker did not emit JSON (exit {proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from e
    return envelope, proc.returncode


def test_checker_available(bin_dir):
    """Pre-grade: the vendored checker + WASM blob are present and node can reach them."""
    assert (bin_dir / "dcl-check.mjs").is_file(), "missing bin/dcl-check.mjs"
    assert (bin_dir / "dcl.wasm").is_file(), "missing bin/dcl.wasm"
    assert shutil.which("node"), "node not on PATH"


def test_candidate_exists(response_path):
    """The candidate must produce exactly one file named response.dcl in its output dir."""
    assert response_path.is_file(), f"no candidate DCL at {response_path}"


def test_candidate_compiles_zero_errors(bin_dir, response_path):
    """G1: the candidate DCL compiles clean — ok:true AND zero error diagnostics
    AND the checker's typed exit code is 0. Warnings are allowed (non-fatal)."""
    envelope, exit_code = _run_checker(bin_dir, response_path)
    diags = envelope.get("diagnostics", [])
    errors = [d for d in diags if d.get("severity") == "error"]
    assert envelope.get("ok") is True, f"ok is not true; error diagnostics: {errors}"
    assert envelope.get("errorCount") == 0, f"errorCount != 0: {errors}"
    assert exit_code == 0, f"checker exit code {exit_code} (expected 0)"


def test_candidate_structural_floor(response_path):
    """G2: a light structural floor — the candidate declares a capability with an
    intent, at least one outcome, and a lifecycle. Not a schema (the compiler is the
    schema); a floor so an empty-but-valid file cannot pass on a technicality."""
    source = response_path.read_text(encoding="utf-8")
    missing = [b for b in REQUIRED_BLOCKS if b not in source]
    assert missing == [], f"structural floor: missing block(s) {missing}"


def test_broken_fixture_is_rejected(bin_dir):
    """FALSE-GREEN GUARD (the false-green corpus pattern): the permanent known-bad
    fixture (undefined actor/shape + a when-branch naming an undeclared outcome) MUST
    fail — ok:false, at least one error, exit 1. If this ever passes, the grader is a
    false-green and this suite is void."""
    fixture = Path(__file__).resolve().parent / "fixtures" / "broken.dcl"
    assert fixture.is_file(), f"missing known-bad fixture {fixture}"
    envelope, exit_code = _run_checker(bin_dir, fixture)
    assert envelope.get("ok") is False, "known-bad fixture unexpectedly compiled ok:true"
    assert envelope.get("errorCount", 0) >= 1, "known-bad fixture produced no errors"
    assert exit_code == 1, f"known-bad fixture exit {exit_code} (expected 1)"
