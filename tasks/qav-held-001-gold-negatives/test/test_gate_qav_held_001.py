"""Gate battery for qav-held-001-gold-negatives (G-Q1/G-Q2)."""
from harness import qav_gates


def test_verdict_contract(bundles, expected, output_dir):
    """G-Q1: one parseable verdict file per bundle; verdict enum; approve ⇒
    findings: []; reject ⇒ ≥1 finding with an admissible DC class and a
    non-empty locus. The expected registry and the bundle set must agree."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(qav_gates.verdict_schema_findings(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_gold_negatives_all_caught(bundles, expected, anchors, output_dir):
    """G-Q2 (must-catch, 100% — the QAV-FT deploy gate bar, WS4-S8): every one
    of the four real gold negatives is rejected, ≥1 finding carries the owning
    documented DC class, and the findings name the in-bundle signal (anchor
    group = bundle id). 3 of 4 is a FAIL."""
    groups = {g["id"]: g for g in qav_gates.compile_anchors(anchors)}
    misses = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (gold negative approved)")
            continue
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        if row["dc_class"] not in classes:
            misses.append(f"{bundle_id}: owning class {row['dc_class']} absent from {sorted(map(str, classes))}")
        locus = qav_gates.normalize(qav_gates.verdict_locus_text(verdict))
        if not qav_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    assert misses == [], misses
