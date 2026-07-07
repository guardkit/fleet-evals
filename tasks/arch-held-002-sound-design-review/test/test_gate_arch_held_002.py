"""Gate battery for arch-held-002-sound-design-review (G-A1/G-A3)."""
from harness import arch_gates


def test_review_schema(review):
    """G-A1: parseable review.json; verdict/pattern enums; approve ⇒ zero
    findings; every finding carries target + evidence."""
    findings = arch_gates.review_schema_findings(review)
    assert findings == [], findings


def test_verdict_is_approve(review):
    """G-A3 (false-block ceiling): the repaired design carries no seeded
    flaw — a fabricated blocker here is the inverse failure of
    arch-held-001's 'accepting without stress-testing'."""
    assert review.get("verdict") == "approve", (
        f"verdict={review.get('verdict')!r} with findings="
        f"{[f.get('target') for f in review.get('findings') or [] if isinstance(f, dict)]}: "
        "the sound design was blocked"
    )
