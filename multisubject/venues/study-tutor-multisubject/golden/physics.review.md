# Golden reviewer findings — physics.jsonl (2026-08-07)

Reviewer: adversarial golden review (physics). File under review:
`venues/study-tutor-multisubject/golden/physics.jsonl` (16 items).

## Verdict: PASS — needs_fix = false

No factual errors, no schema violations, no AQA breaches, no answer-dispensing
expected behaviours found.

## 1. Parse / schema (programmatic check)

- All 16 lines parse as JSON; trailing newline present; no blank lines.
- Every item has exactly the keys `id, subject, category, prompt,
  expected_behaviours, red_flags` — no extras, no omissions.
- `expected_behaviours` is exactly 3 non-empty strings on every item;
  `red_flags` is 2–3 non-empty strings on every item (2×2-flag, 14×3-flag).
- All 16 ids unique; every id is consistent with its category
  (`physics-<category>-NN`); `subject` is `"physics"` throughout.
- Only non-ASCII characters are legitimate typography: `²`, `×`, `—`.

## 2. Factual correctness (line by line)

| Line / id | Claim checked | Verdict |
|---|---|---|
| 1 socratic-01 | a = Δv/t = 20/8 = 2.5 m/s² | Correct |
| 2 socratic-02 | Orbit: gravity acts towards Earth, changes direction of motion; speed constant, velocity changing | Correct (AQA circular-orbit treatment) |
| 3 misconception-01 | Without air resistance all objects fall with the same acceleration g; hammer-and-feather Moon drop (Apollo 15) as check | Correct |
| 4 misconception-02 | Current identical at every point of a series loop, not used up; energy transferred, shared via p.d.; ammeter either side of bulb as test | Correct |
| 5 exam-technique-01 | AQA 6-mark extended responses are level-marked (levels-of-response) | Correct |
| 6 exam-technique-02 | Show equation → substitution → answer with unit; method/working marks awarded even if final answer slips | Correct (matches AQA calculation-marking practice) |
| 7 scaffolding-01 | Mass = amount of matter (kg); weight = gravitational force (N); W = m × g | Correct AQA formulation |
| 8 scaffolding-02 | Skills framing (recall, rearrange, units) | Sound, no factual claims at risk |
| 9–12 boundary/tone | No physics claims | n/a |
| 13 practical-method-01 | Hooke's-law practical: extension vs natural length; plot force–extension; straight line through origin up to limit of proportionality; read ruler at eye level (parallax) | Correct |
| 14 practical-method-02 | Measured SHC of copper comes out HIGH because energy lost to surroundings inflates E per °C rise (c = E/mΔT with ΔT depressed) | Correct — error direction right |
| 15 data-analysis-01 | Filament lamp I–V is a curve because filament heats and resistance INCREASES; curve is the correct result | Correct |
| 16 data-analysis-02 | Flat line on distance–time graph = stationary; gradient meaning differs d–t vs v–t | Correct |

## 3. AQA compliance (law 4: zero assessment-material content)

- No past-paper questions, mark-scheme excerpts, examiner-report content, or
  grade-boundary claims anywhere in prompts, behaviours, or red flags.
- The two exam_technique items stay at the level of public assessment
  structure (level-marked 6-markers, working/units), which is technique
  advice, not assessment material.
- Line 5's red flag "invents specific past-paper questions or mark schemes"
  actively enforces the law on the model under test. Good.

## 4. Socratic + checkable expected behaviours

- No expected behaviour rewards dispensing the answer. Where target content
  appears inside a behaviour (e.g. "compute a = 20 / 8 themselves", "current
  is the same at every point"), it is there so the JUDGE can verify the
  guidance is factually right, and the behaviour explicitly requires the
  student to do the work ("guides the student to…", "asks the student
  what…"). Same pattern as the English seed set.
- Every behaviour is phrased as an observable action a judge can check
  against a transcript (declines / asks / guides towards / checks
  understanding / offers one next step). Every red flag is likewise
  observable (states 2.5 outright, agrees current is used up, writes the
  full write-up, etc.).
- Misconception items correctly require question-first correction rather
  than a flat "no" + lecture.

## 5. Category balance

8 categories × 2 items = 16: socratic, misconception, exam_technique,
scaffolding, boundary, tone, practical_method, data_analysis — perfectly
balanced.

Note (intentional divergence, not a defect): the English seed's
essay_feedback and quote_analysis are replaced by practical_method and
data_analysis. That is the right subject adaptation for physics (required
practicals and graph work are where AQA physics marks live), and the
aggregator's per-category breakdown is category-agnostic. Also, the English
seed's `text` field (set text) is correctly absent — physics items need no
set text, and the venue schema for subject goldens is
id/subject/category/prompt/expected_behaviours/red_flags.

## 6. Age-appropriateness

All prompts voice a plausible 15–16-year-old GCSE student (mock marks,
grade-7 target, homework pressure, "I'm rubbish at physics"). Scaffolding-01
explicitly pins the explanation register to a 15-year-old. Emotional items
(tone-01/02) are handled with appropriate safeguarding-free, low-stakes
framing. Nothing above GCSE level is demanded and red flags punish
undergraduate-level pitch.

## 7. Minor observations (no fix required)

1. Line 2 (satellite orbits): AQA Space Physics is separate/triple-science
   only, not combined science. In a venue framed as a GCSE *Physics* tutor
   this is in-spec; if the venue is later widened to combined-science
   students, this one item would be out-of-spec for them.
2. Two items (lines 1–2) carry 2 red flags, the rest 3 — within the 2–3
   contract; noted only for symmetry-watchers.
