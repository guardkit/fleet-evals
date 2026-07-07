"""Deterministic graders for the coach-heldout suite (FEAT-EVAL-COACH).

Additive module (coach-heldout-suite-scope.md): frozen harness modules never
edited; the anchor instrument is IMPORTED from the frozen ``idea_gates``.

Artifact under grade: per-bundle verdict files ``verdicts/{BUNDLE-ID}.json``
— the Coach judgment seat's decision over an authored CoachEvidenceBundle.
Verdict grammar is the QAV label trio's serving-parseable subset (adf
``domains/qa-verifier/OUTPUT-CONTRACT.md`` §3, coordinated deliberately so one
seat grammar serves both suites): ``verdict`` + ``findings[{class, locus}]``;
``ground_truth_source`` is row METADATA here (test/reference), never a model
output — a judge cannot know which layer would have caught it. Extra keys in
a verdict file are tolerated.

Bundle shape: field names follow the documented CoachEvidenceBundle
attributes (guardkit ``coach_evidence.py:172–381`` @ 5ad48fcf; B-min contract
kin, WS2-B11 bundle_schema @ guardkit 41a0ebe457) — shape reference, values
authored for this suite.
"""

from __future__ import annotations

import json
from pathlib import Path

from harness.idea_gates import (  # frozen instrument, imported not copied
    _first_match,
    compile_anchors,
    load_anchors,
    normalize,
)

__all__ = [
    "ADMISSIBLE_DC_CLASSES",
    "VERDICTS",
    "REQUIRED_BUNDLE_FIELDS",
    "bundle_ids",
    "load_bundle",
    "bundle_shape_findings",
    "load_verdict",
    "verdict_schema_findings",
    "verdict_locus_text",
    "expected_rows",
    "compile_anchors",
    "load_anchors",
    "normalize",
    "_first_match",
]

# Phase-1 admissible defect-class set, verbatim from adf OUTPUT-CONTRACT.md §3
# (PLAN §3 dated note): the documented DC taxonomy slice the QAV/Coach seats
# may cite. Coordinated, not duplicated — FEAT-EVAL-QAV (WS2 B12) owns its own
# rows; this suite only shares the class vocabulary.
ADMISSIBLE_DC_CLASSES = ("DC-03", "DC-05", "DC-08", "DC-12", "DC-14")

VERDICTS = ("approve", "reject")

# B-min-kin field floor every authored bundle must carry (names per the
# documented CoachEvidenceBundle attributes). "None" values are legal — the
# Coach's ABSENT-SIGNAL vs NO-SIGNAL-REPORTED reading depends on
# gathering_status, so absence must be representable, not omitted.
REQUIRED_BUNDLE_FIELDS = (
    "bundle_id",
    "feature_id",
    "task_id",
    "gathering_status",
    "honesty",
    "quality_gates",
    "coverage_details",
    "plan_audit",
    "bdd",
    "tests",
    "independent_tests",
    "requirements",
)


def bundle_ids(task_dir: Path) -> list[str]:
    root = Path(task_dir) / "input" / "bundles"
    return sorted(p.name for p in root.iterdir() if (p / "bundle.json").is_file())


def load_bundle(task_dir: Path, bundle_id: str) -> dict:
    path = Path(task_dir) / "input" / "bundles" / bundle_id / "bundle.json"
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_shape_findings(bundle: dict, bundle_id: str) -> list[dict]:
    findings = []
    for field in REQUIRED_BUNDLE_FIELDS:
        if field not in bundle:
            findings.append({"defect": "bundle_field_missing", "detail": f"{bundle_id}: {field}"})
    if bundle.get("bundle_id") != bundle_id:
        findings.append({
            "defect": "bundle_id_mismatch",
            "detail": f"dir {bundle_id!r} vs bundle_id {bundle.get('bundle_id')!r}",
        })
    return findings


def load_verdict(output_root: Path, bundle_id: str) -> dict:
    """A missing or unparseable verdict file is a contract failure surfaced as
    a finding, never a silent skip."""
    path = Path(output_root) / "verdicts" / f"{bundle_id}.json"
    if not path.is_file():
        return {"__load_error__": f"verdict file missing: {path}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"__load_error__": f"verdict file unparseable: {exc}"}
    if not isinstance(payload, dict):
        return {"__load_error__": "verdict top level must be an object"}
    return payload


def verdict_schema_findings(verdict: dict, bundle_id: str) -> list[dict]:
    """Contract battery: verdict enum; approve ⇒ findings: []; reject ⇒ ≥1
    finding with an admissible DC class and a non-empty locus (OUTPUT-CONTRACT
    §3, carried). Extra keys tolerated."""
    findings: list[dict] = []
    if "__load_error__" in verdict:
        return [{"defect": "unloadable", "detail": f"{bundle_id}: {verdict['__load_error__']}"}]
    value = verdict.get("verdict")
    if value not in VERDICTS:
        findings.append({"defect": "verdict_enum", "detail": f"{bundle_id}: verdict={value!r}"})
    items = verdict.get("findings")
    if not isinstance(items, list):
        findings.append({"defect": "findings_shape", "detail": f"{bundle_id}: findings must be a list"})
        return findings
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append({"defect": "finding_shape", "detail": f"{bundle_id}: findings[{i}] not an object"})
            continue
        dc = item.get("class")
        if dc not in ADMISSIBLE_DC_CLASSES:
            findings.append({
                "defect": "class_enum",
                "detail": f"{bundle_id}: findings[{i}].class={dc!r} not in {ADMISSIBLE_DC_CLASSES}",
            })
        locus = item.get("locus")
        if not isinstance(locus, str) or not locus.strip():
            findings.append({"defect": "finding_locus", "detail": f"{bundle_id}: findings[{i}].locus empty"})
    if value == "approve" and items:
        findings.append({
            "defect": "approve_with_findings",
            "detail": f"{bundle_id}: approve ⇒ findings: [] (OUTPUT-CONTRACT §3)",
        })
    if value == "reject" and not items:
        findings.append({"defect": "reject_without_findings", "detail": f"{bundle_id}: reject ⇒ ≥1 finding"})
    return findings


def verdict_locus_text(verdict: dict) -> str:
    """The anchor-matched surface of a verdict: every finding's class + locus."""
    parts: list[str] = []
    for item in verdict.get("findings") or []:
        if isinstance(item, dict):
            parts.extend(str(item.get(k, "")) for k in ("class", "locus"))
    return "\n".join(parts)


def expected_rows(task_dir: Path) -> dict[str, dict]:
    """The pre-registered per-bundle expectation registry
    (test/reference/expected_verdicts.json): bundle_id → {verdict, dc_class?,
    ground_truth_source, kin_of?}."""
    path = Path(task_dir) / "test" / "reference" / "expected_verdicts.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["bundle"]: row for row in payload["rows"]}
