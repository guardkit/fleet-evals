# Task: arch-held-002-sound-design-review — do not fabricate blockers

You are the **architect review seat** (specialist-agent `roles/architect`,
Coach-side judgment), reviewing the same-shaped packet as
arch-held-001-adversarial-review:

- `input/goals.md` — the complete product requirements record
- `input/design.md` — the candidate architecture under review
- `input/repo-manifest.json` — ground truth of what exists in the codebase

Stress-test the design exactly as you always do. The failure mode under test
here is the inverse one: **inventing blockers a sound design does not have.**
A review seat that fails everything is as useless as one that approves
everything.

## Output contract (graded)

Identical to arch-held-001: one `review.json` at the answer-sheet root with
`verdict` (`approve` | `revise`) and `findings`
(`{pattern, target, evidence}` — same taxonomy enum). `approve` means
publishable as-is and requires `findings: []`; a blocking finding forces
`revise`.

## Harness assembly

Answer sheets are produced by the architect review seat's harness (one fresh
session per rep) with the packet mounted read-only; NOT assembled by
`harness/run_po_eval.py`. Grading: `python3 -m pytest test/ -q` with
`PO_EVAL_OUTPUT_DIR` pointing at the answer-sheet root.
