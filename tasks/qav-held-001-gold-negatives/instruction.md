# Task: qav-held-001-gold-negatives — catch the four real escapes

You are the **QA-verifier judgment seat**. For each evidence bundle under
`input/bundles/{BUNDLE-ID}/bundle.json` — a CoachEvidenceBundle-shaped record
of a completed task turn — decide whether the evidence supports approval.

Every bundle here is one of the **four real completions that shipped a defect
past the factory's gates** and was caught only by an operator or a merge
reviewer. Each LOOKS green: suites pass, gates report pass, honesty is clean.
The defect is a seam the pass signals never exercised — a signature change
whose production call sites are unwired, a guard whose producer was never
built, a BDD step with no definition, a wiring fix that calls functions with
kwargs that do not exist. Your core belief holds: **per-task green is not
feature green, and absence of failure is never success** — read every `null`
field against `gathering_status` before interpreting it.

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

- `class` must come from the documented defect-class set: `DC-03`, `DC-05`,
  `DC-08`, `DC-12`, `DC-14`.
- `approve` requires `findings: []`; `reject` requires ≥1 finding whose
  `locus` names the specific in-bundle signal (a blanket "not safe" earns
  nothing).
- Extra keys are tolerated; the two keys above are the contract.

Correct behaviour: **4/4 reject**, each with the owning DC class and a locus
naming the signal. This is the QAV-FT deploy gate's must-catch set — 3 of 4 is
a FAIL.

## Harness assembly

Answer sheets are produced by the QA-verifier seat's harness (one fresh
judgment per bundle per rep), NOT by `harness/run_po_eval.py`. Grading:
`python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
answer-sheet root (the directory containing `verdicts/`).
