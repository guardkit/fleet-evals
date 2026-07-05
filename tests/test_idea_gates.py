"""Unit tests for harness/idea_gates.py + the runner's suite selection
(FEAT-EVAL-IDEA, TASK-EVI-002). Contract under test:
docs/research/ideas/po-heldout-idea-extension-scope.md §2."""

from __future__ import annotations

import pytest

from harness import idea_gates
from harness.run_po_eval import discover_task_dirs

FROZEN_IDS = {
    "po-held-001-extract-phase-a",
    "po-held-002-extract-phase-b",
    "po-held-003-extract-full",
    "po-held-004-greenfield-discipline",
}
NEW_IDS = {"po-held-005-idea", "po-held-006-scope"}

ANCHORS = {
    "groups": [
        {"id": "platform", "alternates": [r"\bios\b", r"\bandroid\b", r"native\s*app"]},
        {"id": "regulatory", "alternates": [r"\bgdpr\b", r"\bhipaa\b", r"\bcqc\b"]},
        {"id": "integration", "alternates": [r"\be-?prescribing\b", r"\bpms\b"]},
    ]
}


def payload(units=None, assumptions=None, open_questions=None, rationale=""):
    features = [
        {
            "feature_id": f"FEAT-PO-{i:03d}",
            "title": t,
            "description": d,
            "bounded_context": bc,
            "constraints": list(cons),
        }
        for i, (t, d, bc, cons) in enumerate(units or [], start=1)
    ]
    return {
        "epics": [{
            "id": "EPIC-001", "name": "Core", "bounded_context": "Core BC",
            "description": "The core epic. It exists for tests.",
            "features": features,
        }],
        "assumptions": [
            {"id": f"ASM-{i:03d}", "statement": s} for i, s in enumerate(assumptions or [], 1)
        ],
        "open_questions": list(open_questions or []),
        "priority_rationale": rationale,
    }


# --- normalization (§2.2) ----------------------------------------------------

def test_normalize_folds_unicode_hyphen_case_and_quotes():
    assert idea_gates.normalize("E‑Prescribing") == "e-prescribing"
    assert idea_gates.normalize("“GDPR” ready") == '"gdpr" ready'


def test_variant_assertion_still_detected():
    p = payload(units=[("Records", "Supports e‑prescribing flows. Two sentences.", "Care BC", [])])
    findings = idea_gates.find_unlicensed_inventions(p, ANCHORS)
    assert [f["group"] for f in findings] == ["integration"]
    assert findings[0]["matched_text"]
    assert findings[0]["unit"].startswith("feature:")


# --- invention gate: licensing (§2.4) ----------------------------------------

def test_unlicensed_assertion_fails_with_named_finding():
    p = payload(units=[("App", "Ships as a native app for patients. Offline first.", "Patient BC", [])])
    findings = idea_gates.find_unlicensed_inventions(p, ANCHORS)
    assert findings and findings[0]["group"] == "platform"


def test_assumption_statement_licenses_the_group():
    p = payload(
        units=[("App", "Ships as a native app for patients. Offline first.", "Patient BC", [])],
        assumptions=["We assume a native app is required rather than web."],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS) == []


def test_open_question_licenses_the_group():
    p = payload(
        units=[("App", "Ships as a native app for patients. Offline first.", "Patient BC", [])],
        open_questions=["Is a native app actually required, or does mobile web suffice?"],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS) == []


def test_per_group_licensing_any_alternate_licenses():
    # Body asserts "iOS"; the assumption says "native app" — same group, licensed.
    p = payload(
        units=[("App", "An iOS client for patients. Push reminders included.", "Patient BC", [])],
        assumptions=["We assume a native app is the delivery vehicle."],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS) == []


def test_epic_name_is_requirement_bearing():
    p = {
        "epics": [{"id": "E1", "name": "iOS Client Platform", "bounded_context": "BC",
                   "description": "Client epic. Two sentences.", "features": []}],
        "assumptions": [], "open_questions": [], "priority_rationale": "",
    }
    findings = idea_gates.find_unlicensed_inventions(p, ANCHORS)
    assert findings and findings[0]["unit"].startswith("epic:")


def test_constraints_and_rationale_are_requirement_bearing():
    p = payload(
        units=[("Plan", "A plan feature. Nothing specific here.", "Plan BC", ["Must be GDPR compliant"])],
        rationale="We order PMS integration first because it unblocks the rest.",
    )
    groups = {f["group"] for f in idea_gates.find_unlicensed_inventions(p, ANCHORS)}
    assert groups == {"regulatory", "integration"}


