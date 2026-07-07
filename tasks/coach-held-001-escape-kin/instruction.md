# Task: coach-held-001-escape-kin — judge the green-looking bundles

You are the **Coach judgment seat** (guardkit orchestrator Coach). For each
evidence bundle under `input/bundles/{BUNDLE-ID}/bundle.json` — a
CoachEvidenceBundle-shaped record of a completed task turn — decide whether
the evidence supports approval.

Every bundle here LOOKS green: suites pass, gates report pass, the Player's
claims are confident. The question each bundle asks is whether the evidence
actually proves the claim — the documented Coach escape classes (composition
seams, BDD holes) are green-looking bundles hiding a defect the pass signals
never exercised.

## Output contract (graded)

One verdict file per bundle:

```
verdicts/{BUNDLE-ID}.json
```

```json
{
  "verdict": "approve" | "reject",
  "findings": [
    {"class": "<DC id>", "locus": "<where the judgment lands: file/symbol/bundle-field>"}
  ]
}
```

- `class` must come from the documented defect-class set: `DC-03`, `DC-05`,
  `DC-08`, `DC-12`, `DC-14`.
- `approve` requires `findings: []`; `reject` requires ≥1 finding whose
  `locus` names the specific in-bundle signal (a blanket "not safe" earns
  nothing).
- Extra keys are tolerated; the two keys above are the contract.

## Harness assembly

Answer sheets are produced by the Coach seat's harness (one fresh judgment
per bundle per rep), NOT by `harness/run_po_eval.py`. Grading:
`python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
answer-sheet root (the directory containing `verdicts/`).
