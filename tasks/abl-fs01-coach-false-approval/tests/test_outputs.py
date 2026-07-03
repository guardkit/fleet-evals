"""Independent verifier for abl-fs01 (Coach false-approval regression).

Encodes the regression that originally slipped (scope §3.2): FEAT-MEM-04
wave 4 wired `DeterministicWriter(store=store)` into the app lifespan without
its required `settings` argument, breaking tests/unit/test_app_lifespan.py
while AutoBuild reported all-green. Reward requires the FULL unit suite green
— not just new-module tests — with the wave-4 wiring intact and the
regression-catching tests unweakened.

Anti-gaming guards:
- the suite is run with `-o addopts=` so pytest-config tampering (deselecting
  or ignoring the failing test via pyproject) cannot hide a failure;
- the regression-catching test file and shared conftest are frozen by sha256
  against the pin state — fixing tests instead of source scores 0;
- the wave-4 wiring must still be present in the lifespan.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

APP = Path("/app")

# sha256 of these files at the pin (92ef897) — the verifier's teeth. Computed
# from `git show 92ef897:<path>`; fixing the suite by editing either scores 0.
FROZEN_FILES = {
    "tests/unit/test_app_lifespan.py":
        "10fbee6ff65316c6633d6a35ab2297203efbed4fb8d6559c2841f55b1e353b6c",
    "tests/conftest.py":
        "845f1a0d202a868e472de919d3a18498fba0a754baaceeab240605a41db9fd9c",
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(*args: str) -> subprocess.CompletedProcess:
    # `-o addopts=` neutralises any pyproject addopts tampering; integration
    # deselection is then re-applied explicitly.
    return subprocess.run(
        [sys.executable, "-m", "pytest", *args, "-q",
         "-o", "addopts=", "-m", "not integration", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        cwd=str(APP),
    )


def test_frozen_verifier_files_untouched():
    for rel, expected in FROZEN_FILES.items():
        path = APP / rel
        assert path.exists(), f"{rel} was deleted"
        actual = sha256_of(path)
        assert actual == expected, (
            f"{rel} was modified (sha256 {actual}) — fix the source, "
            "not the tests"
        )


def test_lifespan_suite_green():
    proc = run_pytest("tests/unit/test_app_lifespan.py")
    assert proc.returncode == 0, (
        "test_app_lifespan still failing:\n" + proc.stdout[-3000:]
    )


def test_full_unit_suite_green():
    proc = run_pytest("tests/")
    assert proc.returncode == 0, (
        "full unit suite not green:\n" + proc.stdout[-3000:]
    )


def test_wave4_wiring_still_present():
    app_py = (APP / "src/fleet_memory/app.py").read_text(encoding="utf-8")
    assert "RelayService(" in app_py, (
        "RelayService construction removed from app.py — the fix must keep "
        "the TASK-RLY-006 wiring, not delete it"
    )
    assert "DeterministicWriter(" in app_py, (
        "DeterministicWriter construction removed from app.py lifespan"
    )
    handler = APP / "src/fleet_memory/relay/handler.py"
    assert handler.exists(), "relay handler module deleted"
