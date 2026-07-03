"""Verifier integrity for the PO held-out suite (po-heldout-suite-scope.md §3.5).

Three-sided proof that the graders work:
  (a) every task's Oracle solution PASSES its own gate battery;
  (b) every broken fixture FAILS exactly the test(s) that own its defect class —
      including the REAL April fabricated-citation output, preserved un-repaired;
  (c) every good fixture PASSES — legitimate-but-tricky shapes (literal think tags
      inside the JSON payload, serving-repairable overlong Phase B quotes, trailing
      echo fences) that a naive grader would falsely reject.

Plus corpus integrity (SHA-256 manifests) and checklist sanity. This suite must be
green before the gate may grade anything, and it never shrinks (ablation scope §6c).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
FIXTURES_DIR = REPO_ROOT / "tests" / "broken_fixtures"
GOOD_FIXTURES_DIR = REPO_ROOT / "tests" / "good_fixtures"

TASK_IDS = sorted(p.name for p in TASKS_DIR.glob("po-held-*") if (p / "task.toml").exists())

FIXTURE_CASES = [
    (task_id, fixture.name)
    for task_id in TASK_IDS
    for fixture in sorted((FIXTURES_DIR / task_id).glob("*"))
    if (fixture / "meta.json").exists()
]

GOOD_FIXTURE_CASES = [
    (task_id, fixture.name)
    for task_id in TASK_IDS
    for fixture in sorted((GOOD_FIXTURES_DIR / task_id).glob("*") if (GOOD_FIXTURES_DIR / task_id).exists() else [])
    if (fixture / "response.txt").exists()
]

FAILED_LINE = re.compile(r"^FAILED .*::(\w+)", re.MULTILINE)


def run_gate(task_id: str, output_dir: Path | None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PO_EVAL_OUTPUT_DIR"}
    if output_dir is not None:
        env["PO_EVAL_OUTPUT_DIR"] = str(output_dir)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(TASKS_DIR / task_id / "test"), "-q", "-p", "no:cacheprovider"],
        capture_output=True, text=True, env=env, cwd=REPO_ROOT,
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.mark.parametrize("task_id", TASK_IDS)
def test_oracle_passes(task_id):
    """(a) A task whose Oracle fails is a broken verifier, not a hard task."""
    code, out = run_gate(task_id, None)  # default output dir = solution/
    assert code == 0, f"Oracle FAILED its own gate for {task_id}:\n{out}"


@pytest.mark.parametrize("task_id,fixture_name", FIXTURE_CASES)
def test_broken_fixture_fails_its_owner(task_id, fixture_name):
    """(b) A verifier that cannot fail a known-bad output is also broken."""
    fixture_dir = FIXTURES_DIR / task_id / fixture_name
    meta = json.loads((fixture_dir / "meta.json").read_text(encoding="utf-8"))
    code, out = run_gate(task_id, fixture_dir)
    assert code != 0, f"{task_id}/{fixture_name}: gate PASSED a known-bad output"
    failed = set(FAILED_LINE.findall(out)) | set(re.findall(r"^ERROR .*::(\w+)", out, re.MULTILINE))
    missing = [t for t in meta["expect_fail"] if t not in failed]
    assert not missing, (
        f"{task_id}/{fixture_name}: expected {meta['expect_fail']} to fail, "
        f"but only {sorted(failed)} failed:\n{out}"
    )


@pytest.mark.parametrize("task_id,fixture_name", GOOD_FIXTURE_CASES)
def test_good_fixture_passes(task_id, fixture_name):
    """(c) A verifier that rejects a legitimate serving-acceptable shape is broken too."""
    fixture_dir = GOOD_FIXTURES_DIR / task_id / fixture_name
    code, out = run_gate(task_id, fixture_dir)
    assert code == 0, f"{task_id}/{fixture_name}: gate REJECTED a legitimate output:\n{out}"


def test_fixture_battery_is_populated():
    """Every task has at least one broken fixture; the suite never shrinks."""
    for task_id in TASK_IDS:
        fixtures = list((FIXTURES_DIR / task_id).glob("*/meta.json"))
        assert fixtures, f"{task_id}: no broken fixtures — the verifier is unproven"
    # The permanent member: the real April fabrication (scope §3.5/§6b-c).
    assert (FIXTURES_DIR / "po-held-003-extract-full" / "april-fabrication" / "meta.json").exists()


@pytest.mark.parametrize("task_id", [t for t in TASK_IDS if (TASKS_DIR / t / "input" / "corpus").exists()])
def test_corpus_integrity(task_id):
    """input/corpus/ content matches its SHA-256 manifest — the held-out corpus is pinned."""
    corpus = TASKS_DIR / task_id / "input" / "corpus"
    manifest = {}
    for line in (corpus / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            manifest[name.lstrip("*")] = digest
    assert len(manifest) == 13, f"{task_id}: expected the 13 April files_read, found {len(manifest)}"
    for name, digest in manifest.items():
        actual = hashlib.sha256((corpus / name).read_bytes()).hexdigest()
        assert actual == digest, f"{task_id}: corpus drift in {name}"
    extra = {p.name for p in corpus.glob("*.md")} - set(manifest)
    assert not extra, f"{task_id}: unpinned files in corpus: {sorted(extra)}"


@pytest.mark.parametrize(
    "task_id", [t for t in TASK_IDS if (TASKS_DIR / t / "test" / "reference" / "coverage_checklist.json").exists()]
)
def test_checklist_sanity(task_id):
    """Anchor regexes compile; the five required areas are exactly the corpus-grounded BCs."""
    checklist = json.loads(
        (TASKS_DIR / task_id / "test" / "reference" / "coverage_checklist.json").read_text(encoding="utf-8")
    )
    for area in checklist["areas"]:
        for pattern in area["anchors_any"]:
            re.compile(pattern)
    required = sorted(a["id"] for a in checklist["areas"] if a["required"])
    assert required == [
        "audit-compliance", "behavioural-intelligence", "escalation", "lpa-management", "open-banking",
    ]
