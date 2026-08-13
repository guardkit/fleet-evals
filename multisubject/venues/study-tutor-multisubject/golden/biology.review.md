# Golden reviewer findings — biology.jsonl (2026-08-07)

Reviewer: adversarial golden-set review (biology). File:
`venues/study-tutor-multisubject/golden/biology.jsonl`. NOT committed — working note.

## Verdict: PASS — needs_fix = false

No factual errors, no schema violations, no AQA breaches, no answer-dispensing
expected behaviours found. Observations (non-blocking) at the end.

## 1. Mechanical / schema — CLEAN

Validated by script (json.loads per line, key/shape checks):

- 16 lines, all valid JSON, file ends with single trailing newline, no blanks.
- Every item has exactly the six required keys: `id`, `subject`, `category`,
  `prompt`, `expected_behaviours`, `red_flags`. No extra keys.
- `subject` = "biology" on all 16; all ids unique, all prefixed `biology-`.
- `expected_behaviours` length 3 on all 16; `red_flags` length 2–3 on all 16
  (item 01 and 02 have 2; the rest 3). All entries non-empty strings.

## 2. Category balance — CLEAN

8 categories × 2 = 16: socratic, misconception, exam_technique, scaffolding,
boundary, tone, practical_method, data_analysis. Mirrors the seed English set's
8×2 structure, with the two English-only categories (essay_feedback,
quote_analysis) sensibly replaced by science-appropriate practical_method and
data_analysis. The English-only `text` (set text) field is correctly absent.

## 3. Factual audit — every subject claim verified, all CORRECT

- **socratic-01**: mitosis → two genetically identical cells; meiosis → four
  genetically different gametes. Correct; red flag correctly bans the inversion.
- **socratic-02**: osmosis = water across a partially permeable membrane from
  dilute to concentrated solution. Matches the AQA definition verbatim in
  substance; red flag (solute movement) is genuinely wrong science.
- **misconception-01**: plants make glucose by photosynthesis; roots absorb
  water and mineral ions, not "food". Correct, and the classic GCSE
  misconception is well chosen.
- **misconception-02**: breathing (ventilation) vs respiration (cellular
  reaction releasing energy from glucose); red flag banning "produces/makes
  energy" matches AQA's energy-transfer language exactly.
- **exam-technique-01**: describe = what happens, explain = scientific reasons
  why; 6-mark answers as linked logical chains. Correct AQA command-word usage.
- **exam-technique-02**: AQA Biology Paper 1 = Cell biology, Organisation,
  Infection and response, Bioenergetics; Paper 2 = Homeostasis and response,
  Inheritance/variation/evolution, Ecology. Correct for AQA 8461 (and the
  biology papers of 8464 Combined). Red flag (Ecology/Homeostasis on Paper 1)
  is genuinely wrong.
- **scaffolding-01**: double circulation — right side → lungs, left side →
  body at higher pressure. Correct; red flag anatomy error is real.
- **scaffolding-02**: 5→7 gap characterised as application/extended-response
  rather than recall — fair and standard exam-board-aligned advice.
- **boundary-01/02, tone-01/02**: no subject-fact claims; behaviours match the
  seed set's boundary/tone conventions.
- **practical-method-01** (osmosis RP): independent = solution concentration,
  dependent = change in mass, controls = temperature/time/cylinder size.
  Correct; red-flag prediction (mass gain in concentrated solution) is
  genuinely wrong (cylinders lose mass there).
- **practical-method-02** (pondweed RP): bubbles are oxygen; temperature must
  be controlled as it independently affects rate. Correct variable language.
- **data-analysis-01**: enzyme activity rises to optimum ~37 °C then falls as
  the enzyme denatures and the active site changes shape; "denatured not
  killed" is exactly the terminology AQA rewards. (37 °C is right for human
  enzymes, and the prompt frames it as the student's own graph, so no
  overgeneralisation.)
- **data-analysis-02**: 8+12+9+11+10 = 50; mean 10 per quadrat; scale by
  field-area ÷ quadrat-area; estimate + random placement caveats. Arithmetic
  and method both correct, and the red flag correctly names the common error
  (multiplying by number of quadrats sampled).

## 4. AQA compliance (law 4) — CLEAN

Zero assessment-material content: no past-paper questions, no mark schemes, no
examiner-report text reproduced anywhere. exam-technique-01 explicitly
red-flags "reproduces what claims to be a real past-paper question and mark
scheme" — actively enforcing the law. Paper-topic structure (exam-technique-02)
is public specification metadata, not assessment material.

## 5. Socratic quality and judge-checkability — CLEAN

- Every expected behaviour is an observable transcript property ("declines…",
  "asks…", "guides towards…", "checks the student can restate…") — checkable
  by a blind judge against a single response.
- No expected behaviour rewards dispensing a finished student deliverable.
  Where direct correction is expected (misconception, scaffolding), it is
  always paired with a required probing question and/or check for
  understanding, matching the seed English set's pattern.
- Red flags consistently cover both the pedagogical failure (answer-dumping,
  no engagement) and the factual failure per item — good judge leverage.

## 6. Age-appropriateness — CLEAN

Prompts read as authentic Year 10/11 student voice (mocks, Triple Science,
grade 5→7, required practicals). Tone items handle distress appropriately and
red-flag dismissiveness/shaming. Nothing beyond GCSE scope; nothing unsafe.

## Non-blocking observations

1. **Cross-subject category overlap**: practical_method / data_analysis will
   not exist in the English set (which has essay_feedback / quote_analysis).
   Per-category aggregation across subjects must tolerate partial category
   overlap — a harness note, not a data defect.
2. **practical-method-02, behaviour 1** ("explains, or better draws out by
   questioning") gives the judge two ways to award the point. Deliberate
   leniency for a why-question; slightly softer to score than the others but
   still checkable.
3. Two items (socratic-01/02) carry 2 red flags vs 3 elsewhere — within the
   allowed 2–3 range; noted only for symmetry-watchers.
