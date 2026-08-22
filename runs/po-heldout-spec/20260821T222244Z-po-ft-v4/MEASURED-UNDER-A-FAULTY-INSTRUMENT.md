# Measured under a faulty instrument — read this before quoting any number from this run

**Run:** `20260821T222244Z-po-ft-v4` · exam `po-held-007-feature-spec`
**Noted:** 2026-08-22 · **Nothing in this directory has been changed, recomputed or removed.**

## What this run actually is

An aborted first attempt, superseded twenty-four minutes later by
`20260821T224650Z-po-ft-v4`. The runner wrote the model's files flat instead of into
`features/<slug>/`, so every structural check failed or errored on the layout before it
could look at the content. `rep3` produced no files at all — there is no `config.json`
and no `grade.txt` for it. There is no `run_summary.json` for this run.

**No score should be quoted from it in any form.** It is kept because a discarded
attempt is part of the record.

## The instrument fault, for completeness

The same fault applies here as to the run that superseded it: a check that could not
measure anything stepped aside, and a step-aside was scored as a pass. In this run only
one of the three quality-bar-seed checks stepped aside —
`test_gate_po_held_007_f1_seed.py::test_negative_path_honesty` — because the other two
errored on the missing `features/` directory first.

Every rep exited non-zero on genuine failures, so nothing here was a false pass.
Re-measured on 2026-08-22 under the repaired instrument: identical outcome on every
check, identical exit code.

The fix, and the ruling behind it, are in `harness/could_not_measure.py` and
`docs/research/ideas/po-heldout-spec-extension-scope.md` §11.
