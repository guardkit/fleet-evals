"""Gate tests for the revise path: did the note Rich sent actually land?

Three questions, each its own test so a failure names which one broke:

  1. was the change the note asked for made,
  2. was anything else changed while nobody was looking,
  3. do the plain-language list and the specification file still describe the
     same set of worked examples.

Around them sit the three structural checks the revised spec still has to pass —
it is a /feature-spec output like any other, and a revise that breaks the file
contract is not a pass either. The rest of po-held-007's quality axes are NOT
repeated here: this exam asks whether feedback was resolved, and duplicating the
whole 007 battery would grade the same spec twice and blur which one failed.
"""
import json

from harness import revise_gates, spec_gates


def test_four_file_contract(output_dir):
    """The revised answer is still the pinned four files under features/{slug}/."""
    findings = spec_gates.spec_layout_findings(output_dir)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_digest_matches_the_feature(digest, feature_text, manifest, paths):
    """The list a person approves is a faithful compression of the specification —
    one entry per worked example, in file order, titles and tags word for word."""
    findings = spec_gates.digest_findings(digest, feature_text, manifest, paths["slug"].name)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_assumptions_manifest_still_resolves(parsed, manifest):
    """A dropped worked example must not leave an assumption pointing at nothing —
    the failure mode a revise introduces that a first draft cannot."""
    names = {sc["name"] for sc in parsed["scenarios"]}
    findings = spec_gates.manifest_schema_findings(manifest, names)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_the_note_was_honoured(prior_sentences, produced_sentences, note):
    """THE POINT OF THIS TASK. On 2026-09-05 the seat returned the same six worked
    examples after being told to drop one, and scored 1.0."""
    findings = revise_gates.note_findings(prior_sentences, produced_sentences, note)
    assert findings == [], "\nthe note was: " + str(note["note"]) + "\n" + "\n".join(
        f["reason"] for f in findings)


def test_nothing_else_changed(prior_sentences, produced_sentences, note):
    """Everything the note did not mention survives word for word, in order."""
    findings = revise_gates.collateral_findings(prior_sentences, produced_sentences, note)
    assert findings == [], "\nthe note was: " + str(note["note"]) + "\n" + "\n".join(
        f["reason"] for f in findings)


def test_list_and_spec_agree_on_count(produced_sentences, parsed):
    """The card and the specification behind it have to be the same list."""
    findings = revise_gates.count_findings(produced_sentences, len(parsed["scenarios"]))
    assert findings == [], "\n" + "\n".join(f["reason"] for f in findings)
