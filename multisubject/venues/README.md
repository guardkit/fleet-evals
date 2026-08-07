# venues/ — one directory per ruled evaluation venue

A **venue** is a pre-registered evaluation context: what is being compared,
on what data, under what decision rule. A venue directory contains:

| File | Role | Required to run? |
|---|---|---|
| `PROTOCOL.md` | The pre-registration: hypothesis, decision rule, seeds, judges, n. Committed BEFORE any generation — the harness **refuses to start a run without it, and refuses while its Status is DRAFT** (`harness/common.py::require_protocol`; the DRAFT → REGISTERED flip is Rich's gate tap). Template: `runbooks/templates/PROTOCOL-template.md`. | YES (REGISTERED) |
| `candidates.yaml` | The n-way candidate list (name / model / endpoint / gguf_sha256 + provenance status). | YES |
| `golden/*.jsonl` | Golden-set items (`id`, `category`, `subject`, `prompt`, `expected_behaviours`, `red_flags`). | per track |
| `golden/multiturn/scenarios.jsonl` | Scripted multi-turn sessions. | per track |
| `prompts/` | SHA-pinned system-prompt files + `PROMPTS-PROVENANCE.md` (source path, line range, sha256 per file). | for parity-pinned runs |
| `probes-17/probes.jsonl` | Informal probe protocol as data (multisubject venue). | probe track |

## Current venues

- **`study-tutor-multisubject/`** — the seed venue. Has the 16-item English
  golden set + 3 multi-turn scenarios lifted from study-tutor; the eight
  subject system prompts extracted byte-verbatim from the Open WebUI runbook
  heredocs (+ english.txt from `roles/tutor/prompts/player.md`) with sha256
  provenance (`prompts/PROMPTS-PROVENANCE.md`); `probes-17/probes.jsonl` —
  the 17-prompt protocol as data, with C1/C2 carrying the pinned defect
  annotation (the 2026-05-era transcript answered both Chemistry probes
  under the BIOLOGY preset — Chemistry is UNBACKED, re-run required under
  the real `gcse-chemistry` preset); `candidates.yaml` for the
  base-vs-finetune pair (provenance honestly UNVERIFIED); and `PROTOCOL.md`
  encoding all seven 2026-05-18 required fixes — **Status DRAFT, pending
  Rich's gate tap, so no run can start.** Still missing before
  registration: per-subject golden sets at the 24+ bar, real per-subject
  rubrics, the automated criteria producer.
- **`study-tutor-bakeoff/`** — Lane 7 n-way skeleton (refreshed Gemma 4
  fine-tune vs Qwen 3.6 fine-tune vs old fine-tune vs base). DRAFT
  PROTOCOL.md with TBD blanks + `candidates.yaml` whose placeholder seats
  are labeled honestly (two candidates NOT TRAINED, base NOT ON HOST, old
  fine-tune provenance UNVERIFIED). Build prerequisite: n-way `pairwise_api`.
