"""Pinned row schema, program assembly, and prompt contract for gc-heldout.

Single source of truth shared by the provisioner (subset selection), the gate
battery (grading by execution), and the runner (prompt building) — so the
exclusion rule, the grading rule, and the serving prompt can never diverge
(FEAT-EVAL-GC integration contract PINNED_ROW_SCHEMA_AND_MANIFEST).

stdlib-only. Everything here is instrument content: changing any pinned string
after the scope-doc freeze is an instrument revision and reopens the doc before
the next freeze, never silently.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

BENCHMARK_HUMANEVAL = "HumanEval"
BENCHMARK_MBPP = "MBPP"

# --- Canonical bytes + hashing (the SHA-256 pin surface) -----------------------------

def canonical_json_bytes(obj) -> bytes:
    """The committed byte form every pin hashes over."""
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


# --- Row access -----------------------------------------------------------------------

def load_manifest(task_dir: Path) -> dict:
    return json.loads((task_dir / "input" / "manifest.json").read_text(encoding="utf-8"))


def row_path(task_dir: Path, row_id: str) -> Path:
    return task_dir / "input" / "rows" / row_id / "row.json"


def load_row(task_dir: Path, row_id: str) -> dict:
    return json.loads(row_path(task_dir, row_id).read_text(encoding="utf-8"))


def manifest_row_ids(task_dir: Path) -> list[str]:
    return [entry["row_id"] for entry in load_manifest(task_dir)["rows"]]


# --- Program assembly (grading side) --------------------------------------------------
# The candidate program NEVER contains the reference assertions; the grader
# appends them at execution time — the verdict comes from executed assertions.

def canonical_candidate_program(row: dict) -> str:
    """The Oracle: the benchmark's own solution in candidate-program form."""
    if row["benchmark"] == BENCHMARK_HUMANEVAL:
        return row["prompt"] + row["canonical_solution"]
    if row["benchmark"] == BENCHMARK_MBPP:
        return row["code"] if row["code"].endswith("\n") else row["code"] + "\n"
    raise ValueError(f"unknown benchmark {row['benchmark']!r}")


def reference_assertions(row: dict) -> str:
    if row["benchmark"] == BENCHMARK_HUMANEVAL:
        return row["test"] + f"\n\ncheck({row['entry_point']})\n"
    if row["benchmark"] == BENCHMARK_MBPP:
        setup = row.get("test_setup_code") or ""
        asserts = "\n".join(row["test_list"])
        return (setup + "\n" if setup else "") + asserts + "\n"
    raise ValueError(f"unknown benchmark {row['benchmark']!r}")


def execution_script(row: dict, candidate_program: str) -> str:
    """Candidate program + the benchmark's reference assertions — the exact
    text the sandbox executes. Exit 0 = row PASS."""
    program = candidate_program if candidate_program.endswith("\n") else candidate_program + "\n"
    return program + "\n" + reference_assertions(row)


# --- Prompt contract (serving side; ASSUM-009) ----------------------------------------

PINNED_SYSTEM_PROMPT = (
    "You are a careful Python programmer. Solve the task exactly as specified. "
    "Output ONE fenced Python code block containing a complete, self-contained "
    "solution. No prose outside the code block."
)

_HUMANEVAL_USER_TEMPLATE = (
    "Complete this Python function.\n\n"
    "```python\n{prompt}```\n\n"
    "Output the complete function definition (including the signature shown) in a "
    "single ```python code block. Do not include tests or example usage."
)

_MBPP_USER_TEMPLATE = (
    "{text}\n\n"
    "Your solution must pass these tests:\n\n"
    "```python\n{asserts}\n```\n\n"
    "Output a single ```python code block with a complete solution. "
    "Do not include the tests in your answer."
)


def user_prompt(row: dict) -> str:
    if row["benchmark"] == BENCHMARK_HUMANEVAL:
        prompt = row["prompt"] if row["prompt"].endswith("\n") else row["prompt"] + "\n"
        return _HUMANEVAL_USER_TEMPLATE.format(prompt=prompt)
    if row["benchmark"] == BENCHMARK_MBPP:
        return _MBPP_USER_TEMPLATE.format(
            text=row["text"].strip(), asserts="\n".join(row["test_list"])
        )
    raise ValueError(f"unknown benchmark {row['benchmark']!r}")


def prompt_hashes(row: dict) -> dict:
    """Recorded per rep in config.json — the hash-recorded prompt convention."""
    return {
        "system_sha256": sha256_text(PINNED_SYSTEM_PROMPT),
        "user_sha256": sha256_text(user_prompt(row)),
    }
