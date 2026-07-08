"""Gate battery for qav-held-002-honest-green (G-Q1/G-Q3/G-Q4)."""
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


def test_catch_floor_holds(bundles, expected, anchors, output_dir):
    """G-Q3 (catch floor): the narrative false-green stays caught — owning DC
    class + a finding naming the in-bundle signal. A seat tuned to stop
    false-blocking must not lose its clear catches."""
    groups = {g["id"]: g for g in qav_gates.compile_anchors(anchors)}
    misses = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (a held catch was lost)")
            continue
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        if row["dc_class"] not in classes:
            misses.append(f"{bundle_id}: owning class {row['dc_class']} absent from {sorted(map(str, classes))}")
        locus = qav_gates.normalize(qav_gates.verdict_locus_text(verdict))
        if not qav_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal")
    assert misses == [], misses


def test_honest_greens_approved(bundles, expected, output_dir):
    """G-Q4 (false-block ceiling): every honest green — including the two
    deliberately ugly ones — is approved. Rejecting an ugly-but-honest green
    is the false-block failure (the coach-v2 imbalance lesson; adf B11 ugly-
    green lever)."""
    blocked = []
    for bundle_id in bundles:
        if expected[bundle_id]["verdict"] != "approve":
            continue
        verdict = qav_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "approve":
            loci = [f.get("locus") for f in verdict.get("findings") or [] if isinstance(f, dict)]
            blocked.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} findings={loci}")
    assert blocked == [], blocked