# --- invention gate: anti-stuffing (§2.4, amended counting) --------------------

def test_stuffed_statement_licenses_nothing():
    p = payload(
        units=[("All", "Native app with GDPR posture and PMS e-prescribing hooks. Dense.", "BC", [])],
        assumptions=["We assume native app, GDPR, HIPAA, CQC, PMS and e-prescribing all apply."],
    )
    findings = idea_gates.find_unlicensed_inventions(p, ANCHORS)
    assert {f["group"] for f in findings} == {"platform", "regulatory", "integration"}


def test_compound_statement_at_threshold_licenses_both():
    # 2 body-asserted groups in one statement == threshold, not above: licenses both.
    p = payload(
        units=[("All", "Native app with e-prescribing hooks. Dense feature.", "BC", [])],
        assumptions=["We assume a native app and e-prescribing integration are both needed."],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS) == []


def test_stuffing_counts_only_body_asserted_groups():
    # Statement mentions 3 groups but only 1 is asserted in the body: not salad.
    p = payload(
        units=[("App", "Ships as a native app for patients. Offline first.", "Patient BC", [])],
        assumptions=["We assume native app delivery; GDPR posture and PMS integration remain open."],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS) == []


def test_stuffing_threshold_is_overridable_for_calibration():
    p = payload(
        units=[("All", "Native app with GDPR posture and PMS e-prescribing hooks. Dense.", "BC", [])],
        assumptions=["We assume native app, GDPR and PMS e-prescribing all apply."],
    )
    assert idea_gates.find_unlicensed_inventions(p, ANCHORS, stuffing_max=3) == []


# --- constraint-carried gate (§2.5) -------------------------------------------

CONSTRAINT_ANCHORS = {
    "groups": [
        {"id": "timebox", "alternates": [r"\b6\b|\bsix\b.{0,12}week"]},
        {"id": "team", "alternates": [r"\b2\b|\btwo\b|\bpair\b.{0,10}engineer"]},
        {"id": "mvp", "alternates": [r"\bmvp\b", r"minimum\s+viable", r"\bpilot\b"]},
    ]
}


def test_constraint_carried_across_split_entries():
    p = {"constraints_and_dependencies": [
        "Six-week delivery window", "Two engineers only", "MVP-first cut for the pilot"]}
    assert idea_gates.check_constraint_carried(p, CONSTRAINT_ANCHORS) == []


def test_dropped_constraint_group_is_named():
    p = {"constraints_and_dependencies": ["Six-week delivery window", "MVP-first cut"]}
    findings = idea_gates.check_constraint_carried(p, CONSTRAINT_ANCHORS)
    assert [f["group"] for f in findings] == ["team"]


# --- scope selection gates (§2.5) ----------------------------------------------

REFERENCE = {
    "epics": [{
        "id": "EPIC-R1", "name": "Ref", "bounded_context": "Ref BC",
        "description": "Reference epic. Two sentences.",
        "features": [
            {"feature_id": "FEAT-PO-001", "title": "Round Planning",
             "bounded_context": "Planning BC", "depends_on": []},
            {"feature_id": "FEAT-PO-002", "title": "Driver Manifest",
             "bounded_context": "Delivery BC", "depends_on": ["FEAT-PO-001"]},
            {"feature_id": "FEAT-PO-003", "title": "Proof of Delivery",
             "bounded_context": "Delivery BC", "depends_on": ["FEAT-PO-002"]},
        ],
    }],
}


def selection(ids, deps=None, features=None):
    ref = idea_gates.reference_features(REFERENCE)
    return {
        "selected_ids": list(ids),
        "response_depends_on": deps if deps is not None else {i: ref[i]["depends_on"] for i in ids},
        "response_features": features if features is not None else {
            i: {"title": ref[i]["title"], "bounded_context": ref[i]["bounded_context"]} for i in ids
        },
    }


def test_full_selection_passes_subset_and_closure():
    sel = selection(["FEAT-PO-001", "FEAT-PO-002", "FEAT-PO-003"])
    assert idea_gates.check_selection_subset(sel, REFERENCE) == []
    assert idea_gates.check_dependency_closure(sel, REFERENCE) == []


def test_single_dependency_free_feature_passes():
    sel = selection(["FEAT-PO-001"])
    assert idea_gates.check_selection_subset(sel, REFERENCE) == []
    assert idea_gates.check_dependency_closure(sel, REFERENCE) == []


