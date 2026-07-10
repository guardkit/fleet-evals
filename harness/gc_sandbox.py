"""Execution sandbox for the gc-heldout suite (FEAT-EVAL-GC / OBS-7).

The ONE sanctioned surface for executing model-generated code in this repo
(gc-heldout-suite-scope.md; ASSUM-008). stdlib-only, no Docker (DF-001 posture).
Threat model is ACCIDENT (infinite loops, stray writes, runaway allocation) —
candidate code comes from our own served checkpoints, not adversaries.

Isolation stack per execution:
  - fresh interpreter: ``python3 -I`` (implies -E -s: no env hooks, no user site)
  - fresh network namespace: ``unshare -rn`` (unprivileged user+net namespaces;
    only a downed loopback exists, so any connection attempt fails immediately)
  - throwaway scratch CWD (program file lives there; removed afterwards, always)
  - scrubbed allowlist environment (no host secrets reach the program)
  - rlimits set pre-exec: CPU, address space, per-UID process count, file size,
    core dumps off
  - wall-clock timeout enforced by killing the whole process group

REFUSE-LOUD: ``ensure_available()`` probes every leg and raises
``SandboxUnavailable`` naming the missing isolation. No caller may fall back to
unsandboxed execution — grading blocks instead (gate G-G4).

Failure-surface separation: candidate failures come back as
``SandboxResult(status="fail", ...)``; bugs in THIS module (or its callers)
raise exceptions, which the gate battery surfaces as pytest ERRORs — the G-G1
harness-defect route, never a candidate FAIL.

Known accepted residuals (recorded in the scope doc §residuals):
  - RLIMIT_NPROC is per-UID: on a busy host any fork/thread from candidate code
    fails immediately. Benchmark solutions are single-threaded pure functions.
  - Filesystem confinement is scratch-CWD scoping, not a mount namespace:
    absolute-path writes are constrained only by host DAC.
"""
from __future__ import annotations

import os
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

# Frozen-suite design rule: these are instrument constants. Raising limits between
# candidates is additive; lowering them reopens the scope doc before the next freeze.
ROW_TIMEOUT_S = 10.0
MEMORY_BYTES = 512 * 1024 * 1024
MAX_PROCESSES = 1
FILE_SIZE_BYTES = 64 * 1024 * 1024
CPU_SECONDS_HEADROOM = 5

UNSHARE = "unshare"
PROGRAM_FILENAME = "program.py"

_ENV_ALLOWLIST_PATH = "/usr/bin:/bin"


class SandboxUnavailable(RuntimeError):
    """A required isolation leg cannot be established on this host.

    Callers must treat this as BLOCK GRADING (G-G4 route) — never degrade to
    unsandboxed execution.
    """


@dataclass
class SandboxResult:
    status: str  # "pass" | "fail"
    reason: str  # "ok" | "nonzero-exit" | "timeout"
    exit_code: int | None
    stdout: str
    stderr: str
    seconds: float


def _scrubbed_env(scratch_dir: str) -> dict[str, str]:
    """Minimal allowlist environment — built fresh, never copied from the host,
    so no host credential or token can leak into candidate code."""
    return {
        "PATH": _ENV_ALLOWLIST_PATH,
        "HOME": scratch_dir,
        "TMPDIR": scratch_dir,
        "LC_ALL": "C.UTF-8",
    }


def _rlimit_preexec(timeout_s: float, memory_bytes: int, max_processes: int):
    def apply_limits() -> None:
        cpu_s = int(timeout_s) + CPU_SECONDS_HEADROOM
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(resource.RLIMIT_NPROC, (max_processes, max_processes))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE_BYTES, FILE_SIZE_BYTES))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    return apply_limits


