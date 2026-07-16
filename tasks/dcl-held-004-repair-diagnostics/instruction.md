# Task: repair a rejected DCL capability so it compiles clean

You are given a **DCL (Declarative Capability Language) v1.0** capability document that
the compiler **rejected**, together with the compiler's verbatim diagnostics. Produce a
**compile-clean repair** that preserves the declared capability semantics. Emit **only**
the repaired DCL source. Save it as `response.dcl` in the output directory (nothing
stripped, no prose around it).

## Inputs (self-contained)

- [`input/broken.dcl`](input/broken.dcl) — the rejected capability (a `GET /stats` model).
- [`input/diagnostics.json`](input/diagnostics.json) — the checker's verbatim envelope on
  `broken.dcl` (`ok:false`, four error diagnostics with codes, lines, and columns).

## What "repair" means (the grade)

1. The repaired file must compile `ok:true` with **zero error diagnostics**.
2. It must **preserve the declared semantics** — the same capability, intent, outcome, and
   event the original was reaching for. Concretely, your repair must still declare:
   `capability GetStats`, `intent StatsRequest`, `outcome StatsRetrieved`, and
   `event StatsRetrievedEvent`. Renaming or dropping the capability, its intent shape, its
   outcome, or its event is **not** a repair — it changes what the capability is.

## The defects (read the diagnostics)

The four errors fall into two classes:

- **Invented closed-vocabulary literals** — DCL v1.0's actor kinds and effect kinds are a
  **closed vocabulary**. `actor Client is machine` and `effect ... is in_memory` name kinds
  that do not exist (`DCL_SEM_ACTOR_KIND_UNKNOWN`, `DCL_SEM_EFFECT_KIND_UNKNOWN`). Valid
  actor kinds include `human` and `system`; valid effect kinds include `persistence` and
  `notification`. An effect that no closed kind can honestly express should be removed
  rather than mislabelled.
- **A `when` branch naming an outcome that was never declared**
  (`DCL_SEM_UNKNOWN_OUTCOME`), which also leaves the declared outcome without a cause
  (`DCL_SEM_OUTCOME_CAUSE_REQUIRED`). Point the branch at the declared outcome.

Grade with: `PO_EVAL_OUTPUT_DIR=<output-dir> python3 -m pytest test/ -q`
