"""Deterministic graders for the arch-adversarial held-out suite (FEAT-EVAL-ARCH).

Additive module (arch-heldout-suite-scope.md): the frozen harness modules are
never edited. The anchor instrument (load/compile/normalize/match + the
anti-stuffing threshold) is IMPORTED from the frozen ``idea_gates`` — the same
carry-over spec_gates used — so the licensing semantics cannot drift from the
frozen suites.

Artifact under grade: ``review.json`` at the answer-sheet root — the architect
review seat's structured verdict over a design-review packet
(goals + candidate design + repo manifest).

Pattern vocabulary: the architect Coach's own detection taxonomy
(specialist-agent ``roles/architect/criteria/definitions.yaml`` @ ed2cfe5),
plus ``MISSING_SEAM`` for the player.md flow-trace duty ("missing
interactions" — the WS4 §5 "phantom component or missing seam" pair has no
definitions.yaml id, so this suite adds one rather than mislabel the class).
"""

from __future__ import annotations

import json
from pathlib import Path

from harness.idea_gates import (  # frozen instrument, imported not copied
    STUFFING_MAX_ASSERTED_GROUPS,
    _first_match,
    compile_anchors,
    load_anchors,
    normalize,
)

__all__ = [
    "DETECTION_PATTERNS",
    "VERDICTS",
    "load_review",
    "review_schema_findings",
    "finding_text",
    "fired_groups",
    "missed_groups",
    "compile_anchors",
    "load_anchors",
    "normalize",
]

# definitions.yaml detection_patterns ids (pinned @ ed2cfe5) + MISSING_SEAM.
DETECTION_PATTERNS = (
    "PHANTOM",
    "UNGROUNDED",
    "SCOPE_CREEP",
    "MISSING_TRADEOFF",
    "SOURCE_COLLAPSE",
    "DOMAIN_DILUTION",
    "UNSTATED_ASSUMPTION",
    "MISSING_SEAM",
)

VERDICTS = ("approve", "revise")


def load_review(output_root: Path) -> dict:
    """Load the answer sheet. A missing or unparseable review.json is a
    contract failure, reported as a finding (never a silent skip)."""
    path = Path(output_root) / "review.json"
    if not path.is_file():
        return {"__load_error__": f"review.json missing at {path}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"__load_error__": f"review.json unparseable: {exc}"}
    if not isinstance(payload, dict):
        return {"__load_error__": "review.json top level must be an object"}
    return payload


def review_schema_findings(review: dict) -> list[dict]:
    """Contract battery: verdict enum, findings shape, pattern enum, and the
    approve⇒zero-findings rule (carried verbatim from the QAV label contract,
    adf OUTPUT-CONTRACT.md §3 — one verdict grammar across the judgment
    seats). Unknown extra top-level keys are tolerated (extra='ignore'
    precedent, po-held-008 extra-yaml-keys)."""
    findings: list[dict] = []
    if "__load_error__" in review:
        return [{"defect": "unloadable", "detail": review["__load_error__"]}]
    verdict = review.get("verdict")
    if verdict not in VERDICTS:
        findings.append({"defect": "verdict_enum", "detail": f"verdict={verdict!r} not in {VERDICTS}"})
    items = review.get("findings")
    if not isinstance(items, list):
        findings.append({"defect": "findings_shape", "detail": "findings must be a list"})
        return findings
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            findings.append({"defect": "finding_shape", "detail": f"findings[{i}] not an object"})
            continue
        pattern = item.get("pattern")
        if pattern not in DETECTION_PATTERNS:
            findings.append({
                "defect": "pattern_enum",
                "detail": f"findings[{i}].pattern={pattern!r} not in the pinned taxonomy",
            })
        for key in ("target", "evidence"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                findings.append({"defect": f"finding_{key}", "detail": f"findings[{i}].{key} empty/missing"})
    if verdict == "approve" and items:
        findings.append({
            "defect": "approve_with_findings",
            "detail": "approve ⇒ findings: [] (QAV label rule, carried); blocking findings force revise",
        })
    if verdict == "revise" and not items:
        findings.append({"defect": "revise_without_findings", "detail": "revise ⇒ ≥1 finding"})
    return findings


def finding_text(item: dict) -> str:
    """The anchor-matched surface of one finding: pattern + target + evidence."""
    parts = [item.get(k) for k in ("pattern", "target", "evidence")]
    return "\n".join(p for p in parts if isinstance(p, str))


def fired_groups(review: dict, anchors: dict, stuffing_max: int | None = None) -> set[str]:
    """Anchor groups the review demonstrably catches. Per-FINDING counting
    with the frozen anti-stuffing rule (idea-extension §2.4, threshold
    imported): a single finding matching more than the threshold's group
    count is keyword salad and credits nothing."""
    max_groups = STUFFING_MAX_ASSERTED_GROUPS if stuffing_max is None else stuffing_max
    groups = compile_anchors(anchors)
    fired: set[str] = set()
    for item in review.get("findings") or []:
        if not isinstance(item, dict):
            continue
        text = normalize(finding_text(item))
        matched = {g["id"] for g in groups if _first_match(g, text)}
        if len(matched) > max_groups:
            continue  # stuffed finding: credits nothing
        fired |= matched
    return fired


def missed_groups(review: dict, anchors: dict) -> list[str]:
    all_ids = {g["id"] for g in compile_anchors(anchors)}
    return sorted(all_ids - fired_groups(review, anchors))
