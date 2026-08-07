# Golden reviewer findings — history.jsonl (2026-08-07)

Reviewer: adversarial golden review (history). File under review:
`venues/study-tutor-multisubject/golden/history.jsonl` (16 items).

## Verdict: PASS — needs_fix = false

No factual errors, no schema violations, no AQA breaches, no answer-dispensing
expected behaviours found.

## 1. Parse / schema (programmatic check)

- All 16 lines parse as JSON; no blank lines.
- Every item has exactly the keys `id, subject, category, prompt,
  expected_behaviours, red_flags` — no extras, no omissions.
- `expected_behaviours` is exactly 3 non-empty strings on every item;
  `red_flags` is 2–3 non-empty strings on every item (2×2-flag on lines 1–2,
  14×3-flag).
- All 16 ids unique; every id follows `history-<category>-NN` and matches its
  category; `subject` is `"history"` throughout.

## 2. Factual correctness (line by line)

| Line / id | Claim checked | Verdict |
|---|---|---|
| 1 socratic-01 | Hitler Chancellor 1933; Depression, Weimar weaknesses, 1932 elections; backstairs deal with Papen and Hindenburg | Correct (appointed January 1933 after the Papen–Hindenburg intrigue) |
| 2 socratic-02 | WW2 causes menu: Versailles, appeasement, Hitler's foreign policy, failure of the League | Correct, standard AQA Conflict & Tension framing |
| 3 source-analysis-01 | 1936 Nazi propaganda poster; useful as evidence of regime intent even if biased; provenance = who/when/purpose | Correct source-skills content ("biased ≠ useless" is the exact skill AQA rewards) |
| 4 source-analysis-02 | Soldier's letter from the Somme, July 1916; censorship and reassuring family as limitations | Correct (battle opened 1 July 1916; WW1 field-post censorship is well documented) |
| 5 interpretation-01 | Historians differ via focus, context, selection; German hardship vs French security/war damage on Versailles | Correct |
| 6 interpretation-02 | Weimar: 1923 hyperinflation and putsch attempts vs Stresemann era, Dawes Plan, Locarno | Correct (hyperinflation 1923; Munich Putsch Nov 1923, Kapp Putsch 1920; Dawes 1924; Locarno 1925) |
| 7 misconception-01 | Crash October 1929; Hitler Chancellor January 1933; in-between sequence (unemployment, Nazi vote, 1932 elections, the deal); Crash as longer-term enabler | Correct — and the item exists precisely to catch the 1929→power conflation |
| 8 misconception-02 | Arrow-in-the-eye story from the Bayeux Tapestry, debated by historians; Harold's march from Stamford Bridge; feigned retreat | Correct (Stamford Bridge 25 Sept 1066, Hastings 14 Oct; the Tapestry identification is genuinely disputed; feigned retreat per William of Poitiers) |
| 9 exam-technique-01 | 16-mark "how far do you agree" = sustained argument, support and challenge, justified judgement | Correct — AQA 16-marker (+4 SPaG) is a balanced-argument essay, verified against current revision sources |
| 10 exam-technique-02 | "Write an account" = structured narrative showing how events connect and lead to an outcome; "explain" = reasons and consequences | Correct — matches AQA's 8-mark "write an account" (narrative analysing cause/consequence/change) vs explain-type demands |
| 11 scaffolding-01 | Health and the People spans ~1000 years; organise by factors (war, religion, government, science and technology, individuals); Jenner and vaccination as a placement check | Correct — AQA thematic "Britain: Health and the People: c1000 to the present day"; the factor list is a faithful subset of AQA's; Jenner/vaccination is on-spec |
| 12 scaffolding-02 | Grade 7 vs 5 gap framed as explanation-vs-description and source/interpretation depth | Sound, no factual claims at risk |
| 13 boundary-01 | No history claims | n/a |
| 14 boundary-02 | Elizabeth I danger from Mary, Queen of Scots: religion, Mary's claim to the throne, the plots, foreign support | Correct factor set (Ridolfi/Throckmorton/Babington plots, Catholic claim, Spanish/French backing) |
| 15–16 tone | No history claims | n/a |

## 3. AQA compliance (law 4: zero assessment-material content)

- No past-paper questions, mark-scheme excerpts, examiner-report content, or
  grade-boundary claims anywhere in prompts, behaviours, or red flags.
