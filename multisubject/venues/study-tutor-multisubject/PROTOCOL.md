# PROTOCOL: study-tutor-multisubject (does one English fine-tune, differentiated only by subject system prompts, tutor Socratically across GCSE subjects — and does it beat the base model at it?)

> Pre-registration document per `runbooks/templates/PROTOCOL-template.md`.
> The harness refuses runs for a venue with no PROTOCOL.md, and refuses
> scored runs while this file's Status is DRAFT
> (`harness/common.py::require_protocol`). Changing this file after any
> generation is a new protocol version and a new run.

**Status:** REGISTERED (v2) — Rich's gate tap given 2026-08-07 ("Tap it —
freeze as drafted"); **amended v2 BEFORE any generation and re-registered on
Rich's word 2026-08-13 ("amend: subscription + local judges")** — the judging
clause only; no other clause changed. Pre-registration is BINDING: changing
this file after any generation is a new protocol version.
**Registered:** 2026-08-07 (v1) · 2026-08-13 (v2, judging amendment)
**Venue:** `venues/study-tutor-multisubject/`

This protocol supersedes-by-fixing the 2026-05-18 base-vs-finetune eval
(imported verbatim at `docs/history/2026-05-18-base-vs-finetune.md`) and the
2026-05-era 17-probe informal validation. It encodes all seven required fixes
pinned in the Lane 1 design pass; each is tagged **[fix #N]** below.

## Hypothesis

H1: Under identical per-subject system prompts, the `gemma4-tutor` fine-tune
produces Socratic tutoring behaviour (asks-before-tells, scaffolds, subject-
appropriate pedagogy) at least as well as the base `gemma-4-26B-A4B-it` in
every subject — not only English. H0 (live, per the 2026-05-18 result): the
base model equals or beats the fine-tune everywhere except
reasoning-visibility and multi-turn Socratic stance.

Secondary, probe-track claim under test: the ADR-TUTOR-MULTI-SUBJECT
"all subjects validated" claim — currently 15/17 informal with Chemistry
UNBACKED (both C probes were answered under the Biology preset; see
`probes-17/probes.jsonl` C1/C2 annotations). A correctly-bound Chemistry
re-run is REQUIRED before that ADR row can be restored.

## Candidates

`candidates.yaml` (two-way seed pair: `base` = `gemma4-base`,
`finetune` = `gemma4-tutor`, both via llama-swap `http://localhost:9000/v1`).

Provenance gate — no checksum resolution, no run (scored-run blockers, stated
plainly in `runbooks/RUNBOOK-serve-candidates.md`):

- `gemma4-tutor`: served GGUF's local sha256 is
  `675424b0021ad7b78699e4bf1da404ca57c70f5c581a9ce11209fbe22b7a3144` but its
  provenance is **UNVERIFIED** — the HF repo
  `RichWoollcott/studytutor-gcse-26b-moe` is safetensors+LoRA only, so **no
  GGUF comparator exists**. Resolution (an operator act) is REQUIRED before
  any scored run; if the served file turns out to be the base GGUF, a run
  would be base-vs-base.
- `gemma4-base`: **NOT ON HOST** — no seat, no GGUF. Registration (~16 GB
  download + config block + llama-swap restart) is an operator act.

## Parity rule

Held identical across candidates (the 2026-05-18 parity rule, verbatim in
spirit): the per-subject system prompt **by pinned sha256** from `prompts/`
(`PROMPTS-PROVENANCE.md` is the manifest — English =
`prompts/english.txt`, the canonical survivor of the GB10
`system-prompt.txt`); greedy decoding (`temperature 0`, fixed `max_tokens`);
the same `llama-server` binary via llama-swap; ~4-bit K-M quantisation;
frozen prompt sets. The only variable is the weights.

Known asymmetry to record honestly in RESULTS (modelled on 2026-05-18): if
the base again requires the fine-tune's `gemma4-tutor.jinja` chat template to
avoid `<|channel>` 500s, both models run the same template — tighter parity,
logged as a caveat, not hidden.

## Data

| Track | Source | n | Status |
|---|---|---|---|
| Single-turn golden, English | `golden/english.jsonl` | 16 today → **24+ required [fix #1]** | The runbook's own bar is 24–32; 16 was the 2026-05-18 deadline floor. 8+ items must be authored before registration. |
| Single-turn golden, per subject | `golden/<subject>.jsonl` | **24+ per subject [fix #1]** | NOT YET AUTHORED — registration is blocked until each subject in scope has its set. A subject with no golden set is out of scope for the scored claim, not silently skipped. |
| Multi-turn | `golden/multiturn/scenarios.jsonl` | 3 scripted sessions | Lifted; extension optional. |
| Probes (informal smoke track) | `probes-17/probes.jsonl` | 17 (M×4 F×3 S×2 H×3 B×3 C×2) | C1/C2 MUST be re-run under the real `gcse-chemistry` preset; every probe row's output is stamped `subject` + `prompt_sha256` + `preset_id` so the Biology-labeling defect cannot recur. Physics has a preset+prompt but no probes — out of probe scope. |

## Judging

- **Judge path [fix #3, AMENDED v2 — Rich, 2026-08-13: "amend: subscription
  + local judges"]: two independent judges, NEITHER the executing session and
  NEITHER a paid frontier API call.** The 2026-05-18 conflict was the same
  context generating and judging; the integrity mechanism is the blinding
  plus judge independence, not API spend. The registered judges:
  - **Judge A — a fresh-context Claude subagent** (subscription usage): a
    clean session that receives ONLY the blind pairs + the rubric — never the
    identity key, never the generation logs, never this protocol's candidate
    names. Its raw judgements are committed before the key is applied.
  - **Judge B — `gpt-oss-120b` served locally on llama-swap `:9000`**: a
    different model family from both candidates (no family bias), zero cost,
    fully household.
  The API judge (`harness.judge.pairwise_api`) is RETAINED as an explicitly
  priced TIEBREAK option only — run it only on Rich's word, only over items
  where A and B disagree, and record the spend in RESULTS.
- **≥ 2 judges, agreement reported [fix #2]:** satisfied by A+B above —
  per-item win-agreement between the two judges in RESULTS; the registered
  verdict is their agreement set, with disagreements itemised (and either
  carried as "split" honestly or tiebroken per the clause above). Judge model id(s) are fixed
  at registration time.
- **Per-subject rubrics [fix #4]:** `harness/rubrics/<subject>.md`, selected
  by each item's `subject` field. The English-only rubric made
  `aqa_alignment` / `subject_accuracy` meaningless for other subjects in
  2026-05. **DRAFT rubrics are barred from scored runs by code** — a subject
  whose rubric is still a stub is out of scope until its rubric is real.
- **Mandatory human spot-check:** at least 3–4 full pairs per subject read by
  a human against the blind labels before the key is applied; recorded in
  RESULTS.
- **Criterion track (length-neutral) is automated [fix #7]:**
  `criteria_judgements.jsonl` is produced by the automated producer (per-item
  behaviours/red-flags judgement), not hand-authored mid-run; the producer's
  judge model and prompt are pinned in MANIFEST.json. Hand spot-checks
  validate it; they do not replace it.
- **Blinding:** per ADR-EVAL-001 — seeded key split, raw judgements committed
  BEFORE the key is applied.

## Decision rule (pre-registered) [fix #6]

Modelled on study-tutor `RUNBOOK-base-vs-finetune-tutor-eval.md` §7.2,
committed before any generation; no post-hoc re-scoring may change it.

| Outcome | Reading | Action |
|---|---|---|
| Fine-tune wins a clear majority (≥60% of decided pairs) per subject, positive Δ on socratic_stance and scaffolding, no red-flag regression | Fine-tuning generalises across subjects | Keep serving the fine-tune for all subject presets; restore the ADR "validated" rows with this run as evidence. |
| Fine-tune wins English only; base wins or ties elsewhere | Behaviour did not transfer via prompts alone | Adopt the probe protocol's cluster branch: STEM/language cluster fine-tunes; ADR amended by dated note. |
| Base wins overall (2026-05-18 repeat) | Base+prompt is the stronger tutor | **The verdict/serving contradiction [fix #5] must not recur:** within one week either (a) serving switches to the winning model for the losing presets, or (b) a dated ADR note records WHY the loser stays in service (e.g. reasoning-visibility requirement) — signed by Rich. No silent status quo. |
| leak_total > 0 for any candidate | Template regression | Flag; block any serving change until re-checked. |
| Chemistry probes fail under the correct preset | The 15/17 informal rate drops further | ADR "Chemistry" row stays revoked; chemistry-specific remediation before any multi-subject claim. |

## Outputs

`runs/YYYY-MM-DD-study-tutor-multisubject-<slug>/` — immutable, with
`MANIFEST.json` (seeds, endpoints, model ids, GGUF sha256s, prompt SHAs,
judge model, repo HEADs) and a RESULTS write-up from
`runbooks/templates/RESULTS-template.md`. Probe-track outputs additionally
stamp `preset_id` per row.
