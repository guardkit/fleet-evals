# Golden sets — study-tutor-multisubject venue

**STATUS: DRAFT** — these golden sets are **pre-registration INPUTS**. They are not
usable for a scored run until Rich's gate tap promotes the venue's `PROTOCOL.md`
(decision rule, seeds, judges, n) out of DRAFT. Nothing here has been shown to any
candidate model; keep it that way until the protocol is pre-registered.

Authored 2026-08-07, with per-subject adversarial review (one `<subject>.review.md`
alongside each `<subject>.jsonl`; all eight verdicts PASS — needs_fix = false).

## Per-subject counts

| Subject | Items | Categories (8 × per subject) |
|---|---|---|
| english | 24 | socratic, essay_feedback, quote_analysis, misconception, exam_technique, scaffolding, boundary, tone (3 each) |
| maths | 16 | socratic, problem_solving, method_feedback, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| french | 16 | socratic, translation_support, grammar_discovery, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| spanish | 16 | socratic, translation_support, grammar_discovery, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| history | 16 | socratic, source_analysis, interpretation_analysis, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| biology | 16 | socratic, practical_method, data_analysis, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| chemistry | 16 | socratic, practical_method, data_analysis, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| physics | 16 | socratic, practical_method, data_analysis, misconception, exam_technique, scaffolding, boundary, tone (2 each) |
| **Total** | **136** | |

English is 24 (the 16 items lifted from study-tutor's
`scripts/eval/golden_set.jsonl` — identical modulo an added `subject` field —
plus 8 extensions, one per category) to meet the
runbook's own 24–32 bar — the 2026-05-18 run's n=16 was a deadline floor, fixed here.
The other seven subjects are freshly authored at 16 each (8 categories × 2).

## Schema

One JSON object per line:

- `id` — unique across the whole corpus (136 unique ids)
- `subject` — matches the filename
- `category` — one of the subject's 8 categories above
- `prompt` — the student's message
- `expected_behaviours` — 3 per item, judge-checkable behaviours
- `red_flags` — 2–3 per item, judge-checkable failure modes
- `text` — **english only**: the set text (Macbeth, An Inspector Calls,
  Power and Conflict poetry, or the AQA spec code); other subjects omit it

The harness hard-requires only `id` + `prompt` (`harness/generate/run_ab_eval.py`);
`subject` selects the rubric and drives per-subject aggregation; `category`,
`expected_behaviours` and `red_flags` flow into blind judging via
`harness/judge/prepare.py`.

## Review discipline

Each `<subject>.review.md` records a scripted schema check, hand verification of
every embedded factual claim, an AQA-compliance pass (no past-paper / mark-scheme /
examiner-report content — law 4), a Socratic/checkability pass, and
age-appropriateness. A golden file must not be edited without re-running its review.
