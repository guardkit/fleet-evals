# Base vs Fine-Tuned — Multi-Turn Evaluation Results

_3 scripted multi-turn tutoring scenarios, blind position-randomised holistic judging. Identical system prompt, greedy decoding and student script; each model built its own side of the conversation._

## Head-to-head — judge preference (whole session)

| Outcome | Count |
|---|---|
| Fine-tune preferred | 0 |
| Base preferred | 2 |
| Tie | 1 |

## Mean dimension scores (1–5)

| Dimension | Base | Fine-tuned | Δ |
|---|---|---|---|
| Socratic Stance | 4.00 | 5.00 | +1.00 |
| Aqa Alignment | 4.67 | 3.00 | -1.67 |
| Scaffolding | 5.00 | 3.67 | -1.33 |
| Subject Accuracy | 5.00 | 4.33 | -0.67 |
| Tone | 5.00 | 4.00 | -1.00 |
| Reasoning Visibility | 1.33 | 3.33 | +2.00 |

## Per-scenario verdicts

| Scenario | Winner | Rationale |
|---|---|---|
| mt-macbeth-ladymacbeth | tie | Both are strong, goal-focused sessions. A draws the analysis out of the student turn by turn with consistently Socratic questions and never hands over the answer; B teaches more explicitly, modelling a grade-5 vs grade-8/9 sentence and ending with a concrete thesis-writing task. A genuine tie — the difference is style, not quality. |
| mt-inspector-stuck | base | A gives a discouraged student concrete AO2 tools — a word/technique/effect cheat sheet and a worked practice quote — directly meeting their stated 'I never know what to write'. B stays purely Socratic and warm but, for a student who explicitly cannot do AO2, leaves them cycling through 'what do you notice?' questions without a concrete method. |
| mt-poetry-compare | base | B teaches poem-comparison technique explicitly (comparative connectives, a model 'whereas' sentence) and stays accurate throughout. A is fluently Socratic but misnames 'My Last Duchess' as 'Nuit's Last Duchess' in the opening turn — a factual slip in the very lesson meant to teach that poem. |

