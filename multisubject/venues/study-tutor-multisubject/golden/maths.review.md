# Golden reviewer findings — maths.jsonl (2026-08-07)

Verdict: **PASS — needs_fix = false**. All 16 items parse, conform to schema, are
factually correct, AQA-compliant, Socratic, judge-checkable, and age-appropriate.

## Schema (scripted check)

- 16/16 lines valid JSON; keys exactly {id, subject, category, prompt,
  expected_behaviours, red_flags}; subject "maths" throughout; ids unique.
- expected_behaviours: 3 per item (16/16). red_flags: 2–3 per item (16/16).
- Category balance: 8 categories × 2 (socratic, problem_solving, method_feedback,
  misconception, exam_technique, scaffolding, boundary, tone).

## Factual verification (every embedded claim, checked by hand)

| Item | Claim | Check |
|---|---|---|
| socratic-01 | 3x + 7 = 22 → x = 5 | 3(5)+7 = 22 ✓ |
| socratic-02 | 5, 8, 11, 14 → 3n + 2 | d = 3; 3(1)+2 = 5 ✓ |
| problem-solving-01 | 12 cookies : 300g → 30 cookies : 750g | 25g/cookie × 30 = 750 ✓ |
| problem-solving-02 | P = 26, l = 8 → 2(8 + w) = 26 → w = 5 | ✓ |
| method-feedback-01 | x² − 5x + 6 = (x − 2)(x − 3); roots x = 2, 3; student's x = −2, −3 is the classic sign error | ✓ (factorisation correct, error diagnosis correct) |
| method-feedback-02 | 2/3 + 1/4 = 11/12; sanity check that 3/7 < 2/3 | 8/12 + 3/12 = 11/12 ✓; 3/7 ≈ 0.43 < 0.67 ✓ |
| misconception-01 | (x + 3)² = x² + 6x + 9; x = 1 distinguishes | 16 vs 10 ✓ (x = 1 is a well-chosen test — x = 0 would NOT distinguish; the item picks the right value) |
| misconception-02 | 0.6 > 0.57 via tenths comparison; 0.6 = 0.60 | ✓ |
| exam-technique-01 | AQA GCSE Maths (8300): three papers, Paper 1 non-calculator, Papers 2 & 3 calculator, equally weighted | ✓ (each 1h30, 80 marks, 33⅓%) |
| exam-technique-02 | Clear working earns method marks even on unfinished questions | ✓ standard GCSE mark-scheme practice |
| scaffolding-01/02, boundary-01/02, tone-01/02 | No factual maths claims embedded | n/a — behavioural only ✓ |

Minor, non-blocking: exam-technique-01's "roughly a mark a minute" pacing example is a
slight simplification (80 marks / 90 min ≈ 1.1 min/mark) but is phrased as "such as" —
an illustrative suggestion, not a required fact — and is standard, safe GCSE advice.

## AQA compliance

Zero assessment-material content: no past-paper questions, mark-scheme text, or
examiner-report content quoted or reconstructed anywhere. exam-technique-01 describes
only the public specification structure (allowed). Its red flag "quotes or reconstructs
past-paper questions or mark schemes" actively enforces law 4. ✓

## Socratic + checkability

- No expected behaviour dispenses an answer. Every EB either requires a question of the
  student, requires the student to perform the step, or (exam_technique/scaffolding)
  requires legitimate factual/strategic guidance that is the point of the prompt.
- All EBs and red flags are concretely checkable by a judge against a transcript
  (specific answers named — x = 5, 3n + 2, 750g, 5 cm, 11/12 — so "did the model hand
  it over" is a binary read; behavioural EBs name observable moves, not vibes).
- Red flags include "gets the maths wrong" traps on the items where a model could
  plausibly err (problem-solving, method-feedback, misconception) — good coverage.

## Age-appropriateness

All content is KS4/GCSE-level (linear equations, sequences, proportion, perimeter,
quadratics, fractions, place value, averages); tone items model realistic 14–16-year-old
anxieties handled supportively. ✓

## Observations (not defects, no action required)

1. Categories intentionally diverge from the English golden set (problem_solving and
   method_feedback replace essay_feedback and quote_analysis) — a sensible subject
   adaptation, but cross-subject per-category aggregation will only align on the 6
   shared categories.
2. No `text` field (English set carries the set text) — correct for maths; the harness
   schema treats it as optional per subject.
