# Measured under a faulty instrument — read this before quoting any number from this run

**Run:** `20260821T224650Z-po-ft-v4` · exam `po-held-007-feature-spec` · 3 reps
**Noted:** 2026-08-22 · **Nothing in this directory has been changed, recomputed or removed.**

## What was wrong with the instrument

When these reps were graded, three of the exam's seventeen checks stepped aside
rather than running, because the graded answer carried no `qa/pass-bar-seed-*.yaml`
file. The three are:

    test_gate_po_held_007_f1_seed.py::test_seed_wellformed
    test_gate_po_held_007_f1_seed.py::test_criteria_observability
    test_gate_po_held_007_f1_seed.py::test_negative_path_honesty

The graded run is scored by the exit code of `pytest test/ -q`, and **pytest exits 0
when a check steps aside.** So a check that measured nothing was indistinguishable,
at the level the score is taken, from a check that measured everything and passed.

Fixed on 2026-08-22: a skipped check now makes the whole grade exit **40**, names
itself, and can never again be counted as a pass. See
`harness/could_not_measure.py` and
`docs/research/ideas/po-heldout-spec-extension-scope.md` §11.

## What these recorded results still support — and what they do not

**They still support the pass/fail verdict of every rep.** All three reps failed
checks that genuinely ran, so all three exited non-zero and were recorded as failures.
Re-measured on 2026-08-22 under the repaired instrument, over these exact directories:
**every rep produces the identical outcome on every single check, and the identical
exit code.** Nothing here was a false pass.

| rep | as recorded, 2026-08-21 | what was actually measured | exit code, then and now |
|---|---|---|---|
| rep1 | 12 passed, 2 failed | 12 passed, 2 failed, **3 not measured** | 1 → 1 |
| rep2 | 13 passed, 1 failed | 13 passed, 1 failed, **3 not measured** | 1 → 1 |
| rep3 | 5 passed, 2 failed, 7 errors | 5 passed, 2 failed, 7 errors, **3 not measured** | 1 → 1 |

**They do not support any per-axis score quoted out of seventeen, or any denominator
that silently drops the three.** A figure of the form "13 of 15" taken off rep2 is
wrong twice over: the exam has seventeen checks, and three of them returned no
information at all.

**The specific published number this touched** was "feature-spec at 13/15 on the best
rep", written into `ai-transition/docs/po-lane-state-2026-08-18.md` §17 and repeated in
§18.5. The product-owner lane corrected it in §21 of the same document on 2026-08-22:
it was 13 of **17**, with three axes not measured. That correction stands; this note is
the record beside the run itself.

## Why the seed was missing — and why it is not a model failure

The seed file is **not written by the model.** Production's `/feature-spec`
post-processor composes it from the model's own scenarios. Each rep's `config.json`
records, in `tree_source`, that this runner could not construct that post-processor and
fell back to slicing the model's file bundle — so no rep in this run could have produced
a seed whatever the model did. A red or unmeasured result on those three axes is a
finding about the harness, not about the tune.

Whether this exam should grade the seed at all is an open question for Rich, set out
with the evidence and the options in the scope document §11.6.

## If you want these axes measured

Re-run the exam under the repaired instrument. That is a **new** run with a new record.
It does not overwrite this one.
