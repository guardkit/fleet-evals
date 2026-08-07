"""Pinned change 3: rubrics live in harness/rubrics/<subject>.md, selected
by subject; the English rubric is the verbatim 2026-05-18 lift; every other
subject is a DRAFT stub the judge refuses to score with."""
from __future__ import annotations

import pytest

from harness.common import RUBRICS_DIR, load_rubric

SUBJECTS = ["maths", "french", "spanish", "history", "biology",
            "chemistry", "physics"]


def test_english_rubric_is_the_verbatim_lift():
    text = load_rubric("english")
    # Anchor phrases from judge_pairwise.py:42-65 (study-tutor HEAD 27bb0b5b).
    assert text.startswith(
        "You are an experienced AQA GCSE English examiner and teacher-trainer.")
    assert "AQA English Literature (8702) and English" in text
    assert "Power &\n  Conflict anthology" in text
    assert '"rationale": "<= 2 sentences"}' in text
    assert "STATUS: DRAFT" not in text


@pytest.mark.parametrize("subject", SUBJECTS)
def test_stub_rubrics_are_draft_and_refused(subject):
    with pytest.raises(SystemExit, match="DRAFT"):
        load_rubric(subject)
    text = load_rubric(subject, allow_draft=True)
    assert "STATUS: DRAFT" in text
    assert "TODO" in text
    # Stubs carry the shared base dimensions and verdict shape, nothing
    # invented per-subject.
    assert '"winner": "A" | "B" | "tie"' in text


def test_unknown_subject_lists_available():
    with pytest.raises(SystemExit, match="latin"):
        load_rubric("latin")


def test_every_subject_rubric_file_exists():
    stems = sorted(p.stem for p in RUBRICS_DIR.glob("*.md"))
    assert stems == sorted(["_base", "english"] + SUBJECTS)
