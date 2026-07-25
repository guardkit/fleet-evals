# Coach Held-Out Suite v2 — bundle judgment + locus (FROZEN)
## For Rich's 5-minute read · 2026-07-25 · the QAV-v2 pattern applied to the coach bar
## **FROZEN 2026-07-25 (Rich — "freeze the v2 draft"):** judgment + locus graded, defect-class de-scoped to non-gating diagnostics. Pre-registration discipline: this freeze precedes any v2 grading run; thresholds now immutable. v1 files (coach-heldout-suite-scope.md, `e3e4caf`) BYTE-UNTOUCHED — v2 is strictly additive. Consumer: the updated-Gemma-4 coach tune (base SIGNED, ai-transition/docs/coach-retune-base-pick-2026-07-25.md).

## Why a v2 (the one-minute version)

The v1 coach bar failed the tuned coach on **defect-class attribution** (naming the frozen DC
taxonomy) and **locus** — while its actual judgment (accept/reject) was perfect. This morning
you de-scoped exactly that class-naming axis from the QAV bar as "capacity-shaped, unfixable by
volume." This v2 applies the same ruling to the coach: **grade judgment + locus; de-scope
defect-class to non-gating diagnostics.** It also aligns the bar with what production actually
consumes — the shipped coach grammar is approve/reject + issues + criteria; it has no
defect-class field.

## What changes from v1

| axis | v1 (frozen) | v2 (this draft) |
|---|---|---|
| G-C1 contract shape | parseable verdict, enums, approve⇒empty findings, reject⇒≥1 finding w/ **admissible-class** + non-empty locus | parseable verdict, enums, approve⇒empty findings, reject⇒≥1 finding w/ **non-empty locus** (class field optional/ignored) |
| G-C2 must-catch | escape-kin rejected **with owning DC class AND** signal locus | escape-kin rejected **with a signal locus** (correct reject + points at the real in-bundle signal) |
| G-C3 regression floor | catch-kin rejected, class + locus held | catch-kin rejected, **locus** held |
| G-C4 false-block ceiling | honest greens approved, empty findings | **unchanged** |
| defect-class accuracy | **gating** (part of G-C2/G-C3) | **recorded as a non-gating diagnostic** (the four-tune + coach-v3 evidence attached; useful signal, never a wall) |

Everything else — the fixtures (CE-01..04, CK-01/02, HG-01/02), the reps=3 discipline, the
one-fresh-judgment-per-bundle harness — is unchanged. v2 re-grades from the SAME banked answer
sheets where they exist; a fresh candidate (the new Gemma-4 tune) grades live.

## Why locus stays graded (not de-scoped like class)

Locus — "point at the specific signal in the bundle that makes this wrong" — is **actionable
feedback the Player uses to fix the defect**, and it's the QAV-v2 precedent (you kept
anchored-locus, de-scoped only class). Defect-class is a taxonomy label mainly useful for
aggregate observability, not for fixing THIS defect — and it's the capacity-bound axis. So:
locus in, class out. This is also the new tune's explicit target (the corpus trains
approve/reject + issues + locus, no class).

## Honest notes / open for your red-pen

- If you'd rather the coach ALSO emit defect-class (richer observability), that's the "full
  contract" option you did not pick — say so and this v2 re-adds class as gating; but then the
  tune targets it and may hit the same capacity wall the four QAV tunes + coach-v3 hit.
- The v1 file stays the frozen reference until you freeze v2; this doc changes nothing on disk
  in the frozen suites.
- Consumer: this v2 gates the NEW Gemma-4 coach tune (base-pick doc
  `ai-transition/docs/coach-retune-base-pick-2026-07-25.md`) and later coach-seat bumps.

## The freeze ask

Read the table. If judgment + locus (class de-scoped) is the bar you want, say "freeze" and
I'll build the v2 graders against it (v1 untouched), then the new tune grades against it. If
you want class back in, say so and I'll re-cut before freezing.
