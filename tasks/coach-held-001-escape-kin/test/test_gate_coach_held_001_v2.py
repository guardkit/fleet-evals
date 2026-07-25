"""v2 gate battery for coach-held-001-escape-kin (coach-heldout-suite-scope-v2,
FROZEN 2026-07-25). Judgment + LOCUS graded; defect-class de-scoped to a
non-gating diagnostic. v1 battery (test_gate_coach_held_001.py) is untouched."""
from harness import coach_gates


def test_verdict_contract_v2(bundles, expected, output_dir):
    """G-C1 v2: one parseable verdict per bundle; enum; approve ⇒ findings: [];
    reject ⇒ ≥1 finding with a non-empty LOCUS (class NOT required admissible)."""
    assert set(bundles) == set(expected), "bundle dirs and expected registry disagree"
    all_findings = []
    for bundle_id in bundles:
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        all_findings.extend(coach_gates.verdict_schema_findings_v2(verdict, bundle_id))
    assert all_findings == [], all_findings


def test_escape_kin_all_caught_v2(bundles, expected, anchors, output_dir):
    """G-C2 v2 (must-catch 100%): every escape-kin bundle is REJECTED and its
    findings NAME THE IN-BUNDLE SIGNAL (locus anchor match). Owning DC class is
    recorded as a diagnostic only — it never fails this gate (Rich's QAV-consistent
    de-scope: capacity-shaped, not judgment)."""
    groups = {g["id"]: g for g in coach_gates.compile_anchors(anchors)}
    misses = []
    diagnostics = []
    for bundle_id in bundles:
        row = expected[bundle_id]
        if row["verdict"] != "reject":
            continue
        verdict = coach_gates.load_verdict(output_dir, bundle_id)
        if verdict.get("verdict") != "reject":
            misses.append(f"{bundle_id}: verdict={verdict.get('verdict')!r} (escape approved)")
            continue
        locus = coach_gates.normalize(coach_gates.verdict_locus_text(verdict))
        if not coach_gates._first_match(groups[bundle_id], locus):
            misses.append(f"{bundle_id}: findings never name the in-bundle signal (locus)")
        # DIAGNOSTIC ONLY — class match recorded, never gated (v2 de-scope).
        classes = {f.get("class") for f in verdict.get("findings") or [] if isinstance(f, dict)}
        want = row.get("dc_class")
        diagnostics.append(f"{bundle_id}: class {'HIT' if want in classes else 'miss'} (want={want} got={sorted(map(str, classes))})")
    print("\n[v2 class diagnostics — non-gating]\n" + "\n".join(diagnostics))
    assert misses == [], misses
