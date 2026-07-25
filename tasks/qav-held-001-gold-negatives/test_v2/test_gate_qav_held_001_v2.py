"""Gate battery v2 for qav-held-001-gold-negatives (G-Q1/G-Q2 per the FROZEN
qav-heldout-suite-scope-v2.md, ratified by Rich 2026-07-25, freeze c1bc54f).

v2 delta vs the frozen v1 battery (which stays beside this one, untouched):
G-Q2 grades verdict + ANCHORED LOCUS only; the owning DC class is RECORDED as
non-gating diagnostics, never asserted (the four-tune evidence: class-naming
tracks corpus-support gradients — RESULTS-qav-ft-v1..v4)."""
from harness import qav_gates


def test_verdict_contract(bundles, expected, output_dir):
    """G-Q1 (unchanged from v1): one parseable verdict per bundle; schema holds."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(qav_gates.verdict_schema_findings(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_gold_negatives_all_caught_v2(bundles, expected, anchors, output_dir):
    """G-Q2 v2: every gold negative REJECTED with a finding whose locus fires
    the bundle's anchor group. Class diagnostics recorded, not graded."""
    groups = {g["id"]: g for g in qav_gates.compile_anchors(anchors)}
    misses, diagnostics = [], []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (gold negative approved)")
            continue
        classes = sorted({str(f.get("class")) for f in verdict.get("findings") or [] if isinstance(f, dict)})
        diagnostics.append(f"{bundle_id}: owning={row['dc_class']} said={classes}")
        locus = qav_gates.normalize(qav_gates.verdict_locus_text(verdict))
        if not qav_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    print("CLASS DIAGNOSTICS (non-gating):", "; ".join(diagnostics))
    assert misses == [], misses
