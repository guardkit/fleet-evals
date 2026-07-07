"""Gate battery for arch-held-001-adversarial-review (G-A1/G-A2)."""
from harness import arch_gates


def test_review_schema(review):
    """G-A1: parseable review.json; verdict/pattern enums; approve ⇒ zero
    findings; every finding carries target + evidence."""
    findings = arch_gates.review_schema_findings(review)
    assert findings == [], findings


def test_verdict_is_revise(review):
    """G-A2: a design carrying seeded critical flaws must not be accepted —
    'accepting without stress-testing' is the weakness under test."""
    assert review.get("verdict") == "revise", (
        f"verdict={review.get('verdict')!r}: the seeded-flaw design was accepted"
    )


def test_all_seeded_flaws_caught(review, anchors):
    """G-A2: every seeded flaw's anchor group fires in the findings
    (detection floor — per-finding matching, stuffed findings credit
    nothing per the frozen anti-stuffing rule)."""
    missed = arch_gates.missed_groups(review, anchors)
    assert missed == [], f"seeded flaws not caught: {missed}"
