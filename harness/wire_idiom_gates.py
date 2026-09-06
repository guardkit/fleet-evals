"""The wire-idiom gate: every worked example must be one the routing law can stamp by rule.

WHY THIS EXISTS (2026-09-06)
----------------------------
This weekend two of Rich's sentences stopped at the plan stage. The spec seat wrote
worked examples about the database rather than about what a caller sees — planning run
d08a58fc stamped six of eight and refused "a new user can be created on a freshly created
database" and "simultaneous user creations on a fresh database succeed" — and the routing
law, rightly, could not prove them: the factory proves what a caller can see at the
endpoint, and it proves examples written that way. Each refusal cost Rich a round. Part A
of the rewrite-on-refusal lane teaches the machine to rewrite such examples once before it
asks; this gate is the exam row that measures whether the spec seat needed the rewrite at
all. A sentence about wire behaviour should yield examples the law stamps by rule, with
no note from anyone.

WHAT IT MEASURES
----------------
The produced `.feature` is parsed with guardkit's own scenario lexer and every scenario is
classified with guardkit's own rules — rules only, no model — with the target repository
declared as having an HTTP surface, exactly the context the plan stage's pre-commit
stamping gives the rules on api_test. The gate passes only when every scenario gets a
home. The findings name each refused title word for word and the rule that would have
been needed: R9, the wire rule, which stamps a request to the endpoint and the reply it
gets — the method and path, the status code, and what is in the body.

A second, softer measure records how many scenarios the wire rule stamped, so the results
document can say how many worked examples were in the endpoint idiom, not only whether
every one of them had a home. It is printed at the end of the grade, where a tail-
truncated receipt keeps it (the same reasoning as harness/could_not_measure.py).

DEPENDENCY POSTURE
------------------
The lexer and the classifier are IMPORTED from guardkit, never copied. If the rules move,
this gate moves with them and the frozen solutions start failing — which is the signal we
want (the same posture as spec_gates._guardkit_routing_law). A failed import is an
instrument error naming the pin, never a silent skip. The four structural gates each task
reuses from po-held-007 are likewise imported from that task's own test module, so the
two exams can never grade the four-file contract two different ways.
"""

from __future__ import annotations

import importlib.util
import sys
import tomllib
from pathlib import Path
from typing import Any, Callable

WIRE_RULE = "R9"

# What a refused example has to become. Builder-facing (it lands in a pytest failure),
# but written the way Part A's note to the spec writer says it, so the two agree.
HOW_TO_WRITE_IT = (
    "write it as a request to the endpoint and the reply it gets: the method and path, "
    "the status code, and what is in the body"
)

# The four gates every wire-idiom task reuses from po-held-007's test module (rule 29 of
# the 2026-09-06 spec: reused by import, not copied).
REUSED_007_GATES = (
    "test_four_file_contract",
    "test_gherkin_structure",
    "test_single_line_steps",
    "test_digest_conforms",
)
_PO_HELD_007_MODULE_NAME = "po_held_007_gate_module"


def _guardkit_stamp_rules():
    """(`NormalizeContext`, `classify_scenario`, `extract_scenario_blocks`) from the installed guardkit."""
    try:
        from guardkit.orchestrator.stamp_normalizer import (  # noqa: PLC0415
            NormalizeContext,
            classify_scenario,
            extract_scenario_blocks,
        )
    except ImportError as exc:  # pragma: no cover - environment defect
        raise RuntimeError(
            "guardkit is not importable — the wire-idiom gate classifies every scenario "
            "with guardkit.orchestrator.stamp_normalizer's own rules so the exam and the "
            "plan stage's pre-commit stamping can never disagree. Install the pinned "
            "guardkit checkout (CONTRACT-feature-spec-plan-outputs.md §0)."
        ) from exc
    return NormalizeContext, classify_scenario, extract_scenario_blocks


def load_context(task_dir: Path | None = None):
    """The context the rules are given: the target repository has an HTTP surface.

    Read from the task's task.toml `[wire_idiom]` table when there is one (it names the
    target repository and whether it has an HTTP surface); without a table the target is
    taken to have an HTTP surface, which is what the 2026-09-06 spec fixes for this exam
    (rule 28: `NormalizeContext(repo_has_http_surface=True)`).
    """
    NormalizeContext, _, _ = _guardkit_stamp_rules()
    table: dict[str, Any] = {}
    if task_dir is not None:
        toml_path = Path(task_dir) / "task.toml"
        if toml_path.is_file():
            with open(toml_path, "rb") as f:
                table = tomllib.load(f).get("wire_idiom") or {}
    target = str(table.get("target_repository") or "the target repository")
    has_surface = bool(table.get("repo_has_http_surface", True))
    evidence = f"{target} has an HTTP surface" if has_surface else ""
    return NormalizeContext(repo_has_http_surface=has_surface, http_surface_evidence=evidence)


