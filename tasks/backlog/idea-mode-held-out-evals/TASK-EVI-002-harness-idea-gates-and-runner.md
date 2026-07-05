---
id: TASK-EVI-002
title: "harness/idea_gates.py + run_po_eval.py --suite flag and assembly branches"
status: backlog
task_type: feature
parent_review: TASK-REV-09AB
feature_id: FEAT-EVI
wave: 2
implementation_mode: task-work
complexity: 5
priority: high
dependencies: [TASK-EVI-001]
created: 2026-07-05T09:30:00Z
consumer_context:
  - task: TASK-EVI-001
    consumes: ANCHOR_SCHEMA_AND_DIAGNOSTIC_CONTRACT
    framework: "stdlib json + re (frozen-suite grader style)"
    driver: "python3 stdlib"
    format_note: "invention/constraint anchors JSON schema and structured-findings return shape exactly as pinned in the addendum doc §instrument-contracts"
---

# TASK-EVI-002 — Harness gates module + runner suite flag

## Scope

**NEW** `harness/idea_gates.py` (stdlib-only: `json`, `re`, `unicodedata`) — the four
gate families as pure functions returning structured findings:

1. `normalize(s)` — NFKC + casefold + unicode hyphen/dash→`-`, NBSP/thin-space→` `,
   curly→straight quotes. Applied identically to units, license statements, constraint text.
2. Invention-anchor matcher — loads anchors JSON; scans per structural unit
   (structural_units() convention: epic unit = name+bc+description; feature unit =
   title+description+bc+joined constraints; priority_rationale its own unit;
   feature_spec_inputs excluded via flatten-match); licensing per-GROUP via co-match in
   `assumptions[].statement` or `open_questions[]`; amended anti-stuffing (ASSUM-009):
   stuffing score counts only body-asserted groups, >2 ⇒ statement licenses nothing.
   Findings name the unlicensed detail and matched text.
3. Constraint-carried check — ALL constraint-anchor groups must match the JOINED
   `constraints_and_dependencies` text (normalized).
4. Selection-subset + dependency-closure (scope mode) — subset: every response
   feature_id ∈ reference ids AND title/bounded_context equal reference's (normalized);
   closure: for every selected id, every REFERENCE-declared direct dep is selected;
   response depends_on entries must resolve to selected ids. Findings name offending ids.

**MODIFIED (additively)** `harness/run_po_eval.py`: `--suite` arg default `"po-heldout"`;
line 330 compares against `args.suite`; line 336 error message interpolates `args.suite`;
two `assemble()` branches (po-held-005-idea: system=`player_idea.md`, user=`input/brief.md`;
po-held-006-scope: system=`player_scope.md`, user=roadmap+constraint per instruction.md);
docstring touch-up.

## Acceptance Criteria

- [ ] All gates consume the parsed payload dict, never raw response text (payload-only invariant)
- [ ] Unit tests ship in this task: matcher behaviour (licensing, anti-stuffing amended
      counting, normalization incl. U+2011/e‑prescribing-style variants, per-group
      semantics), subset/closure vs a toy reference graph (incl. emptied-depends_on
      failure), constraint all-groups semantics
- [ ] Unit test: default `--suite` selects exactly the 4 frozen ids; `--suite
      po-heldout-idea` selects exactly the 2 new ids; wrong-suite `--task` errors clearly
- [ ] Frozen-path regression proof: `--dry-run` before/after — the 4 frozen tasks'
      assembled prompt sha256s identical
- [ ] INVARIANTS: `harness/po_contract.py` and `harness/grading.py` byte-identical
      (`git diff` empty); `tests/test_verifier_integrity.py` untouched
- [ ] All modified files pass project-configured lint/format checks with zero errors

## Seam Tests

```python
"""Seam test: verify ANCHOR_SCHEMA_AND_DIAGNOSTIC_CONTRACT from TASK-EVI-001."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("ANCHOR_SCHEMA_AND_DIAGNOSTIC_CONTRACT")
def test_anchor_schema_and_diagnostic_contract():
    """Matcher loads the addendum-pinned anchors schema and returns named findings.

    Contract: findings must NAME the unlicensed detail / offending feature id —
    never a bare bool. Producer: TASK-EVI-001 (addendum §instrument-contracts).
    """
    from harness import idea_gates
    anchors = {"groups": [{"id": "platform", "alternates": ["ios", "native\\s+app"]}]}
    payload = {"epics": [{"id": "E1", "name": "iOS Client", "bounded_context": "BC",
                          "description": "Ship the iOS app first. It matters.",
                          "features": []}],
               "assumptions": [], "open_questions": [], "priority_rationale": ""}
    findings = idea_gates.find_unlicensed_inventions(payload, anchors)
    assert findings, "expected a finding for unlicensed platform assertion"
    assert any("platform" in f["group"] for f in findings)
    assert all(f.get("matched_text") for f in findings), "findings must name the detail"
```

## Notes

- read_prompt() raises FileNotFoundError if the specialist-agent prompts are absent —
  verify `player_idea.md`/`player_scope.md` exist in the checkout before wiring;
  provenance-pin them in the new task.tomls (TASK-EVI-003/004).
- assemble() ValueError sits outside run_rep's retry path (run_po_eval.py:226) — the
  assembly branches must land before/with the task.tomls (they do: wave 2 < wave 3).
