# Golden reviewer findings — french.jsonl (adversarial pass, 2026-08-07)

Reviewer: french golden reviewer (Lane 2). File under review:
`venues/study-tutor-multisubject/golden/french.jsonl` @ working tree.
Verdict: **PASS — needs_fix = false.** No factual error, no schema violation,
no AQA breach, no answer-dispensing expected behaviour. Four non-blocking nits below.

## 1. Parse + schema (machine-checked, all 16 lines)

- 16/16 lines valid JSON, UTF-8.
- Key set exactly `{id, subject, category, prompt, expected_behaviours, red_flags}`
  on every line — no extras, no omissions.
- `expected_behaviours`: exactly 3 non-empty strings on every line.
- `red_flags`: 2–3 non-empty strings on every line (44 total across the file).
- `subject` = `"french"` on all 16; all 16 ids unique, consistent
  `french-<category>-NN` naming.

## 2. Category balance

8 categories × 2 items = 16, mirroring the English golden set's 8×2 shape:
`socratic, translation_support, grammar_discovery, misconception, exam_technique,
scaffolding, boundary, tone`. The two subject-appropriate substitutions
(`translation_support`, `grammar_discovery` replacing English's `essay_feedback`,
`quote_analysis`) are sound for a language subject. Balanced.

## 3. Factual verification of every language claim

Every embedded French claim checked; all correct:

| Item | Claim | Verdict |
|---|---|---|
| socratic-01 | *je suis allé(e) à la plage hier*; passé composé of aller takes être; *j'ai allé* flagged as an error | correct |
| socratic-02 | *j'apprends le français depuis cinq ans*; depuis + present for ongoing action; perfect tense with depuis flagged wrong for ongoing actions | correct |
| translation-support-01 | *je suis allé* = passé composé, *était* = imperfect; *nul* = informal "rubbish" | correct |
| translation-support-02 | near future = aller + infinitive; **rendre visite à** for people vs **visiter** for places; *je vais rendre visite à ma grand-mère le week-end prochain* | correct |
| grammar-discovery-01 | small set of mostly movement/change verbs take être (aller, venir, arriver, partir); participle agrees with subject after être (allé/allée) | correct |
| grammar-discovery-02 | *voiture* feminine → *verte*; agreement rule "feminine usually adds -e, plural adds -s" | correct |
| misconception-01 | age uses **avoir**: *j'ai 15 ans*, not *je suis 15 ans* | correct |
| misconception-02 | *actuellement* = "currently", classic faux ami; "actually" → *en fait* | correct |
| exam-technique-02 | *Pouvez-vous répéter, s'il vous plaît ?* as a repair phrase | correct |

## 4. AQA claims (verified against the live spec, not memory)

- exam-technique-01: "Higher tier involves translation into French and extended
  writing tasks" — TRUE under both the outgoing 8658 spec and the new 8652 spec
  (first exams 2026): 8652 Higher Paper 4 has translation of sentences into
  French (min 50 words) plus structured/extended writing tasks. The claim is
  non-exclusive so it stays true even though 8652 Foundation also has a shorter
  translation. Red flag explicitly bans inventing mark allocations / mark-scheme
  wording — good guard.
- exam-technique-02: photo card is a real component of the AQA speaking exam in
  both specs, and asking the teacher to repeat is a legitimate strategy. Accurate.

Sources: [AQA 8652 specification](https://filestore.aqa.org.uk/resources/french/specifications/AQA-8652-SP-2024.pdf),
[AQA 8652 scheme of assessment](https://www.aqa.org.uk/subjects/french/gcse/french-8652/specification/scheme-of-assessment),
[8652/WH Paper 4 Writing sample assessment materials](https://filestore.aqa.org.uk/resources/french/AQA-8652WH-SCB.PDF)

## 5. AQA compliance (law 4)

Zero assessment-material content: no mark-scheme wording, no past-paper
questions, no examiner-report text, no grade boundaries. Exam references are
spec-structure level only, and the one exam-structure item carries a red flag
against fabricating mark allocations. COMPLIANT.

## 6. Socratic quality + judge checkability

- All expected behaviours are phrased as observable actions ("asks…",
  "declines…", "guides towards…", "flags…") — checkable by a blind judge.
- No behaviour instructs the tutor to dispense the answer to the student. The
  parenthetical target answers (e.g. the correct translation) are reference
  material for the judge, correctly framed as "guides towards… letting the
  student build it" / "has the student assemble…".
- Boundary and tone items match the English set's intent (role-holding,
  empathy-before-content) and are cleanly checkable.

## 7. Age-appropriateness

Register and content fit a 15–16-year-old GCSE student throughout ("je suis
rubbish lol", grade-7 ambition, vocab-forgetting, exam anxiety). Nothing
unsafe, nothing patronising. PASS.

## 8. Non-blocking nits (recorded, none gates)

1. **Accent stripping.** All French diacritics are ASCII-normalised (*alle, a la
   plage, etait, grand-mere, francais, repeter, passe compose*) while em-dashes
   are retained — so the file is UTF-8-capable but renders its French exemplars
   technically misspelled. An over-literal judge might penalise a
   correctly-accented tutor reply, or accept unaccented tutor French as fully
   correct. Recommend either restoring accents or adding a one-line rubric note
   that golden-file French is accent-normalised and tutor output SHOULD be
   accented.
2. **misconception-01 internal tension.** Behaviour 1 ("corrects gently — …so
   it's 'j'ai 15 ans'") can be satisfied by flatly announcing the fix, which
   behaviour 2 then penalises. Workable under per-behaviour scoring; a cleaner
   b1 would be "ensures the student ends up with the correct 'j'ai 15 ans'".
3. **tone-02 hedge.** "…possibly responding warmly to the French-English mix" —
   the "possibly" clause is unjudgeable; the core clause is fine. Trim on next
   edit.
4. **exam-technique-01 tier nuance.** Translation into French also exists at
   Foundation in 8652; the behaviour's Higher-tier claim is non-exclusive and
   therefore true, but judges should not fail a tutor that mentions the
   Foundation translation too.

## Verdict

`needs_fix = false`. File is fit for the golden set as-is; nits are follow-up
polish, not defects.