def classify_feature(feature_text: str, ctx=None) -> list[dict]:
    """One row per scenario, in file order, saying where the rules would send it.

    A row is `{"scenario": title, "verifier": home, "rule": "R9", "evidence": ...}` when a
    rule decided it and `{"scenario": title, "verifier": None, "rule": None, "evidence": ""}`
    when every rule refused. Rules only; a model is never asked here.
    """
    _, classify_scenario, extract_scenario_blocks = _guardkit_stamp_rules()
    if ctx is None:
        ctx = load_context(None)
    rows: list[dict] = []
    for block in extract_scenario_blocks(feature_text):
        home = classify_scenario(block.title, block.steps_text, ctx, annotations=block.annotations)
        if home is None:
            rows.append({"scenario": block.title, "verifier": None, "rule": None, "evidence": ""})
        else:
            rows.append({
                "scenario": block.title,
                "verifier": home.verifier,
                "rule": home.rule,
                "evidence": home.evidence,
            })
    return rows


def wire_idiom_findings(feature_text: str, ctx=None) -> list[dict]:
    """Structured findings; empty means every worked example has a home.

    Each finding names the refused title verbatim, the rule that would have been needed
    (the wire rule), and how to write the example so that rule can stamp it.
    """
    findings: list[dict] = []
    for row in classify_feature(feature_text, ctx):
        if row["verifier"] is None:
            findings.append({
                "defect": "worked_example_cannot_be_proven_by_rule",
                "scenario": row["scenario"],
                "rule_needed": f"{WIRE_RULE} (the wire rule)",
                "how_to_write_it": HOW_TO_WRITE_IT,
            })
    return findings


def wire_rule_census(feature_text: str, ctx=None) -> dict:
    """How the rules homed the worked examples: the count the wire rule stamped, the
    count every other rule stamped (by rule), and the refused titles."""
    rows = classify_feature(feature_text, ctx)
    by_rule: dict[str, int] = {}
    refused: list[str] = []
    for row in rows:
        if row["rule"] is None:
            refused.append(row["scenario"])
        else:
            by_rule[row["rule"]] = by_rule.get(row["rule"], 0) + 1
    return {
        "scenarios": len(rows),
        "by_wire_rule": by_rule.get(WIRE_RULE, 0),
        "by_rule": by_rule,
        "refused": refused,
    }


# --- The census line at the end of the grade ---------------------------------------
#
# Module state plus two hook functions, the shape harness/could_not_measure.py uses. A task
# conftest that needs both modules' hooks under the same hook name wraps them in one
# function (see any po-held-01[123] conftest) — pytest allows one function per hook name
# per conftest.

_census_by_feature: "dict[str, dict]" = {}


def record_census(feature: str, census: dict) -> None:
    """Remember a graded feature's census for the terminal summary."""
    _census_by_feature[feature] = dict(census)


def census_line(feature: str, census: dict) -> str:
    """The one line a results document reads the count from."""
    other = census["scenarios"] - census["by_wire_rule"] - len(census["refused"])
    line = (
        f"wire idiom — {feature}: {census['scenarios']} worked examples, "
        f"{census['by_wire_rule']} stamped by the wire rule (a request to the endpoint and "
        f"its reply), {other} by other rules, {len(census['refused'])} refused."
    )
    if census["refused"]:
        line += " Refused: " + "; ".join(f'"{t}"' for t in census["refused"])
    return line


def pytest_sessionstart(session):
    """Clear the record between sessions (module state, as in could_not_measure)."""
    _census_by_feature.clear()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print the census last, so a tail-truncated receipt keeps it; print it once."""
    if not _census_by_feature:
        return
    for feature, census in sorted(_census_by_feature.items()):
        terminalreporter.write_line(census_line(feature, census))
    _census_by_feature.clear()


# --- po-held-007's structural gates, by import -----------------------------------------


def po_held_007_gates(repo_root: Path) -> dict[str, Callable]:
    """The four structural gates every wire-idiom task reuses, as po-held-007's OWN
    function objects (its test module is loaded once from its file and cached).

    Not a copy: a task's test module binds these under their own names, pytest collects
    them there, and the fixtures they ask for (output_dir, feature_text, parsed, digest,
    manifest, paths) come from that task's conftest. If 007's gate changes, these change.
    """
    module = sys.modules.get(_PO_HELD_007_MODULE_NAME)
    if module is None:
        path = Path(repo_root) / "tasks" / "po-held-007-feature-spec" / "test" / "test_gate_po_held_007.py"
        if not path.is_file():
            raise RuntimeError(f"po-held-007's test module is not where rule 29 expects it: {path}")
        spec = importlib.util.spec_from_file_location(_PO_HELD_007_MODULE_NAME, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[_PO_HELD_007_MODULE_NAME] = module
        spec.loader.exec_module(module)
    return {name: getattr(module, name) for name in REUSED_007_GATES}
