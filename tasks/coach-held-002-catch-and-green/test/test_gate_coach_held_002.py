"""Gate battery for coach-held-002-catch-and-green (G-C1/G-C3/G-C4)."""
from harness import coach_gates


def test_verdict_contract(bundles, expected, output_dir):
    """G-C1: one parseable verdict file per bundle; verdict enum; approve ⇒
    findings: []; reject ⇒ ≥1 finding with an admissible DC class and a
    non-empty locus. The expected registry and the bundle set must agree."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(coach_gates.verdict_schema_findings(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_catches_hold(bundles, expected, anchors, output_dir):
    """G-C3 (regression floor): the classes the Coach demonstrably catches
    today stay caught — owning DC class + signal-naming findings."""
    groups = {g["id"]: g for g in coach_gates.compile_anchors(anchors)}
    misses = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (a held catch was lost)")
            continue
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        if row["dc_class"] not in classes:
            misses.append(f"{bundle_id}: owning class {row['dc_class']} absent from {sorted(map(str, classes))}")
        locus = coach_gates.normalize(coach_gates.verdict_locus_text(verdict))
        if not coach_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    assert misses == [], misses


def test_honest_greens_approved(bundles, expected, output_dir):
    """G-C4 (false-block ceiling): honest greens — including the deliberately
    ugly one — are approved. A seat that rejects everything is as useless as
    one that approves everything (the coach-v2 imbalance lesson)."""
    blocked = []
    for bundle_id in bundles:
        if expected[bundle_id]["verdict"] != "approve":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "approve":
            loci = [f.get("locus") for f in verdict.get("findings") or [] if isinstance(f, dict)]
            blocked.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} findings={loci}")
    assert blocked == [], blocked
