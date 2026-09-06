"""Gate tests: does a fresh-database sentence yield worked examples the routing law stamps by rule?

The defect this exam exists for (2026-09-06, planning run d08a58fc): the spec seat wrote two
of eight worked examples about the database — "a new user can be created on a freshly
created database", "simultaneous user creations on a fresh database succeed" — and the
routing law could not prove them, so a person had to send a note. The gate here asks the
law's own rules the same question of every scenario, and fails naming any it refuses.

Around the gate sit four structural checks. They are po-held-007's OWN functions, imported
from its test module and collected here under the same names — not copied — so the
four-file contract, Gherkin structure, single-line steps and digest consistency are graded
one way across the two exams. The rest of 007's axes are deliberately not repeated: its
domain-language axis bans HTTP status codes in steps, and a worked example the factory can
prove names the method and path, the status code, and the body.
"""
import json
from pathlib import Path

from harness import wire_idiom_gates

REPO_ROOT = Path(__file__).resolve().parents[3]

_reused = wire_idiom_gates.po_held_007_gates(REPO_ROOT)
test_four_file_contract = _reused["test_four_file_contract"]
test_gherkin_structure = _reused["test_gherkin_structure"]
test_single_line_steps = _reused["test_single_line_steps"]
test_digest_conforms = _reused["test_digest_conforms"]


def test_every_worked_example_can_be_proven_by_rule(feature_text, rules_context):
    """THE POINT OF THIS TASK. Every scenario gets a home from guardkit's own rules — rules
    only, no model, api_test declared as an HTTP surface. A refusal names the title word
    for word and the rule that would have been needed."""
    findings = wire_idiom_gates.wire_idiom_findings(feature_text, rules_context)
    assert findings == [], (
        "worked example(s) the routing law cannot prove as written:\n"
        + "\n".join(json.dumps(f) for f in findings)
    )


def test_wire_rule_count_is_recorded(feature_text, rules_context, paths):
    """The softer measure: how many worked examples the wire rule stamped. Recorded for the
    census line at the end of the grade, so the results document can say how many were in
    the endpoint idiom; a spec answering a wire sentence with none at all is not an answer."""
    census = wire_idiom_gates.wire_rule_census(feature_text, rules_context)
    wire_idiom_gates.record_census(paths["slug"].name, census)
    assert census["by_wire_rule"] >= 1, (
        "no worked example was stamped by the wire rule: " + json.dumps(census)
    )
