# ADR-EVAL-001: Blinding and pre-registration are the estate's ground rules

**Status:** Accepted (2026-08-07)
**Deciders:** Rich (standing practice ratified); recorded by the Lane 1 venue build
**Context repos:** fleet-evals (this estate); study-tutor (origin of the practice)

## Context

This ADR does not introduce new practice — it RECORDS practice that has
already stood since the 2026-05-18 base-vs-finetune eval (imported verbatim
at [`../history/2026-05-18-base-vs-finetune.md`](../history/2026-05-18-base-vs-finetune.md))
and that this estate now enforces by code. Three mechanisms:

1. **Seeded key split.** The blinding stage (`harness/judge/prepare.py`,
   lifted from study-tutor `judge_prepare.py`) uses a recorded RNG seed
   (2026-05-18 used `20260518`) to shuffle candidate→label positions per
   item, and writes TWO artefacts: `blind_pairs.jsonl` (no model labels — the
   only thing a judge sees) and `blind_key.json` (the label→candidate map).
   The seed makes the blinding itself reproducible and auditable.
2. **Key held back until raw judgements are committed.** The judge — human,
   session, or API — writes `raw_judgements.jsonl` over the blind labels
   only. The key is applied afterwards by a separate stage
   (`harness/judge/resolve.py`), and the raw file is committed BEFORE
   resolution. The 2026-05-18 run held this line ("the base/fine-tune key was
   not consulted until raw verdicts were committed") and it is why the
   base-wins result was credible enough to act on.
3. **Pre-registration before generation.** The venue's `PROTOCOL.md` —
   hypothesis, candidates, parity rule, data + n, judges + seeds, and the
   decision rule — is committed BEFORE any response is generated. The
   2026-05-18 runbook had its §7.2 decision matrix written down in advance;
   what it lacked was enforcement, and its n / single-judge / rubric gaps
   were arguable after the fact (required fixes #1–#7). Here the harness
   refuses to start a run for a venue with no `PROTOCOL.md`, and refuses
   while the protocol's Status is DRAFT — registration (the gate tap flipping
   DRAFT → REGISTERED, dated) is Rich's act
   (`harness/common.py::require_protocol`).

## Decision

- Every scored run in every venue uses the seeded three-file blinding split:
  blind pairs, held-back key, raw judgements committed pre-resolution. No
  judge — including an automated API judge — ever sees candidate identities.
- Every venue pre-registers: `PROTOCOL.md` committed before generation, with
  the decision rule fixed in advance; post-hoc re-scoring cannot change the
  registered rule. DRAFT protocols cannot start runs; the DRAFT→REGISTERED
  flip is Rich's gate tap.
- Runs are immutable evidence: `runs/<run>/` with a `MANIFEST.json` recording
  seeds, endpoints, model ids, GGUF sha256s, prompt SHAs, judge model, and
  repo HEADs. Corrections are new runs, never edits.

## Consequences

- A result can always be audited end-to-end: seed → blinding → raw verdicts
  → key → tables, with every input pinned by hash.
- "Just run it quickly" is impossible by construction — the friction is the
  point. The 2026-05-era Chemistry labeling defect (probes answered under the
  wrong preset, discovered months later) is the cost of unpinned, unregistered
  evidence; the per-row `subject`/`prompt_sha256`/`preset_id` stamping and
  this ADR's rules exist so that class of defect dies here.
- Protocol changes after generation force a new protocol version and a new
  run — slower, and deliberately so.
- The registered decision rule binds the OUTCOME side too: a verdict that is
  not acted on (the 2026-05-18 base-wins vs fine-tune-still-serving
  contradiction, required fix #5) must be resolved by a dated, signed note —
  no silent status quo.
