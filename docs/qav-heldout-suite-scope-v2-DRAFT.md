# QAV held-out suite — scope **v2** — ⚠ DRAFT, NOT FROZEN — awaiting Rich's ratification

**Status: DRAFT.** The frozen v1 (`docs/qav-heldout-suite-scope.md` @ `2165802`) is untouched
and remains the bar of record for every sitting to date (v1–v4, all NO-DEPLOY, results stand).
This page becomes binding only on Rich's explicit freeze; the v2 graders are built only after
that freeze, against this text.

## The one-minute version

**What changes:** a pass no longer requires the judge to name the internal defect-class code
(DC-03/05/08/12/14) on its findings. **What does NOT change:** everything the product actually
consumes stays strictly graded — the judge must still reject every planted defect, approve
every honest green (clean and ugly), speak the exact serving contract, and **point at the
right evidence** (the anchor requirement stays: a finding whose locus does not name the
in-bundle signal still fails). The class code becomes recorded diagnostics, and in production
it is derived downstream from the locus — never asked of the model's memory.

**Why (the four-tune evidence, receipts in RESULTS-qav-ft-v1..v4):** across four frozen
sittings the verdict layer was perfect every time, the evidence-pointing layer reached 14/15
by v4, and the class-naming layer never exceeded 2/15 — with the wrong-class attractor
migrating to whichever class the corpus most recently grew (DC-12 → wobble → DC-05). Four
probes establish that class-naming tracks corpus-support gradients, not taxonomy semantics:
the bar was a proxy for understanding, and the anchor evidence now measures that directly.
Changing a bar we just failed is only honest done in the open: hence this page, versioned,
with the old bar preserved and the reasons attached.

## The v2 gates (per rep, per task — grading semantics)

| Gate | v1 | **v2** |
|---|---|---|
| G-Q1 contract | bare loadable verdict JSON per bundle | **unchanged** |
| G-Q2 must-catch | 4/4 gold negatives rejected **with owning class + anchored locus** | 4/4 rejected **with anchored locus** (class recorded, not graded) |
| G-Q3 catch floor | RC-01 rejected with owning class + anchor | RC-01 rejected **with anchor** (class recorded, not graded) |
| G-Q4 false-block | 0 honest/ugly greens blocked | **unchanged** |
| NEW: class diagnostics | — | per-rep `findings[].class` vs owning class, recorded in RESULTS as a non-gating table |

Pass = all four gates, all reps — same K=3 discipline, same runner, same frozen bundles
(tasks/qav-held-001, qav-held-002 are NOT edited; only the grading assertions change, in a
new test version living beside the old one).

## The rollout this bar unlocks (gate 1 of the pre-registered ladder)

**Shadow mode:** the seat runs log-only beside every Coach verdict on every factory build —
it never blocks, and a down seat records "absent", never a failure. Each disagreement becomes
a receipt adjudicated at normal merge review (verdict right/wrong + the class, seconds each) —
building the real-world class library the synthetic corpus could not. **Graduation to gate 2
(block-with-override) is a separate future Rich decision on pre-registered burn-in numbers** —
proposed defaults to edit or accept at freeze time: minimum 25 shadow-judged builds, zero
adjudicated false-blocks, shadow-catch of any adjudicated true escape. Nothing graduates
automatically.

## Freeze mechanics (so the record stays honest)

On Rich's word ("frozen", or edits then "frozen"): this file is renamed to drop the DRAFT
mark, committed with his ratification line and date, and its commit sha becomes the v2 freeze
reference quoted by every future RESULTS. v1 stays in place; historical RESULTS keep citing
`2165802`. The v2 graders are then built (new test files beside the frozen v1 tests, coach-
reviewed) and `qav-ft-v4` re-graded against v2 from its existing, untouched answer sheets —
no new model sitting is needed for the re-grade, and no retrain occurs (the park stands).

*Drafted 2026-07-25 by the post-park coordinator per Rich's "continue with your QAV
recommendations"; evidence base: RESULTS-qav-ft-v1/v2/v3/v4 + adf tune-train receipts.*
