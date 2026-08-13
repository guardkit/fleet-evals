"""Pinned change 3: rubrics live in harness/rubrics/<subject>.md, selected
by subject; the English rubric is the verbatim 2026-05-18 lift. All seven
other subjects were finalised to PRODUCTION rubrics 2026-08-13 (Rich's word:
"Finalise all 7 now") — each carries its real AQA specification code and
assessment-objective structure, the shared six dimensions, and the verdict
shape. The DRAFT-refusal mechanism in ``load_rubric`` stays for any future
stub subject."""
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


AQA_SPEC_CODES = {
    "maths": "8300", "french": "8652", "spanish": "8692", "history": "8145",
    "biology": "8461", "chemistry": "8462", "physics": "8463",
}


@pytest.mark.parametrize("subject", SUBJECTS)
def test_subject_rubrics_are_production(subject):
    """Finalised 2026-08-13: load_rubric admits every subject without the
    draft escape hatch; each rubric names its real AQA spec code, keeps the
    shared six dimensions, and demands the exact verdict shape."""
    text = load_rubric(subject)  # no allow_draft — must NOT raise
    assert "STATUS: DRAFT" not in text and "TODO" not in text
    assert f"({AQA_SPEC_CODES[subject]})" in text
    assert "AQA" in text
    for dim in ("socratic_stance", "aqa_alignment", "scaffolding",
                "subject_accuracy", "tone", "reasoning_visibility"):
        assert dim in text
    assert '"winner": "A" | "B" | "tie"' in text
    assert '"rationale": "<= 2 sentences"}' in text


def test_unknown_subject_lists_available():
    with pytest.raises(SystemExit, match="latin"):
        load_rubric("latin")


def test_every_subject_rubric_file_exists():
    stems = sorted(p.stem for p in RUBRICS_DIR.glob("*.md"))
    assert stems == sorted(["_base", "english"] + SUBJECTS)
