"""Gate battery v2 for qav-held-002-honest-green (G-Q1/G-Q3/G-Q4 per the FROZEN
qav-heldout-suite-scope-v2.md, ratified by Rich 2026-07-25, freeze c1bc54f).

v2 delta: G-Q3 grades verdict + ANCHORED LOCUS; class recorded, not asserted.
G-Q1/G-Q4 unchanged from the v1 battery (which stays beside this one, untouched)."""
from harness import qav_gates


def test_verdict_contract(bundles, expected, output_dir):
    """G-Q1 (unchanged from v1)."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(qav_gates.verdict_schema_findings(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_catch_floor_holds_v2(bundles, expected, anchors, output_dir):
    """G-Q3 v2: the narrative false-green stays caught, locus firing its anchor.
    Class diagnostics recorded, not graded."""
    groups = {g["id"]: g for g in qav_gates.compile_anchors(anchors)}
    misses, diagnostics = [], []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (a held catch was lost)")
            continue
        classes = sorted({str(f.get("class")) for f in verdict.get("findings") or [] if isinstance(f, dict)})
        diagnostics.append(f"{bundle_id}: owning={row['dc_class']} said={classes}")
        locus = qav_gates.normalize(qav_gates.verdict_locus_text(verdict))
        if not qav_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    print("CLASS DIAGNOSTICS (non-gating):", "; ".join(diagnostics))
    assert misses == [], misses


def test_honest_greens_approved(bundles, expected, output_dir):
    """G-Q4 (unchanged from v1): every honest green approved."""
    blocked = []
    for bundle_id in bundles:
        if expected[bundle_id]["verdict"] != "approve":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "approve":
            loci = [f.get("locus") for f in verdict.get("findings") or [] if isinstance(f, dict)]
            blocked.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} findings={loci}")
    assert blocked == [], blocked
