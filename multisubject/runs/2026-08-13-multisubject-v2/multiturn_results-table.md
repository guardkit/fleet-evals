# Multi-Turn Evaluation Results

_24 scripted multi-turn tutoring scenarios, blind position-randomised holistic judging. Identical system prompt, decoding and student script; each candidate built its own side of the conversation._

## Head-to-head — judge preference (whole session)

| Outcome | Count |
|---|---|
| base preferred | 21 |
| finetune preferred | 2 |
| Tie | 1 |

## Mean dimension scores (1–5)

| Dimension | base | finetune | Δ |
|---|---|---|---|
| Socratic Stance | 3.92 | 4.21 | +0.29 |
| Aqa Alignment | 4.75 | 3.38 | -1.38 |
| Scaffolding | 4.83 | 3.42 | -1.42 |
| Subject Accuracy | 4.92 | 4.58 | -0.33 |
| Tone | 4.92 | 4.29 | -0.62 |
| Reasoning Visibility | 4.33 | 3.04 | -1.29 |
| Engagement Elicitation | 4.17 | 3.71 | -0.46 |

## Per-scenario verdicts

| Scenario | Winner | Rationale |
|---|---|---|
| mt-chemistry-ionic-covalent | base | A builds a full diagnose-support-stretch arc that extends to a new case (Group 2 magnesium) using precise electron-configuration numbers throughout, while B's closing turn just re-asks the same charge question already posed a turn earlier. Both stay chemically accurate and equally warm. |
| mt-chemistry-rates-discouraged | base | B extends collision theory from concentration to surface area to a temperature-vs-concentration comparison via fill-in-the-blank chains that keep the student constructing the answer, and correctly separates collision frequency from energy; A conflates 'frequency' with the conditions for a successful collision and hands over a fully worked 6-mark model before asking for practice. |
| mt-chemistry-titration-practical | base | B adds the relative-formula-mass step, makes the student recall the concordant-results value instead of supplying it, and closes with a full numeric titration calculation for the student to work through, directly answering the 'muddled with the calculations' request; A stays conceptual throughout and never reaches an actual number. |
| mt-physics-weight-vs-mass | base | B reaches an explicit numeric weight calculation on Earth and then the Moon, using a visible identify-substitute-calculate-state method, fulfilling the session's stated goal; A stays at concept-and-formula level and never gets the student to an actual calculation. |
| mt-physics-specific-heat-anxiety | base | B lays out an explicit 5-step 'battle plan' from turn one, uses a gentler warm-up example before specific heat capacity, and asks the anxious student to type out the actual question and extract values themselves; both are physically accurate with one minor typo apiece. |
| mt-physics-density-units | finetune | A's final turn becomes a long 'Golden Rules' reference lecture with only a token closing question, whereas B closes with a genuine dual-unit (g/cm3 and kg/m3) numeric conversion the student must actually work through, better matching the session's unit-consistency goal. |
| mt-macbeth-ladymacbeth | base | A builds a coherent AO1-to-AO2 arc with authentic quotation work and precise analytical vocabulary while still ending every turn on a live question; B's turns 4-5 repeat near-identical prompts almost verbatim, so the session stalls rather than advances. |
| mt-inspector-stuck | base | A gives the student concrete construction tasks (rewrite-the-sentence, complete-the-sentence, pick-the-stronger-option) that visibly escalate from AO1 plot-telling to AO2/AO3 analysis; B stays at a generic 'what words show that' register and repeats its two-question pattern without fresh textual grounding. |
| mt-poetry-compare | base | B grounds the comparison in authentic Ozymandias quotation ('shattered', 'trunkless', 'boundless and bare') and teaches a genuinely useful comparative-essay move (choosing a linking word to bridge the two poems); A stays conceptual throughout and never anchors a turn in actual text evidence. |
| mt-maths-simultaneous-signs | base | B explicitly generalises the add/subtract rule the session was meant to build ('different signs add, same signs subtract'), adds a correct bracket technique for protecting method marks, and closes with an exam sanity-check habit; A works the same method correctly but never states the transferable rule. |
| mt-maths-circle-theorems | base | A builds a memorable 'Big Three' clue-spotting framework and correctly nuances that the centre/circumference theorem needs the same arc, tying the strategy explicitly to method-mark risk; B is accurate but more generic, and its turn-4 example is under-specified for the student to actually pick a theorem. |
| mt-maths-sine-cosine-rule | base | A sustains a consistent surveyor/field framing and explicitly explains why each rule choice follows from the 'matching pair' logic, integrating the area formula into that same reasoning; B is equally correct but leans on the student's own recall without adding much new reasoning, especially on the area-formula turn. |
| mt-history-putsch-vs-chancellor | base | A stays purely Socratic but falls into a repetitive double-question pattern with little concrete structure; B trades some Socratic purity for a real sequencing task, explicit grade-boundary framing, and an AO4-style historiography stretch question on Hindenburg's motives. |
| mt-history-coldwar-discouraged | base | A keeps asking questions but never resolves the Blockade/Wall confusion or the describe-vs-explain distinction the student explicitly raised, leaving a discouraged pre-exam student without closure; B lands both with a four-stage timeline skeleton and a football-commentary analogy, then closes with a genuinely actionable exam-eve plan. |
| mt-history-elizabethan-16marker | base | A builds a genuine PEEL scaffold with concrete exercises (evidence-sorting, one-sentence conclusion, courtroom/reporter analogies) that develops turn by turn; B recycles generic 'think about PEEL again' prompts and repeats an almost verbatim question in turns 2 and 5 regardless of what the student actually asked. |
| mt-biology-genetics-probability | base | Both correctly diagnose the genotype-vs-phenotype error behind the student's 'half the babies' mistake, but B directly answers the student's 'what's the point' frustration with an accurate mark-by-mark breakdown of the 3-mark question before handing the final translation task back to the student. |
| mt-biology-osmosis | base | A stays tightly on AQA-spec vocabulary and builds a worked sentence-starter/'domino chain' model for the 4-mark answer; B introduces hypertonic/hypotonic terminology that is not part of the AQA GCSE Biology spec and drifts into an unrelated practical-design tangent that dilutes the osmosis explanation being built. |
| mt-biology-photosynthesis-practical | base | A asks a steady stream of questions but never lands why distance is used as an intensity proxy or confirms the inverse-square calculation, leaving the core concept ungrounded; B names the required-practical organism, explicitly teaches the IV/DV/CV framework, supplies an exam-ready phrase ('inverse square law'), and walks the calculation to a clear conclusion. |
| mt-french-etre-verbs | tie | Near-mirror sessions with the same DR & MRS VANDERTRAMP arc; A gives the fuller être-verb list the student explicitly asked for while B weaves AQA theme/spec language in more explicitly, offsetting into a genuine tie. |
| mt-french-discouraged-writing | base | A directly answers the 'I have to look up every word' complaint with concrete power-words and teaches real content (adjective agreement), while B ignores that complaint and contradicts its own 'keep it simple' advice by assigning a three-tense task the student then has to push back on. |
| mt-french-speaking-nerves | base | B teaches named, worked-example strategies (circumlocution, the Expansion Rule, Flexible Templates) that build across turns into a mock-exam finish, while A mostly stacks abstract rhetorical questions without landing on a concrete technique. |
| mt-spanish-tenses-stuck | base | Both build the same accurate photo/video preterite-imperfect distinction, but at the payoff moment B's 'what if you changed comí to comía' nearly hands over the correction outright, while A holds the Socratic line and ties explicitly to the AQA theme throughout. |
| mt-spanish-speaking-discouraged | finetune | A's exam breakdown and vocabulary are richer, but in the key complex-sentence turn it pre-assembles the whole answer in the correct order before asking the student to 'put it together,' undercutting the genuine construction work that B preserves throughout. |
| mt-spanish-future-examprep | base | A gives a candid grade-band assessment ('that's Level 4/5') and models the near-future/future-simple contrast with worked conjugations plus rich, accurate upgrade phrases, delivering more exam-relevant depth than B while both leave final construction to the student. |

