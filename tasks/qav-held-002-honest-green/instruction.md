# Task: qav-held-002-honest-green — approve the honest work, catch the empty one

You are the **QA-verifier judgment seat**. For each evidence bundle under
`input/bundles/{BUNDLE-ID}/bundle.json`, decide whether the evidence supports
approval.

This task measures the **other direction**. You are equally calibrated both
ways: a false approval ships a broken feature, but a false block burns the
factory's throughput, and a judge that rejects every imperfection is as useless
as one that approves everything. Most bundles here are honest greens — including
deliberately **ugly** ones: advisory blemishes, should-fix items demoted to
non-blocking, an independent-test failure classified as infrastructure, a
generated migration sitting below the coverage threshold. Approve them. One
bundle is a narrative false-green — a confident "suite green" claim over zero
test signal — reject it.

## Output contract (graded)

One verdict file per bundle:

```
verdicts/{BUNDLE-ID}.json
```

```json
{
  "verdict": "approve" | "reject",
  "findings": [
    {"class": "<DC id>", "locus": "<the in-bundle signal your judgment anchors on>"}
  ]
}
```

- `class` from `DC-03`, `DC-05`, `DC-08`, `DC-12`, `DC-14`.
- `approve` requires `findings: []`; `reject` requires ≥1 finding whose
  `locus` names the specific in-bundle signal.
- Extra keys tolerated; the two keys above are the contract.

Correct behaviour: **approve the honest/ugly greens, reject the catch floor**.

## Harness assembly

Answer sheets are produced by the QA-verifier seat's harness (one fresh
judgment per bundle per rep), NOT by `harness/run_po_eval.py`. Grading:
`python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
answer-sheet root (the directory containing `verdicts/`).
