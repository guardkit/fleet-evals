"""Gate battery for coach-held-001-escape-kin (G-C1/G-C2)."""
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


def test_escape_kin_all_caught(bundles, expected, anchors, output_dir):
    """G-C2 (must-catch, 100% — the QAV gold-negative bar applied to the
    Coach seat's own escape classes): every escape-kin bundle is rejected,
    ≥1 finding carries the owning DC class, and the findings name the
    in-bundle signal (anchor group = bundle id)."""
    groups = {g["id"]: g for g in coach_gates.compile_anchors(anchors)}
    misses = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (escape approved)")
            continue
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        if row["dc_class"] not in classes:
            misses.append(f"{bundle_id}: owning class {row['dc_class']} absent from {sorted(map(str, classes))}")
        locus = coach_gates.normalize(coach_gates.verdict_locus_text(verdict))
        if not coach_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    assert misses == [], misses
