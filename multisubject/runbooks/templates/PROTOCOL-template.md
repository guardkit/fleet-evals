# PROTOCOL: <venue> (<one-line what-is-being-decided>)

> **How to use this template.** Copy to `venues/<venue>/PROTOCOL.md`, fill
> every section, and COMMIT IT BEFORE any response is generated. The
> harness refuses to start a run for a venue without this file
> (`harness/common.py::require_protocol`) — pre-registration is enforced by
> code, not prose (2026-05-18 required fix #6). Changing this file after
> generation is a new protocol version and a new run.

**Status:** DRAFT | REGISTERED (Rich's gate tap, dated)
**Registered:** YYYY-MM-DD by <name>
**Venue:** `venues/<venue>/`

## Hypothesis

What claim is this run designed to test? One or two sentences, falsifiable.

## Candidates

Point at `candidates.yaml` and state, per candidate: model id, quantisation,
serving runtime, and the GGUF sha256 (provenance verified — no checksum, no
run).

## Parity rule

What is held identical across candidates (system prompt + SHA, decoding
params, quantisation, runtime family, prompt set). The only variable must be
the weights. Note any known asymmetry honestly (e.g. chat-template
substitutions) — the 2026-05-18 run's base-served-with-tutor-jinja caveat is
the model here.

## Data

Which golden sets / scenario files / probe sets, with n per track. The
2026-05-18 lesson: the runbook's own bar is 24–32 single-turn prompts
(required fix #1) — justify anything smaller.

## Judging

- Judge(s): model id(s) — and whether a session judge is also used
  (conflict-of-interest note: the judge must not be the executing session
  alone; required fix #3).
- Seeds: blinding seed(s). ≥2 judges or seeds, with agreement reported
  (required fix #2).
- Rubrics: which `harness/rubrics/*.md` files, by subject. DRAFT rubrics
  are barred from scored runs.
- Human spot-check: how many full items (2026-05-18 used 3–4).

## Decision rule (pre-registered)

The decision matrix, committed before generation. Model on study-tutor's
RUNBOOK-base-vs-finetune-tutor-eval.md decision matrix: for each plausible
outcome bracket, the action that will be taken. No post-hoc re-scoring may
change the registered rule.

| Outcome | Action |
|---|---|
| <e.g. finetune wins ≥ 60% and no red-flag regression> | <ship / keep serving> |
| <e.g. base wins> | <name the consequence — the 2026-05-18 verdict/serving contradiction (fix #5) must not recur> |

## Outputs

`runs/YYYY-MM-DD-<venue>-<slug>/` with MANIFEST.json + a RESULTS write-up
from `runbooks/templates/RESULTS-template.md`.
