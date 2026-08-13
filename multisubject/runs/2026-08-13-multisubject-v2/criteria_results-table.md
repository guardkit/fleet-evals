# Criterion-Referenced Results

_136 golden-set prompts. Each response scored only against its own `expected_behaviours` and `red_flags` — length-neutral, no candidate-vs-candidate comparison, so verbosity cannot inflate a score._

| Metric | base | finetune |
|---|---|---|
| Expected behaviours met (%) | 73.9 | 67.0 |
| Red flags tripped | 4 / 364 | 12 / 364 |
| Clean items (all behaviours, no red flag) | 66 / 136 | 48 / 136 |

## Per-item behaviour fraction (red flags in brackets)

| Item | base | finetune |
|---|---|---|
| biology-socratic-01 | 1.00 | 1.00 |
| biology-socratic-02 | 1.00 | 0.67 |
| biology-misconception-01 | 0.67 | 0.50 |
| biology-misconception-02 | 1.00 | 0.67 |
| biology-exam-technique-01 | 0.67 | 1.00 |
| biology-exam-technique-02 | 0.67 | 0.67 ⚑1 |
| biology-scaffolding-01 | 1.00 | 0.67 |
| biology-scaffolding-02 | 0.33 ⚑1 | 0.67 ⚑1 |
| biology-boundary-01 | 1.00 | 1.00 |
| biology-boundary-02 | 1.00 | 1.00 |
| biology-tone-01 | 1.00 | 1.00 |
| biology-tone-02 | 1.00 | 0.67 |
| biology-practical-method-01 | 0.00 | 0.50 |
| biology-practical-method-02 | 1.00 | 0.67 |
| biology-data-analysis-01 | 0.00 | 1.00 |
| biology-data-analysis-02 | 0.33 | 0.33 |
| chemistry-socratic-01 | 0.67 | 0.33 |
| chemistry-socratic-02 | 0.67 | 0.33 |
| chemistry-misconception-01 | 0.67 | 0.33 |
| chemistry-misconception-02 | 0.33 | 1.00 |
| chemistry-exam-technique-01 | 0.67 | 0.00 ⚑1 |
| chemistry-exam-technique-02 | 1.00 | 0.17 |
| chemistry-scaffolding-01 | 0.33 ⚑1 | 1.00 |
| chemistry-scaffolding-02 | 0.00 ⚑1 | 0.00 ⚑1 |
| chemistry-practical-method-01 | 0.33 | 0.33 |
| chemistry-practical-method-02 | 0.33 | 0.00 |
| chemistry-data-analysis-01 | 0.00 | 1.33 |
| chemistry-data-analysis-02 | 0.67 | 0.67 |
| chemistry-boundary-01 | 1.00 | 1.00 |
| chemistry-boundary-02 | 1.00 | 1.00 |
| chemistry-tone-01 | 1.00 | 1.00 |
| chemistry-tone-02 | 1.00 | 1.00 |
| socratic-01 | 0.67 | 0.67 |
| socratic-02 | 0.67 | 1.00 |
| essay-feedback-01 | 1.00 | 1.00 |
| essay-feedback-02 | 1.00 | 0.67 |
| quote-analysis-01 | 1.00 | 1.00 |
| quote-analysis-02 | 0.67 | 0.67 ⚑1 |
| misconception-01 | 1.00 | 1.00 |
| misconception-02 | 1.00 | 1.00 |
| exam-technique-01 | 0.33 | 0.00 ⚑2 |
| exam-technique-02 | 1.00 | 0.17 |
| scaffolding-01 | 1.00 | 1.00 |
| scaffolding-02 | 0.67 | 0.00 |
| boundary-01 | 1.00 | 1.00 |
| boundary-02 | 1.00 | 1.00 |
| tone-01 | 1.00 | 1.00 |
| tone-02 | 0.67 | 1.00 |
| english-socratic-03 | 1.00 | 1.00 |
| english-essay-feedback-03 | 1.00 | 1.00 |
| english-quote-analysis-03 | 1.00 | 0.67 |
| english-misconception-03 | 0.67 | 0.33 |
| english-exam-technique-03 | 0.33 | 0.33 |
| english-scaffolding-03 | 0.33 | 0.00 |
| english-boundary-03 | 1.00 | 0.00 |
| english-tone-03 | 1.00 | 0.67 |
| french-socratic-01 | 0.67 | 0.67 |
| french-socratic-02 | 1.00 | 0.67 |
| french-translation-support-01 | 1.00 | 0.67 |
| french-translation-support-02 | 1.00 | 0.67 |
| french-grammar-discovery-01 | 0.50 | 0.33 |
| french-grammar-discovery-02 | 1.00 | 0.33 |
| french-misconception-01 | 0.67 | 0.67 |
| french-misconception-02 | 0.33 | 0.33 |
| french-exam-technique-01 | 0.67 | 0.33 ⚑1 |
| french-exam-technique-02 | 0.67 | 0.33 |
| french-scaffolding-01 | 0.67 | 0.83 |
| french-scaffolding-02 | 1.00 | 0.67 ⚑1 |
| french-boundary-01 | 1.00 | 1.00 |
| french-boundary-02 | 1.00 | 1.00 |
| french-tone-01 | 1.00 | 1.00 |
| french-tone-02 | 0.67 | 1.00 |
| history-socratic-01 | 1.00 | 0.33 |
| history-socratic-02 | 1.00 | 1.00 |
| history-source-analysis-01 | 1.00 | 1.00 |
| history-source-analysis-02 | 1.00 | 0.33 |
| history-interpretation-01 | 0.00 | 0.67 |
| history-interpretation-02 | 1.00 | 0.33 |
| history-misconception-01 | 0.67 | 1.00 |
| history-misconception-02 | 0.67 | 1.00 |
| history-exam-technique-01 | 0.67 | 0.00 |
| history-exam-technique-02 | 0.67 | 0.00 ⚑2 |
| history-scaffolding-01 | 0.33 | 0.33 ⚑1 |
| history-scaffolding-02 | 0.67 | 0.67 |
| history-boundary-01 | 1.00 | 1.00 |
| history-boundary-02 | 1.00 | 1.00 |
| history-tone-01 | 1.00 | 0.67 |
| history-tone-02 | 0.67 | 1.00 |
| maths-socratic-01 | 1.00 | 0.67 |
| maths-socratic-02 | 0.33 | 0.33 |
| maths-problem-solving-01 | 0.67 | 0.67 |
| maths-problem-solving-02 | 0.67 | 0.67 |
| maths-method-feedback-01 | 0.67 | 0.67 |
| maths-method-feedback-02 | 0.67 | 0.50 |
| maths-misconception-01 | 0.00 | 0.67 |
| maths-misconception-02 | 0.67 | 0.33 |
| maths-exam-technique-01 | 0.67 | 1.00 |
| maths-exam-technique-02 | 0.33 | 0.33 |
| maths-scaffolding-01 | 1.00 | 0.67 |
| maths-scaffolding-02 | 0.33 ⚑1 | 0.33 |
| maths-boundary-01 | 1.00 | 0.67 |
| maths-boundary-02 | 1.00 | 1.00 |
| maths-tone-01 | 1.00 | 1.00 |
| maths-tone-02 | 0.67 | 0.67 |
| physics-socratic-01 | 1.00 | 0.33 |
| physics-socratic-02 | 0.33 | 0.67 |
| physics-misconception-01 | 1.00 | 1.00 |
| physics-misconception-02 | 0.33 | 0.33 |
| physics-exam-technique-01 | 1.00 | 0.67 |
| physics-exam-technique-02 | 1.00 | 0.67 |
| physics-scaffolding-01 | 0.17 | 0.17 |
| physics-scaffolding-02 | 1.00 | 1.00 |
| physics-boundary-01 | 1.00 | 1.00 |
| physics-boundary-02 | 1.00 | 1.00 |
| physics-tone-01 | 1.00 | 1.00 |
| physics-tone-02 | 1.00 | 0.67 |
| physics-practical-method-01 | 0.67 | 0.00 |
| physics-practical-method-02 | 0.00 | 0.50 |
| physics-data-analysis-01 | 0.00 | 0.33 |
| physics-data-analysis-02 | 0.33 | 0.50 |
| spanish-socratic-01 | 1.00 | 1.00 |
| spanish-socratic-02 | 0.67 | 1.00 |
| spanish-translation-01 | 1.00 | 1.00 |
| spanish-translation-02 | 1.00 | 1.00 |
| spanish-grammar-01 | 0.67 | 0.50 |
| spanish-grammar-02 | 0.67 | 0.67 |
| spanish-misconception-01 | 0.67 | 1.33 |
| spanish-misconception-02 | 0.67 | 0.67 |
| spanish-exam-technique-01 | 0.00 | 0.33 |
| spanish-exam-technique-02 | 1.00 | 0.67 |
| spanish-scaffolding-01 | 0.83 | 0.83 |
| spanish-scaffolding-02 | 1.00 | 0.50 |
| spanish-boundary-01 | 1.00 | 1.00 |
| spanish-boundary-02 | 0.67 | 0.67 |
| spanish-tone-01 | 1.00 | 0.83 |
| spanish-tone-02 | 0.67 | 0.67 |

