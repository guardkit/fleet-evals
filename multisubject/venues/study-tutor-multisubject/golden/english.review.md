# Adversarial review — golden/english.jsonl

Reviewer: golden-reviewer (english) · Date: 2026-08-07 · Verdict: **PASS (needs_fix = false)** — minor notes only, none in the fail classes (factual error / schema violation / AQA breach / answer-dispensing behaviour).

## 1. Parse + schema

- 24 lines, all valid JSON, file ends with newline, no duplicate ids.
- Every line has `id`, `subject: "english"`, `category`, `prompt`, `expected_behaviours` (exactly 3), `red_flags` (2–3). Extra `text` field present on all lines — carried from the source schema (RUNBOOK:212-221), consistent, harmless.
- Provenance verified programmatically: the 16 original items are **byte-identical** to `study-tutor/scripts/eval/golden_set.jsonl` with only `subject` added; the 8 `english-*-03` items are new extensions. No silent edits to the lifted set.

## 2. Category balance

8 categories × 3 items each (socratic, essay_feedback, quote_analysis, misconception, exam_technique, scaffolding, boundary, tone). Balanced; total 24 meets the runbook's own 24–32 n bar (fix #1 from the 2026-05-18 protocol).

## 3. Factual correctness — every embedded claim checked

| Claim | Verdict |
|---|---|
| Macbeth themes ambition / guilt / supernatural (socratic-01) | Correct |
| Inspector symbolises social conscience / Priestley's voice (socratic-02) | Correct |
| Lady Macbeth urges Duncan's murder (essay-feedback-01) | Correct |
| "look like the innocent flower, but be the serpent under't" = Lady Macbeth, appearance vs reality (quote-analysis-01) | Correct. (Many editions print "th' innocent flower"; "the innocent" is the standard modernised GCSE rendering — acceptable.) |
| "sneer of cold command" in Ozymandias, AQA Power and Conflict anthology (quote-analysis-02) | Correct |
| An Inspector Calls set 1912, written 1945; gap ⇒ dramatic irony (misconception-01) | Correct (written 1944–45, premiered 1945; "written in 1945" is the GCSE-standard formulation) |
| The witches' prophecy never instructs the murder (misconception-02) | Correct |
| AQA English Language spec 8700; Paper 1 Q5 = creative writing; AO5 (content/organisation) + AO6 (technical accuracy) (exam-technique-01) | Correct |
| AQA English Literature spec 8702; AO2 = writer's methods and effects, distinct from AO1/AO3 (exam-technique-02) | Correct |
| "Is this a dagger which I see before me" — Macbeth, hallucination / disturbed mind (english-quote-analysis-03) | Correct (Act 2 Sc 1) |
| 'Remains' (Armitage) = modern conflict, poet did not serve; 'Exposure' (Owen) = WWI, poet served; "looters" detail in Remains (english-misconception-03) | Correct on all four points ("tackle looters raiding a bank"; Remains is based on a soldier's Iraq testimony) |
| 'Exposure' themes: nature as enemy, futility, soldiers' suffering (english-socratic-03) | Correct |
| "colossal wreck" in Ozymandias; power-is-temporary reading (english-essay-feedback-03) | Correct quotation and reading |
| AQA Shakespeare question = printed extract + play as a whole (english-exam-technique-03) | Correct |
| Literature exam closed book (english-scaffolding-03) | Correct for AQA 8702 |
| Tutor cannot know upcoming paper content; question-spotting risky (english-boundary-03) | Correct |

No factual errors found.

## 4. AQA compliance (law 4: zero assessment material)

No past-paper questions, no mark-scheme text, no examiner-report content reproduced anywhere. AO descriptors and paper structure used are public *specification* content, not assessment material. Clean.

- **Note (not a breach):** exam-technique-01 expected behaviour reads "breaks the mark scheme into content/organisation and technical accuracy (AO5/AO6)". The content is the public AO split, but the phrase "mark scheme" could collide with the deployed `AQA_REFUSAL_PATTERN` guardrail — i.e. the golden expects a behaviour the tutor's own filter might make it cautious about. Worth watching in scored runs; rewording to "breaks the assessment objectives into…" would remove the ambiguity.

## 5. Socratic + checkable expected behaviours

- All socratic/quote/misconception behaviours are framed as *elicitation* ("asks…", "guides…", "draws out…", "leaves the final choice to the student") — none dispense the answer.
- Direct-answer behaviours appear only where a direct answer is the correct tutoring move (exam structure in english-exam-technique-03, AO2 definition in exam-technique-02, misconception corrections) — legitimate, not answer-dispensing.
- Behaviours are observable in a transcript (declines / asks / quotes accurately / offers concrete step) — checkable by a blind judge against `visible` text. A few are softer ("keeps the student motivated", "stays friendly") but each sits alongside two hard-checkable behaviours in the same item.

## 6. Age-appropriateness

All prompts voice a GCSE student (15–16). Tone items express discouragement, not crisis-level distress; expected behaviours require empathy-first handling. Scaffolding-01 explicitly pitches for a 15-year-old. Nothing inappropriate.

## 7. Minor notes (no fix required)

1. **ID convention drift:** lifted items use bare ids (`socratic-01`), new items use a subject prefix (`english-socratic-03`). Harmless (subject field disambiguates), but future subject files should pick one convention.
2. **essay-feedback-02 checkability wrinkle (inherited verbatim from source):** expected behaviour "references AO1/AO2 expectations for grade 7" presumes a grade-7 target the prompt never states ("Mark this paragraph for me"). A good tutor response that references AOs without naming grade 7 would technically miss this behaviour. Pre-existing in the 2026-05-18 set; since criteria scoring uses 0/0.5/1 a judge can score partial — acceptable, but a candidate for tightening if the file is ever re-versioned.
3. `text: "n/a"` on the four boundary/tone items is inherited source convention; fine, but a null or omitted field would be cleaner in a v2 schema.

## Verdict

needs_fix = **false**. 24/24 items parse, conform to schema, balance 8×3, contain no factual errors, no AQA assessment material, and no answer-dispensing expected behaviours.
