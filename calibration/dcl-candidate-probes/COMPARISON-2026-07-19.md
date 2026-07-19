# Gift-base candidate probes — COMPARISON (2026-07-19, informational numbers, not bar verdicts)

**Question (Rich's):** is a stock small model adequate at DCL authoring, so the laptop gift
needs no fine-tune? **Answer: NO — and Qwen3-4B is the base to tune.**

Frozen exam (suite re-freeze `8a3b9d1`) × {zero-shot, §10 protocol (vocab-ref + ≤1 repair)} ×
K=3, via llama-swap probe sets (config 2026-07-18). Per-rep artifacts + grades beside this doc.
Reference rows: our 35B seat's committed graded runs.

| Candidate (Q4 GGUF) | Zero-shot authoring | Zero-shot repair | Protocol authoring | Bar (≥2/3 each + 3/3 repair) |
|---|---|---|---|---|
| qwen36-workhorse 35B (reference) | 0/9 | 3/3 | **9/9** | **CLEARED** (07-17) |
| **Qwen3-4B-Instruct-2507** (~2.5GB) | 0/9 | **3/3** | 2/9 (2/3 · 0/3 · 0/3) | not met |
| Gemma-4-E4B-it (~4.7GB, post-refresh weights) | 0/9 | 1/3 | 0/9 | not met |

**Reading (3 sentences).** Neither small clears the bar stock: the protocol that lifts the
35B to 9/9 lifts Qwen3-4B only to 2/9 and Gemma-4-E4B not at all — model capacity, not
prompting, is the gap. Qwen3-4B's profile is exactly the trainable shape: perfect repair
(3/3 — the format/vocabulary knowledge is reachable) with weak zero-shot emission, which is
precisely the skill the 507-row compiler-verified corpus teaches; Gemma-4-E4B shows neither
skill and its license is messier for a public gift. **Recommendation: fine-tune
Qwen3-4B-Instruct-2507 (Apache-2.0) as the laptop gift; A/B the tuned model on this same
frozen exam — it must beat these stock numbers and hold repair at 3/3.**

Corpus context for the tune (same date): 87 fresh author rows (87/87 compile-clean;
113/200 hard-brief rejections = the quantified zero-shot ceiling on rich constructs) + 420
banked repair rows = 507 verified rows, contamination-pass.
