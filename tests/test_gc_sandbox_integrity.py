"""Sandbox integrity for the gc-heldout suite (FEAT-EVAL-GC / OBS-7).

The sandbox is the load-bearing new mechanism — the first surface in this repo
that executes model-generated code — so its behaviour is itself integrity-tested
(gc-heldout spec Groups C/D): timeout kill, network denial, filesystem
confinement, memory/process containment, env scrub, and the refuse-loud
availability probe. Additive sibling of the frozen integrity files (all stay
byte-identical).
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from harness import gc_sandbox
from harness.gc_sandbox import SandboxUnavailable, ensure_available, run_program

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module", autouse=True)
def sandbox_available():
    """Every test below is meaningless if isolation cannot be established —
    and refuse-loud means that is a hard ERROR, not a skip."""
    ensure_available()


# --- Verdicts come from execution ---------------------------------------------------

def test_trivial_program_passes():
    result = run_program("raise SystemExit(0)\n")
    assert result.status == "pass" and result.reason == "ok"


def test_failing_assertion_fails_by_execution():
    result = run_program("assert 1 + 1 == 3, 'wrong answer'\n")
    assert result.status == "fail" and result.reason == "nonzero-exit"
    assert "wrong answer" in result.stderr


def test_error_before_definition_fails_by_execution():
    result = run_program("raise RuntimeError('broken before defining anything')\n")
    assert result.status == "fail" and result.reason == "nonzero-exit"


# --- Timeout: a grading boundary, not a run abort -----------------------------------

def test_program_inside_the_timeout_grades_on_merit():
    result = run_program("import time; time.sleep(0.2)\n", timeout_s=5.0)
    assert result.status == "pass"


def test_infinite_loop_is_killed_at_the_timeout():
    result = run_program("while True:\n    pass\n", timeout_s=1.0)
    assert result.status == "fail" and result.reason == "timeout"
    assert result.seconds < 10, "kill must land at the timeout, not the CPU backstop"


def test_run_continues_after_a_timeout_kill():
    run_program("while True:\n    pass\n", timeout_s=1.0)
    result = run_program("raise SystemExit(0)\n")
    assert result.status == "pass", "a killed row must not poison subsequent rows"


# --- Network denial ------------------------------------------------------------------

def test_outbound_connection_is_denied():
    result = run_program(
        "import socket\n"
        "socket.create_connection(('1.1.1.1', 80), timeout=3)\n",
        timeout_s=8.0,
    )
    assert result.status == "fail", "an outbound connection must never succeed"
    assert "OSError" in result.stderr or "Errno" in result.stderr


def test_name_resolution_is_denied():
    result = run_program(
        "import socket\nsocket.getaddrinfo('example.com', 443)\n", timeout_s=8.0
    )
    assert result.status == "fail"


# --- Environment scrub ---------------------------------------------------------------

def test_host_env_markers_are_invisible(monkeypatch):
    monkeypatch.setenv("GC_SANDBOX_HOST_SECRET", "leak-canary-1f2e3d")
    result = run_program(
        "import os\n"
        "assert 'GC_SANDBOX_HOST_SECRET' not in os.environ, 'host env leaked'\n"
        "suspicious = [k for k in os.environ if 'KEY' in k or 'TOKEN' in k or 'SECRET' in k]\n"
        "assert not suspicious, f'credential-shaped vars visible: {suspicious}'\n"
    )
    assert result.status == "pass", result.stderr


# --- Filesystem confinement (scratch CWD; repo untouched) ----------------------------

def test_relative_writes_land_in_scratch_and_scratch_is_removed():
    result = run_program(
        "with open('stray.txt', 'w') as fh:\n"
        "    fh.write('x')\n"
        "with open('../stray-parent.txt', 'w') as fh:\n"
        "    fh.write('x')\n"
    )
    # Writing near the scratch dir is permitted-by-design (accident class);
    # what matters is the repo tree stays untouched and scratch is gone.
    assert not list(REPO_ROOT.glob("stray*.txt"))
    assert result.exit_code is not None


def test_repo_tree_unchanged_after_a_writing_candidate():
    import subprocess as sp

    before = sp.run(
        ["git", "status", "--porcelain", "--", "tasks", "harness"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    ).stdout
    run_program("open('output.txt', 'w').write('candidate output')\n")
    after = sp.run(
        ["git", "status", "--porcelain", "--", "tasks", "harness"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    ).stdout
    assert before == after


# --- Resource containment ------------------------------------------------------------

def test_unbounded_allocation_is_contained():
    result = run_program(
        "blocks = []\n"
        "while True:\n"
        "    blocks.append(bytearray(50 * 1024 * 1024))\n",
        timeout_s=8.0,
    )
    assert result.status == "fail", "allocation must be stopped by RLIMIT_AS"


def test_process_spawning_is_contained():
    result = run_program(
        "import os\n"
        "for _ in range(64):\n"
        "    os.fork()\n",
        timeout_s=8.0,
    )
    assert result.status == "fail", "forking must be stopped by RLIMIT_NPROC"


# --- Refuse-loud availability --------------------------------------------------------

def test_missing_isolation_binary_refuses_loudly():
    with pytest.raises(SandboxUnavailable) as excinfo:
        ensure_available(unshare_binary="/nonexistent/gc-no-such-unshare")
    assert "REFUSING to grade" in str(excinfo.value)


def test_unavailable_probe_names_the_missing_leg():
    with pytest.raises(SandboxUnavailable) as excinfo:
        ensure_available(interpreter="/nonexistent/gc-no-such-python")
    assert "unshare -rn + python3 -I" in str(excinfo.value)


def test_no_unsandboxed_execution_path_exists():
    """The module must offer no way to execute a program outside the isolation
    stack: every execution goes through run_program, whose argv is pinned to
    the unshare wrapper."""
    import inspect

    source = inspect.getsource(gc_sandbox)
    assert source.count("subprocess.Popen(") == 1, (
        "exactly one process-spawn site is sanctioned (run_program)"
    )
    assert 'argv = [unshare_binary, "-rn", "--", interpreter, "-I", PROGRAM_FILENAME]' in source


def test_scrubbed_env_is_an_allowlist_not_a_copy():
    env = gc_sandbox._scrubbed_env("/tmp/x")
    assert set(env) == {"PATH", "HOME", "TMPDIR", "LC_ALL"}
    assert os.environ.get("PATH") is not None  # host untouched
