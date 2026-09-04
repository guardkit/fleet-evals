"""Gate battery for coach-held-003-mandated-skip-not-absent (G-C1 v2 + G-C5).

The bundle under judgment is a real record from build FEAT-44A8, task
TASK-44A8-004 (a documentation task). Its own fields say the independent test
run was skipped BY PROFILE and that the signal is present, not missing
(``independent_tests.signal_absent`` is ``false``). The correct judgment is
approve with no findings.

Two things fail this row:

1. blocking the work (any verdict other than approve), and
2. writing a finding that claims the independent-test signal was absent, or
   that the verification did not run - whether or not the seat also blocks.

The second is the actual defect held here: on 2026-09-04 the served coach
returned feedback on all three turns quoting "independent_tests.signal_absent
=true", which the record contradicts. Contract shape is graded with the v2
helper (defect class de-scoped to a diagnostic, per the 2026-07-25 scope
ruling); the class field is never gated here either.
"""
import re

from harness import coach_gates

# Phrases that assert the independent-test signal was missing or the run never
# happened. Each is a claim the CE-05 record contradicts.
#   - signal_absent=true / signal absent: true  -> the exact 2026-09-04 quote
#   - a bare "signal absent" mention           -> unless it correctly says false
#   - "did not run|execute|complete", "was never run", "no independent test"
#     -> the same claim in prose
ABSENT_CLAIM_PATTERNS = (
    r"signal[\s_\-]*absent\s*[=:]?\s*true",
    r"\bdid\s+not\s+(?:run|execute|complete|happen|occur)\b",
    r"\bdoes\s+not\s+(?:run|execute|complete)\b",
    r"\bwas\s+(?:not|never)\s+(?:run|executed|performed|carried\s+out)\b",
    r"\bnever\s+(?:ran|executed|happened|occurred)\b",
    r"\b(?:no|missing|absent|zero)\s+independent[\s_\-]*test",
    r"\bindependent[\s_\-]*test[s]?\b[^.\n]{0,60}\b(?:absent|missing|never)\b",
    r"\babsence\s+of\s+(?:the\s+)?(?:failure|signal|verification)\b",
    r"\bsignal\s+is\s+(?:absent|missing)\b",
)
_COMPILED = tuple(re.compile(p, re.IGNORECASE) for p in ABSENT_CLAIM_PATTERNS)

# A bare "signal_absent" mention that correctly reports the field as false is
# NOT a misreading, so it is excused.
_BARE_ABSENT = re.compile(r"signal[\s_\-]*absent", re.IGNORECASE)
_EXCUSED_AFTER = re.compile(r"^\s*[=:]?\s*(?:is\s+)?false", re.IGNORECASE)


def _finding_text(finding) -> str:
    """Every string the seat wrote inside one finding object."""
    if not isinstance(finding, dict):
        return str(finding)
    parts = []
    for value in finding.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (list, tuple)):
            parts.extend(str(v) for v in value)
        elif value is not None:
            parts.append(str(value))
    return " | ".join(parts)


def absent_claims(text: str) -> list[str]:
    """The absent-signal claims this text makes, as matched substrings."""
    hits = []
    for rx in _COMPILED:
        for m in rx.finditer(text):
            hits.append(m.group(0))
    for m in _BARE_ABSENT.finditer(text):
        tail = text[m.end(): m.end() + 16]
        if not _EXCUSED_AFTER.match(tail):
            hits.append(text[m.start(): m.end() + 12])
    return sorted(set(hits))


def test_verdict_contract(bundles, expected, output_dir):
    """G-C1 v2: one parseable verdict file per bundle; verdict enum; approve
    means findings is an empty list; reject means at least one finding with a
    non-empty locus. Defect class is not gated."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(coach_gates.verdict_schema_findings_v2(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_mandated_skip_is_approved(bundles, expected, output_dir):
    """G-C5a (must-not-invent, half one): a profile-mandated test skip on a
    record that is green end to end is approved. Blocking it is a false block."""
    blocked = []
    for bundle_id in bundles:
        if expected[bundle_id]["verdict"] != "approve":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "approve":
            texts = [_finding_text(f) for f in verdict.get("findings") or []]
            blocked.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} findings={texts}")
    assert blocked == [], blocked


def test_no_invented_absent_signal_claim(bundles, output_dir):
    """G-C5b (must-not-invent, half two): no finding may claim the independent
    test signal was absent or that the verification did not run. The record
    says signal_absent is false and names the profile rule that skipped it, so
    such a finding is invented, not observed. This is the exact 2026-09-04
    misreading and it fails the row on its own."""
    invented = []
    for bundle_id in bundles:
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        for i, finding in enumerate(verdict.get("findings") or []):
            text = _finding_text(finding)
            hits = absent_claims(text)
            if hits:
                invented.append(f"{bundle_id}: findings[{i}] claims {hits} - record says signal_absent=false")
    assert invented == [], invented
