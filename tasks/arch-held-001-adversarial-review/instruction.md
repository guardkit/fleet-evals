# Task: arch-held-001-adversarial-review — stress-test a candidate design

You are the **architect review seat** (specialist-agent `roles/architect`,
Coach-side judgment). You are given a design-review packet:

- `input/goals.md` — the complete product requirements record
- `input/design.md` — the candidate architecture under review
- `input/repo-manifest.json` — ground truth of what exists in the codebase

Your job is the adversarial pass the drafting Player cannot do for itself:
**trace the flows, check every element's traceability, and stress-test the
design before accepting it.** Accepting a flawed design is the failure mode
under test.

## Output contract (graded)

Write exactly one file at the answer-sheet root:

```
review.json
```

```json
{
  "verdict": "approve" | "revise",
  "findings": [
    {
      "pattern": "<detection-pattern id>",
      "target": "<the design element the finding lands on>",
      "evidence": "<why it is a defect, grounded in goals/design/manifest>"
    }
  ]
}
```

- `pattern` must be one of the architect detection taxonomy ids: `PHANTOM`,
  `UNGROUNDED`, `SCOPE_CREEP`, `MISSING_TRADEOFF`, `SOURCE_COLLAPSE`,
  `DOMAIN_DILUTION`, `UNSTATED_ASSUMPTION`, or `MISSING_SEAM` (a required
  interaction with no path in the design).
- `approve` means publishable as-is and **requires `findings: []`** — a
  blocking finding forces `revise`. `revise` requires ≥1 finding.
- Every finding names a concrete `target` and grounds its `evidence` in the
  packet. One defect per finding — a finding that sprays keywords across
  many unrelated defects counts for nothing.

## Harness assembly

Answer sheets are produced by the architect review seat's harness (one fresh
session per rep) with the packet mounted read-only; this task is NOT
assembled by `harness/run_po_eval.py` (the artifact is `review.json`, not
`response.txt`). Grading: `python3 -m pytest test/ -q` with
`PO_EVAL_OUTPUT_DIR` pointing at the answer-sheet root.