- Item 14's essay topic was checked against AQA Elizabethan England past
  papers via web search: it is NOT a verbatim past-paper question (the real
  AQA 16-mark Mary-QoS questions found are historic-environment questions,
  e.g. Sheffield Manor Lodge). Paraphrased topic, no reproduction — clean.
- Items 9/10 stay at the level of public question-format structure (16-mark
  essay demands, account vs explain), which is technique advice, not
  assessment material — same precedent as the physics review.

## 4. Socratic + checkable expected behaviours

- No expected behaviour rewards dispensing a finished answer. Where target
  content appears inside a behaviour (the 1929/1933 dates, the Bayeux
  Tapestry attribution, the factor lists in parentheses), it is judge
  reference material, and the behaviour itself requires student involvement
  ("asks the student to sequence…", "draws out other factors through
  questioning", "guides towards… without dictating it all outright") — the
  English-seed pattern.
- Every behaviour is an observable action a judge can check against a
  transcript (declines / asks / prompts / guides towards / checks
  understanding / offers one next step). Every red flag is likewise
  observable (dictates a ready-to-memorise list, writes the full essay,
  confirms the wrong chronology, no questions at all).
- Misconception items correctly require gentle question-first correction;
  factual corrections (item 7) are legitimate tutoring, not
  answer-dispensing for assessment.
- Boundary items are true boundary tests: out-of-subject homework (13) and
  submit-as-mine ghost-writing (14), with red flags punishing both compliance
  and preachiness.

## 5. Category balance

8 categories × 2 items = 16: socratic, source_analysis,
interpretation_analysis, misconception, exam_technique, scaffolding,
boundary, tone — perfectly balanced.

Note (intentional divergence, not a defect): the English seed's
essay_feedback and quote_analysis are replaced by source_analysis and
interpretation_analysis. That is the right subject adaptation for history —
AO3 (sources) and AO4 (interpretations) are where AQA history marks live —
and the aggregator's per-category breakdown is category-agnostic. The English
seed's `text` field (set text) is correctly absent; the venue schema for
subject goldens is id/subject/category/prompt/expected_behaviours/red_flags.

## 6. Age-appropriateness

All prompts voice a plausible 15–16-year-old GCSE student (mock marks,
"hand it in as mine", night-before-essay panic, wanting to drop the
subject). Scaffolding-01 explicitly pins the register to a 15-year-old.
Sensitive curriculum content (Nazi Germany, the Somme) is handled at
standard GCSE curriculum level with no gratuitous detail. Tone items model
fixed-mindset and overwhelm scenarios appropriately, with red flags against
both dismissal and toxic positivity.

## 7. Minor observations (no fix required)

1. Item 14 frames a free-standing 16-mark essay on Mary, Queen of Scots; in
   the current AQA Elizabethan option the 16-marker is the
   historic-environment question, so the format is closer to generic/Edexcel.
   The framing lives in the student's voice (students say "16-marker"
   loosely) and no expected behaviour asserts the format, so it is in-spec.
2. The set deliberately spans several AQA options (Germany period study,
   Conflict & Tension, Health and the People, Norman England, Elizabethan
   England); no single student sits all of them. For a golden set probing a
   GCSE History tutor's breadth this is the right call, noted only so a
   future per-option venue split isn't surprised.
3. Lines 1–2 carry 2 red flags, the rest 3 — within the 2–3 contract.

Sources used for the two web-verified AQA claims:
- [Save My Exams — AQA Elizabethan England Q3 "Write an Account" (8 marks)](https://www.savemyexams.com/gcse/history/aqa/16/aqa-british-depth-study/revision-notes/elizabethan-england-c1568-1603/exam-skills-elizabethan-england-c1568-1603/bc-elizabethan-england-q3-write-an-account-question/)
- [past-papers.co.uk — Mary Queen of Scots, AQA GCSE History Elizabethan England](https://www.past-papers.co.uk/gcse/history/aqa/aqa-gcse-hist-elizabethan-england/mary-queen-of-scots)
- [AQA 8145/2B/C June 2023 question paper (filestore.aqa.org.uk)](https://filestore.aqa.org.uk/sample-papers-and-mark-schemes/2023/june/AQA-81452BC-QP-JUN23.PDF)
