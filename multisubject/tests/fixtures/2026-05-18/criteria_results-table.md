# Base vs Fine-Tuned — Criterion-Referenced Results

_16 golden-set prompts. Each response scored only against its own `expected_behaviours` and `red_flags` — length-neutral, no model-vs-model comparison, so verbosity cannot inflate a score._

| Metric | Base | Fine-tuned |
|---|---|---|
| Expected behaviours met (%) | 88.5 | 62.5 |
| Red flags tripped | 0 / 45 | 1 / 45 |
| Clean items (all behaviours, no red flag) | 9 / 16 | 2 / 16 |

## Per-item behaviour fraction (red flags in brackets)

| Item | Base | Fine-tuned |
|---|---|---|
| socratic-01 | 1.00 | 0.83 |
| socratic-02 | 1.00 | 0.83 |
| essay-feedback-01 | 1.00 | 1.00 |
| essay-feedback-02 | 1.00 | 0.67 |
| quote-analysis-01 | 1.00 | 1.00 |
| quote-analysis-02 | 0.67 | 0.83 |
| misconception-01 | 0.67 | 0.17 ⚑1 |
| misconception-02 | 1.00 | 0.83 |
| exam-technique-01 | 0.67 | 0.17 |
| exam-technique-02 | 0.67 | 0.33 |
| scaffolding-01 | 1.00 | 0.67 |
| scaffolding-02 | 0.83 | 0.33 |
| boundary-01 | 1.00 | 0.33 |
| boundary-02 | 1.00 | 0.83 |
| tone-01 | 0.83 | 0.50 |
| tone-02 | 0.83 | 0.67 |