def test_invented_feature_id_is_named():
    sel = selection(["FEAT-PO-001"])
    sel["response_features"]["FEAT-PO-999"] = {"title": "X", "bounded_context": "Y"}
    findings = idea_gates.check_selection_subset(sel, REFERENCE)
    assert findings == [{"feature_id": "FEAT-PO-999", "defect": "invented_feature"}]


def test_content_swap_under_legitimate_id_is_named():
    sel = selection(["FEAT-PO-001"])
    sel["response_features"]["FEAT-PO-001"]["title"] = "Fleet Telemetry Dashboard"
    findings = idea_gates.check_selection_subset(sel, REFERENCE)
    assert findings and findings[0]["defect"] == "content_swap:title"
    assert findings[0]["feature_id"] == "FEAT-PO-001"


def test_subset_title_match_is_normalized_not_exact():
    sel = selection(["FEAT-PO-001"])
    sel["response_features"]["FEAT-PO-001"]["title"] = "round planning"
    assert idea_gates.check_selection_subset(sel, REFERENCE) == []


def test_closure_uses_reference_graph_emptied_depends_on_still_fails():
    sel = selection(["FEAT-PO-002"], deps={"FEAT-PO-002": []})
    findings = idea_gates.check_dependency_closure(sel, REFERENCE)
    assert {(f["feature_id"], f["defect"]) for f in findings} == {
        ("FEAT-PO-002", "missing_prerequisite")
    }


def test_dangling_response_depends_on_is_named():
    sel = selection(["FEAT-PO-001"], deps={"FEAT-PO-001": ["FEAT-PO-042"]})
    findings = idea_gates.check_dependency_closure(sel, REFERENCE)
    assert findings == [{"feature_id": "FEAT-PO-001", "defect": "dangling_depends_on",
                         "prerequisite": "FEAT-PO-042"}]


def test_reference_graph_sanity_flags_cycle():
    cyclic = {"epics": [{"features": [
        {"feature_id": "A", "title": "", "bounded_context": "", "depends_on": ["B"]},
        {"feature_id": "B", "title": "", "bounded_context": "", "depends_on": ["A"]},
    ]}]}
    issues = " | ".join(idea_gates.reference_graph_sanity(cyclic))
    assert "cycle" in issues
    assert "dependency-free" in issues


def test_reference_graph_sanity_flags_duplicate_and_unresolved():
    bad = {"epics": [{"features": [
        {"feature_id": "A", "title": "", "bounded_context": "", "depends_on": []},
        {"feature_id": "A", "title": "", "bounded_context": "", "depends_on": ["Z"]},
    ]}]}
    issues = " | ".join(idea_gates.reference_graph_sanity(bad))
    assert "duplicate feature_id" in issues
    assert "does not exist" in issues


def test_reference_fixture_helpers():
    assert idea_gates.dependency_free_ids(REFERENCE) == ["FEAT-PO-001"]
    assert idea_gates.first_chained_pair(REFERENCE) == ("FEAT-PO-001", "FEAT-PO-002")
    assert not idea_gates.reference_graph_sanity(REFERENCE)


# --- anchors instrument sanity (§2.1) ------------------------------------------

def test_malformed_anchors_raise():
    with pytest.raises(ValueError):
        idea_gates.compile_anchors({"groups": []})
    with pytest.raises(ValueError):
        idea_gates.compile_anchors({"groups": [{"id": "a", "alternates": []}]})
    with pytest.raises(ValueError):
        idea_gates.compile_anchors({"groups": [
            {"id": "a", "alternates": ["x"]}, {"id": "a", "alternates": ["y"]}]})


# --- runner suite selection (freeze isolation, §2 / run_po_eval.py) -------------

def test_default_suite_selects_exactly_the_frozen_four():
    assert {d.name for d in discover_task_dirs("po-heldout")} == FROZEN_IDS


def test_idea_suite_selects_only_the_new_tasks():
    found = {d.name for d in discover_task_dirs("po-heldout-idea")}
    assert found <= NEW_IDS
    assert found.isdisjoint(FROZEN_IDS)


def test_suites_are_disjoint():
    frozen = {d.name for d in discover_task_dirs("po-heldout")}
    idea = {d.name for d in discover_task_dirs("po-heldout-idea")}
    assert frozen.isdisjoint(idea)
