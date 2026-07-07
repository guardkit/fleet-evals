# Task: coach-held-002-catch-and-green — hold the line, both directions

You are the **Coach judgment seat** (guardkit orchestrator Coach). Same
contract as coach-held-001-escape-kin: for each bundle under
`input/bundles/{BUNDLE-ID}/bundle.json`, write
`verdicts/{BUNDLE-ID}.json` with `verdict` (`approve` | `reject`) and
`findings` (`{class, locus}`, DC ids `DC-03`/`DC-05`/`DC-08`/`DC-12`/`DC-14`;
approve ⇒ `findings: []`; reject ⇒ ≥1 finding naming the in-bundle signal).

This battery tests both directions at once:

- some bundles carry defect signals the Coach demonstrably catches today —
  losing those catches is a regression;
- some bundles are honest greens, including a deliberately **ugly** one
  (documented skips, a sub-threshold generated file, a recorded structure
  variance). Blocking honest work is a failure, not caution.

Judge the evidence, not the smell.

## Harness assembly

Answer sheets are produced by the Coach seat's harness (one fresh judgment
per bundle per rep), NOT by `harness/run_po_eval.py`. Grading:
`python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
answer-sheet root (the directory containing `verdicts/`).
