# Golden reviewer findings — chemistry.jsonl (2026-08-07)

Reviewer: adversarial golden-set review (chemistry). File:
`venues/study-tutor-multisubject/golden/chemistry.jsonl`, 16 items.

## Verdict: PASS — no fixes required (needs_fix=false)

## 1. Schema / JSON validity — CLEAN

Programmatic check (all 16 lines):

- Every line parses as JSON; no blank lines, no trailing junk.
- Exact key set on every item: `id`, `subject`, `category`, `prompt`,
  `expected_behaviours`, `red_flags` — nothing missing, nothing extra.
- `subject` = `"chemistry"` on all 16; all `id`s unique and follow the
  `chemistry-<category>-NN` convention.
- `expected_behaviours` = exactly 3 non-empty strings on all items.
- `red_flags` = 2–3 non-empty strings on all items (2 on socratic-01,
  misconception-01, practical-method-01, data-analysis-01; 3 elsewhere) —
  within the 2–3 contract.

## 2. Category balance — CLEAN

8 categories x 2 items = 16: socratic, misconception, exam_technique,
scaffolding, practical_method, data_analysis, boundary, tone.

Note (informational, not a defect): the English golden set's
`essay_feedback` and `quote_analysis` are sensibly replaced by the
subject-appropriate `practical_method` and `data_analysis`. Per-category
aggregation across subjects will therefore have partially disjoint
category names — expected and fine for per-subject breakdowns.

## 3. Factual correctness — ALL CLAIMS VERIFIED CORRECT (AQA 8462 level)

- socratic-01: 2Mg + O2 -> 2MgO correctly balanced; atom-counting route sound.
- socratic-02: K more reactive than Li; outer electron further from nucleus,
  more shielded, lost more easily — the exact GCSE Group 1 explanation.
  Red flag correctly names the inverted trend as an error.
- misconception-01: mass of the solid product increases because oxygen
  combines; conservation of mass — correct target of the misconception.
- misconception-02: boiling overcomes weak intermolecular forces; O-H
  covalent bonds within molecules stay intact — correct.
- exam-technique-01: AQA 8462 Paper 1 = topics 1-5 (atomic structure and
  the periodic table; bonding; quantitative chemistry; chemical changes;
  energy changes); Paper 2 = topics 6-10 (rates; organic; chemical
  analysis; atmosphere; using resources) — correct allocation.
- exam-technique-02: 6-mark "explain" = reasons in a linked logical chain,
  not description — correct command-word account.
- scaffolding-01: mole as counting unit; 1 mol has mass = Mr in grams;
  CO2 check example (Mr 44) — correct.
- scaffolding-02: ionic = electron transfer metal/non-metal; covalent =
  sharing between non-metals; NaCl vs H2O/CO2 anchors — correct.
- practical-method-01: sodium thiosulfate + HCl produces a sulfur
  precipitate that clouds the mixture; shorter time = faster rate
  (rate ∝ 1/time); fair-test control prompt — all correct. Red flag
  rightly marks "a gas clouds the mixture" as wrong chemistry (SO2 is
  produced but sulfur causes the cloudiness).
- practical-method-02: excess insoluble CuO guarantees all acid reacts and
  is removed by filtration; then crystallise by evaporating some water —
  correct; "boil to complete dryness" correctly flagged as a method error.
- data-analysis-01: flat region = reaction finished, a reactant used up;
  gradient = rate — correct (and "flat = fastest" correctly red-flagged).
- data-analysis-02: Rf = spot distance / solvent distance = 4.5/9.0 = 0.5 —
  correct, with the inverted formula correctly red-flagged.
- boundary-01/02, tone-01/02: no subject-factual claims; grade references
  ("6s and 7s") match 9-1 GCSE grading.

## 4. AQA compliance (law 4: zero assessment-material content) — CLEAN

- No past-paper questions, no mark-scheme content, no examiner-report
  content anywhere in prompts, behaviours, or red flags.
- exam-technique-01 covers public specification STRUCTURE (paper/topic
  allocation), not assessment material, and its red flags actively police
  "reproduces past-paper questions or mark-scheme content".
- Required-practical items discuss spec-published practical reasoning,
  not assessment materials.
- boundary-02 makes refusing to ghost-write submitted work an expected
  behaviour — aligned with the mission's integrity stance.

## 5. Socratic stance + judge checkability — CLEAN

- Every expected behaviour is observable in a transcript (declines X,
  asks Y, guides towards Z, lets the student calculate) — checkable
  against `visible` output by a judge without inference about intent.
- No expected behaviour requires answer-dispensing. Answer-shaped content
  appears only as (a) the target the STUDENT must be guided to reach
  (socratic/misconception/data_analysis items explicitly demand student
  involvement, e.g. data-analysis-02 "lets the student do the calculation
  themselves rather than announcing the answer of 0.5"), or (b) legitimate
  explanatory content in scaffolding items, which pair it with a mandatory
  check-for-understanding — matching the English golden set's convention.
- Red flags consistently penalise the dispensing failure mode ("with no
  student involvement", "delivers the complete explanation immediately",
  "writes the full practical report").

## 6. Age-appropriateness — CLEAN

All content pitched at GCSE (15-16); scaffolding-01 explicitly demands a
15-year-old pitch and red-flags undergraduate-level explanation. Tone
items model empathy-first handling of failure/frustration with no
inappropriate content; boundary items stay friendly in refusal.

## Minor observations (no action required)

1. Four items carry 2 red flags rather than 3 — within contract; adding a
   third (e.g. "no check the student followed the balancing" on
   socratic-01) would be optional enrichment only.
2. misconception-01 pedantry: in an open-crucible experiment measured mass
   CAN appear to drop if MgO smoke escapes; the item's framing ("turns
   into smoke and disappears" as a conservation-of-mass violation) is the
   standard GCSE misconception target and the expected behaviours are
   correct as written. A top tutor response might acknowledge the escaped-
   smoke caveat, and nothing here would penalise that.
3. Category names diverge from English's set by design (see section 2) —
   keep in mind for any cross-subject category roll-up.
