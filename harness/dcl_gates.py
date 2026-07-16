"""Shared gate logic for the dcl-heldout suite (Phase D / D4).

stdlib-only pure functions in the fleet-evals harness house style (the
``gc_gates`` / ``coach_gates`` idiom): a thin subprocess wrapper over the ONE
vendored DCL checker at ``harness/dcl/bin/`` plus finding-returning gate helpers
the per-task ``test/`` batteries call. There is exactly one checker home — tasks
never reach into ``spike/``.

The grade is the DCL compiler itself: the deterministic, offline, LLM-free WASM
checker (``dcl-check.mjs`` + ``dcl.wasm``), vendored byte-identical from
``spike/dcl-authoring/bin/`` (upstream ``russelleast/Capability-Language`` @
``4f9fbe56``, Apache-2.0). Gates:

  G1  compile-clean — checker ``ok:true``, ``errorCount == 0``, typed exit 0
  G2  structural floor — the blocks a well-formed capability must carry
      (a substring floor, not a parser; the compiler is the schema)
  semantic-preservation floor — for the repair task: the repaired file still
      DECLARES the same capability / intent / outcome / event names it is
      repairing (a declaration floor over the source text)

Every helper fails LOUD on wrong input and never silent-skips: a missing node,
a checker that emits non-JSON, or a wrong artifact all raise or return findings
— none of them green.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

# The ONE vendored checker home (byte-identical to spike/dcl-authoring/bin/).
BIN_DIR = Path(__file__).resolve().parent / "dcl" / "bin"
CHECKER = BIN_DIR / "dcl-check.mjs"
WASM = BIN_DIR / "dcl.wasm"

# The blocks a well-formed capability must carry. ``outcome`` matches both the
# singular ``outcome X`` form and the ``outcomes {`` block form (a substring
# floor, so an empty-but-valid file cannot pass on a technicality).
REQUIRED_BLOCKS = ("capability ", "intent ", "outcome", "lifecycle")

CHECKER_TIMEOUT_S = 120


class CheckerError(RuntimeError):
    """The vendored checker could not be run or did not emit JSON — a harness
    defect (surfaces as an ERROR), never a candidate FAIL."""


def checker_available(bin_dir: Path = BIN_DIR) -> bool:
    """node on PATH and the vendored checker + WASM blob present."""
    return bool(shutil.which("node")) and (bin_dir / "dcl-check.mjs").is_file() and (bin_dir / "dcl.wasm").is_file()


def run_checker(dcl_path: Path, bin_dir: Path = BIN_DIR) -> tuple[dict, int]:
    """Run ``bin/dcl-check.mjs`` on a ``.dcl`` file; return (envelope, exit).

    The fleet-evals ``_run_checker`` idiom: a missing node or a non-JSON stdout
    is a harness defect and raises CheckerError — it is never silently treated
    as a compile failure (that would let a broken grader green a bad file)."""
    node = shutil.which("node")
    if not node:
        raise CheckerError("node is required to run the vendored WASM checker (harness/dcl/bin/dcl-check.mjs)")
    checker = bin_dir / "dcl-check.mjs"
    if not checker.is_file():
        raise CheckerError(f"missing vendored checker {checker}")
    proc = subprocess.run(
        [node, str(checker), str(dcl_path)],
        capture_output=True,
        text=True,
        timeout=CHECKER_TIMEOUT_S,
    )
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise CheckerError(
            f"checker did not emit JSON (exit {proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from exc
    return envelope, proc.returncode


def error_diagnostics(envelope: dict) -> list[dict]:
    return [d for d in envelope.get("diagnostics", []) if d.get("severity") == "error"]


# --- G1: compile-clean ----------------------------------------------------------------

def compile_findings(dcl_path: Path, bin_dir: Path = BIN_DIR) -> list[str]:
    """G1. Empty list ⇒ the file compiles clean (``ok:true``, zero error
    diagnostics, typed exit 0). Warnings are non-fatal (allowed)."""
    envelope, exit_code = run_checker(dcl_path, bin_dir)
    errors = error_diagnostics(envelope)
    findings: list[str] = []
    if envelope.get("ok") is not True:
        findings.append(f"{dcl_path.name}: checker ok is not true; error diagnostics: {errors}")
    if envelope.get("errorCount") != 0:
        findings.append(f"{dcl_path.name}: errorCount != 0: {errors}")
    if exit_code != 0:
        findings.append(f"{dcl_path.name}: checker exit code {exit_code} (expected 0)")
    return findings


def rejects(dcl_path: Path, bin_dir: Path = BIN_DIR) -> list[str]:
    """The false-green guard's positive assertion: a known-bad file MUST be
    rejected — ``ok:false``, at least one error, exit 1. Empty list ⇒ correctly
    rejected; findings ⇒ the grader greened a bad file and is void."""
    envelope, exit_code = run_checker(dcl_path, bin_dir)
    findings: list[str] = []
    if envelope.get("ok") is not False:
        findings.append(f"{dcl_path.name}: known-bad file unexpectedly compiled ok:true")
    if envelope.get("errorCount", 0) < 1:
        findings.append(f"{dcl_path.name}: known-bad file produced no error diagnostics")
    if exit_code != 1:
        findings.append(f"{dcl_path.name}: known-bad file exit {exit_code} (expected 1)")
    return findings


# --- G2: structural floor -------------------------------------------------------------

def structural_findings(source: str, required_blocks: tuple[str, ...] = REQUIRED_BLOCKS) -> list[str]:
    """G2. A light structural floor — the substrings a well-formed capability
    must carry. Not a schema (the compiler is the schema)."""
    missing = [b for b in required_blocks if b not in source]
    if missing:
        return [f"structural floor: missing block(s) {missing}"]
    return []


# --- Semantic-preservation floor (the repair task) ------------------------------------

def declaration_findings(source: str, declarations: tuple[tuple[str, str], ...]) -> list[str]:
    """The repair task's semantic-preservation floor. ``declarations`` is a
    tuple of (keyword, name) pairs the repaired file must still DECLARE — e.g.
    ``("capability", "GetStats")`` requires ``capability GetStats`` to appear as
    a declaration (keyword followed by the name on a word boundary), so a repair
    that renames or drops the capability/intent/outcome/event fails LOUD rather
    than greening a semantics-changing rewrite."""
    findings: list[str] = []
    for keyword, name in declarations:
        pattern = re.compile(rf"\b{re.escape(keyword)}\s+{re.escape(name)}\b")
        if not pattern.search(source):
            findings.append(f"semantic-preservation floor: missing declaration `{keyword} {name}`")
    return findings
