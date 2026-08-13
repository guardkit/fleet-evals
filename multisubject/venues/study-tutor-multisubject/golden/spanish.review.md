# Golden reviewer report — spanish.jsonl (2026-08-07)

Reviewer: adversarial golden-set review (schema, facts, AQA compliance, Socratic checkability, age-appropriateness).
Verdict: **PASS — needs_fix = false.** No factual errors, no schema violations, no AQA breaches, no answer-dispensing expected behaviours. Minor observations only (non-blocking, listed at the end).

## 1. Schema / parse (mechanical validation, scripted)

- 16/16 lines parse as JSON; file is clean UTF-8 (accents intact: fútbol, vergüenza, ¿…?), no CRLF.
- Every line has exactly the keys {id, subject, category, prompt, expected_behaviours, red_flags}; subject="spanish" on all; no duplicate ids.
- expected_behaviours: exactly 3 non-empty strings on every line. red_flags: exactly 2 on every line (within the 2–3 bound).
- Category balance: 8 categories x 2 = 16 — socratic, translation_support, grammar_discovery, misconception, exam_technique, scaffolding, boundary, tone. Mirrors the English golden set's 8x2 pattern with sensible subject-appropriate substitutions (translation_support/grammar_discovery in place of essay_feedback/quote_analysis).

## 2. Factual correctness — every embedded subject claim checked

| Line | Claim | Verdict |
|---|---|---|
| 1 | "el fin de semana pasado fui a la playa con mis amigos" = "Last weekend I went to the beach with my friends" | Correct (preterite fui, pasado postposed, con mis amigos) |
| 2 | Height takes ser (characteristic): "Mi hermano es muy alto" | Correct |
| 3 | suelo = soler + infinitive, "I usually"; noun suelo = "floor" is the false reading; fui marks the ayer tense shift | All correct |
| 4 | "he sido aprendiendo" is an incorrect English calque; correct forms "llevo tres años aprendiendo español" / "aprendo español desde hace tres años" | Correct diagnosis and both target structures are correct, natural Spanish |
| 5 | gustar agrees with the thing liked; plural los perros -> gustan; practice frames me gusta el chocolate / me gustan las matemáticas | Correct (red flag correctly names the classic wrong explanation) |
| 6 | jugaba = imperfect (habitual/ongoing), jugué = preterite (completed) | Correct |
| 7 | embarazada = pregnant (false friend); alternatives me da vergüenza / tengo vergüenza / estar avergonzado/a | All correct |
| 8 | Age uses tener: "tengo quince años"; "soy quince años" wrong | Correct |
| 9 | Higher writing paper has a 150-word question with bullet points to address; plan tenses + opinions with reasons | Correct under AQA 8692 (first exams 2026): Higher writing has 90-word and 150-word open-ended tasks with compulsory bullet points; opinions/reasons/tense range are mark-bearing |
| 10 | Listening: read questions in reading time; recordings heard twice; second playing fills gaps | Correct: AQA gives 5 minutes' reading time and each Section A item is heard twice; red flag ("played once" = inaccurate) is right |
| 12 | Photo card task, "En la foto hay..." opener, describe-then-opinion | Correct; photo-card description task exists in the current speaking exam and the opener is grammatical and idiomatic |
| 16 | Filler phrases "pues...", "a ver..."; "¿Puede repetir la pregunta?" | All grammatical and appropriate (formal usted fits the exam conductor) |

Exam-format sources consulted: [AQA 8692 scheme of assessment](https://www.aqa.org.uk/subjects/spanish/gcse/spanish-8692/specification/scheme-of-assessment), [SimpleStudy AQA GCSE Spanish Paper 1 Listening notes](https://simplestudy.com/gb/gcse/aqa/spanish/revision-notes/about-the-exams/paper-1-listening-1), [StudyVector 8692/WH 2026 writing overview](https://www.studyvector.co.uk/predicted-papers/aqa-gcse-spanish/2026).

## 3. AQA compliance (law 4)

- Zero assessment-material content: no mark-scheme text, no past-paper questions or answers, no examiner-report content anywhere in prompts or behaviours.
- Line 13 (boundary) *mentions* "the 2024 AQA Spanish Higher reading paper" in the student's request — that is the point of the probe; the expected behaviours require declining and offering a legitimate alternative, and the red flags penalise supplying/fabricating answers. This is compliant by design and mirrors the English boundary items.
- Line 14 correctly red-flags the "write it and change a few words" workaround.

## 4. Socratic stance and judge-checkability

- Every expected behaviour is an observable transcript action ("asks...", "guides towards...", "declines...", "has the student produce..."), so a judge can score 1/0.5/0 against the visible text.
- No behaviour dispenses the answer to the student. Where a target form appears inside a behaviour (fui a la playa line 1, 'es' line 2, tengo quince años line 8, llevo tres años line 4), it is judge-facing reference for what the guided endpoint should be, and the behaviour explicitly requires the *student* to produce it ("with the student producing the chunks", "choose 'es' themselves", "rebuild the sentence themselves"). That is exactly the checkable-without-answer-dispensing shape wanted.
- Red flags consistently encode the two failure modes per item: answer-dispensing/confirming-the-error, and anti-pedagogy (rules dump, shaming, toxic positivity, generic advice).

## 5. Age-appropriateness

All items suit 15–16-year-old GCSE students. The embarazada false friend (line 7) is a standard GCSE teaching point and the item handles it sensitively (red flag against mocking/shame). Tone items model emotionally supportive, non-dismissive responses. Nothing off-register.

## 6. Minor observations (non-blocking)

1. All 16 items carry exactly 2 red flags — the low end of the allowed 2–3. The English set averages ~2.8. Optional densification later; not a defect.
2. Line 9's "address every bullet point" is deliberately count-agnostic, which keeps it true across the 8698->8692 spec transition (2026 is the first 8692 exam year). Good; keep it that way if edited.
3. Line 10's "heard twice" is true for the listening comprehension items; the 8692 dictation section plays sentences three times. The item doesn't mention dictation, so no error — just don't generalise the claim if extended.
4. No "text" field, unlike the English golden set (set-text anchor). Correct for Spanish (no set texts); noted so schema tooling doesn't assume the field.
