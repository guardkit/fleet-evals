# Base vs Fine-Tuned — Evaluation Results

_Generated 2026-05-18 — 16 golden-set prompts, blind position-randomised Claude-as-judge. Both models served at Q4_K_M via llama.cpp and given an identical system prompt and greedy decoding (temperature 0); the only variable is the weights._

## Head-to-head — judge preference

| Outcome | Count | Share |
|---|---|---|
| Fine-tune preferred | 1 | 6% |
| Base preferred | 15 | 94% |
| Tie | 0 | 0% |

## Mean dimension scores (1–5)

| Dimension | Base | Fine-tuned | Δ |
|---|---|---|---|
| Socratic Stance | 4.31 | 4.25 | -0.06 |
| Aqa Alignment | 3.50 | 2.06 | -1.44 |
| Scaffolding | 4.62 | 3.38 | -1.25 |
| Subject Accuracy | 4.81 | 4.00 | -0.81 |
| Tone | 4.62 | 4.06 | -0.56 |
| Reasoning Visibility | 1.44 | 2.88 | +1.44 |

## Win rate by prompt category

| Category | Fine-tune | Base | Tie |
|---|---|---|---|
| boundary | 0 | 2 | 0 |
| essay_feedback | 0 | 2 | 0 |
| exam_technique | 0 | 2 | 0 |
| misconception | 0 | 2 | 0 |
| quote_analysis | 1 | 1 | 0 |
| scaffolding | 0 | 2 | 0 |
| socratic | 0 | 2 | 0 |
| tone | 0 | 2 | 0 |

## Deterministic checks

| Metric | Base | Fine-tuned |
|---|---|---|
| Inline `<think>` block in output (%) | 0.0 | 62.5 |
| Reasoning present, either channel (%) | 0.0 | 62.5 |
| Template-token leaks, visible stream (must be 0) | 0 | 0 |
| Visible answer contains a question (%) | 100.0 | 100.0 |
| Mean visible-answer length (words) | 212.3 | 95.1 |