def run_program(
    program_text: str,
    *,
    timeout_s: float = ROW_TIMEOUT_S,
    memory_bytes: int = MEMORY_BYTES,
    max_processes: int = MAX_PROCESSES,
    unshare_binary: str = UNSHARE,
    interpreter: str | None = None,
) -> SandboxResult:
    """Execute one candidate program under the full isolation stack.

    PASS = exit 0. Everything else is a FAIL with a machine-readable reason.
    Grader-side problems (unshare refusing to start, scratch setup failure)
    raise — they are harness defects, not candidate verdicts.
    """
    interpreter = interpreter or sys.executable
    scratch = tempfile.mkdtemp(prefix="gc-sandbox-")
    try:
        program_path = os.path.join(scratch, PROGRAM_FILENAME)
        with open(program_path, "w", encoding="utf-8") as fh:
            fh.write(program_text)

        argv = [unshare_binary, "-rn", "--", interpreter, "-I", PROGRAM_FILENAME]
        t0 = time.monotonic()
        proc = subprocess.Popen(
            argv,
            cwd=scratch,
            env=_scrubbed_env(scratch),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            preexec_fn=_rlimit_preexec(timeout_s, memory_bytes, max_processes),
        )
        try:
            stdout, stderr = proc.communicate(timeout=timeout_s)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_group(proc)
            stdout, stderr = proc.communicate()
        seconds = round(time.monotonic() - t0, 3)

        out = stdout.decode("utf-8", errors="replace")
        err = stderr.decode("utf-8", errors="replace")
        if timed_out:
            return SandboxResult("fail", "timeout", None, out, err, seconds)
        if proc.returncode == 0:
            return SandboxResult("pass", "ok", 0, out, err, seconds)
        return SandboxResult("fail", "nonzero-exit", proc.returncode, out, err, seconds)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _kill_process_group(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()


# --- Availability probe (refuse-loud) ------------------------------------------------

_NETWORK_PROBE = """\
import socket
try:
    socket.create_connection(("1.1.1.1", 80), timeout=3)
except OSError:
    raise SystemExit(0)
raise SystemExit(7)  # connection succeeded: network isolation NOT effective
"""

_RLIMIT_PROBE = """\
import resource
soft, hard = resource.getrlimit(resource.RLIMIT_AS)
raise SystemExit(0 if soft == {memory_bytes} else 7)
"""


def ensure_available(
    *, unshare_binary: str = UNSHARE, interpreter: str | None = None
) -> None:
    """Probe every isolation leg. Raises SandboxUnavailable NAMING the missing
    leg. Callers run this before any candidate code executes (gate conftest,
    runner pre-flight, provisioner)."""
    probes: list[tuple[str, str, str]] = [
        (
            "interpreter execution (unshare -rn + python3 -I)",
            "raise SystemExit(0)",
            "trivial program did not exit 0 — user/network namespaces may be "
            "blocked on this host (check unprivileged userns / AppArmor)",
        ),
        (
            "network isolation (fresh network namespace)",
            _NETWORK_PROBE,
            "an outbound connection SUCCEEDED from inside the sandbox",
        ),
        (
            "resource limits (RLIMIT_AS applied pre-exec)",
            _RLIMIT_PROBE.format(memory_bytes=MEMORY_BYTES),
            "the address-space rlimit was not visible to the sandboxed program",
        ),
    ]
    for leg, probe_program, detail in probes:
        try:
            result = run_program(
                probe_program,
                timeout_s=15.0,
                unshare_binary=unshare_binary,
                interpreter=interpreter,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise SandboxUnavailable(
                f"sandbox isolation unavailable — {leg}: cannot execute probe "
                f"({exc!r}). REFUSING to grade; never degrade to unsandboxed execution."
            ) from exc
        if result.status != "pass":
            raise SandboxUnavailable(
                f"sandbox isolation unavailable — {leg}: {detail} "
                f"(probe: {result.reason}, exit={result.exit_code}, "
                f"stderr={result.stderr.strip()[:200]!r}). "
                "REFUSING to grade; never degrade to unsandboxed execution."
            )
