"""v2 gate battery for coach-held-002-catch-and-green (coach-heldout-suite-scope-v2,
FROZEN 2026-07-25). Judgment + LOCUS graded; defect-class de-scoped to a
non-gating diagnostic; G-C4 (false-block ceiling) UNCHANGED. v1 untouched."""
from harness import coach_gates


def test_verdict_contract_v2(bundles, expected, output_dir):
    """G-C1 v2: reject ⇒ ≥1 finding with a non-empty LOCUS (class de-scoped)."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(coach_gates.verdict_schema_findings_v2(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_catches_hold_v2(bundles, expected, anchors, output_dir):
    """G-C3 v2 (regression floor): held catches stay REJECTED with a signal-naming
    LOCUS. Owning DC class recorded as a diagnostic only."""
    groups = {g["id"]: g for g in coach_gates.compile_anchors(anchors)}
    misses = []
    diagnostics = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (a held catch was lost)")
            continue
        locus = coach_gates.normalize(coach_gates.verdict_locus_text(verdict))
        if not coach_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal (locus)")
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        want = row.get("dc_class")
        diagnostics.append(f"{bundle_id}: class {'HIT' if want in classes else 'miss'} (want={want} got={sorted(map(str, classes))})")
    print("\n[v2 class diagnostics — non-gating]\n" + "\n".join(diagnostics))
    assert misses == [], misses


def test_honest_greens_approved_v2(bundles, expected, output_dir):
    """G-C4 v2 (false-block ceiling) — UNCHANGED from v1: honest greens, incl. the
    deliberately ugly one, are approved with empty findings."""
    blocked = []
    for bundle_id in bundles:
        if expected[bundle_id]["verdict"] != "approve":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "approve":
            loci = [f.get("locus") for f in verdict.get("findings") or [] if isinstance(f, dict)]
            blocked.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} findings={loci}")
    assert blocked == [], blocked
