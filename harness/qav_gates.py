"""Deterministic graders for the QAV held-out suite (FEAT-EVAL-QAV, WS2 B12).

Additive module (qav-heldout-suite-scope.md): frozen harness modules are never
edited; the anchor instrument is IMPORTED from the frozen ``idea_gates`` (the
same house pattern the coach-heldout suite uses).

Artifact under grade: per-bundle verdict files ``verdicts/{BUNDLE-ID}.json`` —
the QA-verifier judgment seat's decision over one CoachEvidenceBundle. Verdict
grammar is the QAV label trio's serving-parseable subset (adf
``domains/qa-verifier/OUTPUT-CONTRACT.md`` §3): ``verdict`` +
``findings[{class, locus}]``. ``ground_truth_source`` is row METADATA
(test/reference), never a model output — a judge cannot know which layer would
have caught the escape. Extra keys in a verdict file are tolerated.

This suite is the **single registration** of the four real Coach/QAV escapes —
the gold negatives GN-1..GN-4 that adf ``qav.gold_negatives`` reconstructs
field-by-field (SMP-002, SMP-003, 10AC, DD4F). The coach-heldout suite carries
only class-KIN analogues and mechanically bans these rows; this suite carries
the rows themselves. The two suites share one seat grammar by design, not by
accident.

Bundle shape: field names follow the documented CoachEvidenceBundle attributes
(guardkit ``coach_evidence.py`` @ ``5ad48fcf``; B-min contract kin, WS2-B11
bundle schema pinned at guardkit ``41a0ebe457``) — every non-identity field a
bundle carries must be a real CoachEvidenceBundle field (fidelity pinned by
``PINNED_COACH_BUNDLE_FIELDS`` + the integrity-test drift guard against adf when
the sibling repo is present). ``harness/qav_gates.py`` is stdlib-only.
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
    "REAL_GROUND_TRUTH_SOURCES",
    "GOLD_NEGATIVE_SOURCES",
    "QAV_ID_FIELDS",
    "REQUIRED_EVIDENCE_FIELDS",
    "PINNED_COACH_BUNDLE_FIELDS",
    "PINNED_BUNDLE_SCHEMA_SHA",
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
# (PLAN §3 dated note). The gold negatives use DC-08 (GN-1) and DC-03
# (GN-2/GN-3/GN-4); the false-block/catch task reaches DC-14/DC-05. Shared
# with the Coach seat's suite — coordinated, not duplicated.
ADMISSIBLE_DC_CLASSES = ("DC-03", "DC-05", "DC-08", "DC-12", "DC-14")

VERDICTS = ("approve", "reject")

# Ground-truth sources a real gold negative may carry (adf OUTPUT-CONTRACT §4);
# the four rows were caught by operator or merge review, never seeded.
REAL_GROUND_TRUTH_SOURCES = ("operator_caught", "merge_review_caught", "live_gate_caught")

# The four real escaped-seam rows this suite registers (single registration).
# repo/feature/task pin the gold-negative source tasks the B11 contamination
# check excludes from every training manifest.
GOLD_NEGATIVE_SOURCES = {
    "GN-1": {"repo": "study-tutor", "feature": "FEAT-SMP-002", "task": "TASK-SMP2-07", "dc_class": "DC-08"},
    "GN-2": {"repo": "study-tutor", "feature": "FEAT-SMP-003", "task": "TASK-SMP3-06", "dc_class": "DC-03"},
    "GN-3": {"repo": "guardkit", "feature": "FEAT-10AC", "task": "TASK-QAV-005", "dc_class": "DC-03"},
    "GN-4": {"repo": "forge", "feature": "FEAT-DD4F", "task": "FEAT-DD4F (wiring-fix 1ad98c0)", "dc_class": "DC-03"},
}

# Eval-harness identity fields every on-disk bundle carries (bundle_id agrees
# with its directory). These are provenance in the adf ROW metadata, not part
# of the CoachEvidenceBundle dataclass — so they are excluded from the pinned
# field fidelity check below.
QAV_ID_FIELDS = ("bundle_id", "feature_id", "task_id")

# The evidence floor common to every gold negative AND every honest green — a
# bundle without these cannot be judged. Deliberately lighter than the coach
# suite's floor: the gold negatives carry heterogeneous diagnostic fields
# (bdd_authoring_sweep, wiring, behavioural_oracle, stub_scan, runtime_parity),
# so only the always-present spine is required; the rest are optional-by-design
# and their `null` is the load-bearing absent signal.
REQUIRED_EVIDENCE_FIELDS = (
    "honesty",
    "gathering_status",
    "quality_gates",
    "tests",
    "independent_tests",
)

# CoachEvidenceBundle field set, pinned at guardkit 41a0ebe457 (adf
# contracts.py BUNDLE_FIELDS, verified field-for-field on disk 2026-07-08).
# Every non-identity field a QAV bundle carries must be in this set — an
# unknown field is drift, not additive growth. The integrity test asserts this
# tuple equals adf's BUNDLE_FIELD_SET when the sibling repo is importable.
PINNED_BUNDLE_SCHEMA_SHA = "41a0ebe457"
PINNED_COACH_BUNDLE_FIELDS = (
    "honesty",
    "gathering_status",
    "gathering_error",
    "quality_gates",
    "coverage_details",
    "plan_audit",
    "bdd",
    "bdd_authoring_sweep",
    "arch_review",
    "tests",
    "wiring",
    "mocked_seam",
    "spec_gap",
    "stub_scan",
    "coverage",
    "behavioural_oracle",
    "independent_tests",
    "independent_test_classification",
    "requirements",
    "runtime_parity",
    "evidence_repo_tests",
    "severity_recommendations",
    "advisory_issues",
    "task_type",
    "profile_name",
)
_PINNED_FIELD_SET = frozenset(PINNED_COACH_BUNDLE_FIELDS)
_ID_FIELD_SET = frozenset(QAV_ID_FIELDS)


def bundle_ids(task_dir: Path) -> list[str]:
    root = Path(task_dir) / "input" / "bundles"
    return sorted(p.name for p in root.iterdir() if (p / "bundle.json").is_file())


def load_bundle(task_dir: Path, bundle_id: str) -> dict:
    path = Path(task_dir) / "input" / "bundles" / bundle_id / "bundle.json"
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_shape_findings(bundle: dict, bundle_id: str) -> list[dict]:
    """Structural battery: identity fields present + bundle_id agrees with its
    directory; the evidence floor present; every non-identity field is a real
    CoachEvidenceBundle field (schema fidelity to guardkit 41a0ebe457)."""
    findings: list[dict] = []
    for field in QAV_ID_FIELDS:
        if field not in bundle:
            findings.append({"defect": "bundle_id_field_missing", "detail": f"{bundle_id}: {field}"})
    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in bundle:
            findings.append({"defect": "evidence_field_missing", "detail": f"{bundle_id}: {field}"})
    if bundle.get("bundle_id") != bundle_id:
        findings.append({
            "defect": "bundle_id_mismatch",
            "detail": f"dir {bundle_id!r} vs bundle_id {bundle.get('bundle_id')!r}",
        })
    unknown = (set(bundle) - _ID_FIELD_SET) - _PINNED_FIELD_SET
    if unknown:
        findings.append({
            "defect": "non_pinned_bundle_field",
            "detail": f"{bundle_id}: {sorted(unknown)} not in CoachEvidenceBundle @ {PINNED_BUNDLE_SCHEMA_SHA}",
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
    ground_truth_source, gold_negative?, ...}."""
    path = Path(task_dir) / "test" / "reference" / "expected_verdicts.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["bundle"]: row for row in payload["rows"]}
