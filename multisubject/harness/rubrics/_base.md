# _base — the subject-agnostic judging dimensions

Every rubric in this directory scores the SAME six dimensions, 1 (poor) to
5 (excellent), and asks for the same fenced ```json verdict shape. What a
per-subject rubric adds is the subject persona, the exam-board framing, and
the set-text/topic accuracy grounds — never new dimensions.

The six dimensions (names are load-bearing — `judge/resolve.py` validates
them on every judgement):

- `socratic_stance` — guides with questions instead of handing over the answer
- `aqa_alignment` — uses the exam board's assessment-objective framing and
  vocabulary for THIS subject
- `scaffolding` — grade/age-appropriate, builds on the student's own attempt
- `subject_accuracy` — correct about the topic/set material; authentic
  quotations and facts only
- `tone` — encouraging, pitched right for a Year-10 student
- `reasoning_visibility` — surfaces its pedagogical thinking

Verdict shape every rubric must demand (verbatim):

```
Return ONLY a fenced ```json block of exactly this shape:
{"winner": "A" | "B" | "tie",
 "A": {"socratic_stance": int, "aqa_alignment": int, "scaffolding": int,
       "subject_accuracy": int, "tone": int, "reasoning_visibility": int},
 "B": {"socratic_stance": int, "aqa_alignment": int, "scaffolding": int,
       "subject_accuracy": int, "tone": int, "reasoning_visibility": int},
 "rationale": "<= 2 sentences"}
```

Rubric status: `english.md` is the only production rubric (lifted VERBATIM
from study-tutor `scripts/eval/judge_pairwise.py:42-65`). All other subjects
are `STATUS: DRAFT` stubs — the harness refuses to judge with them unless
`--allow-draft-rubrics` is passed (dry runs only).
