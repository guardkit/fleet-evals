> Inherited VERBATIM (below this note) from study-tutor docs/runbooks/templates/RESULTS-template.md at HEAD 27bb0b5b760a393c7470b0aaae30bcdccbe1a843 (2026-08-07). Copy per run to runs/<run>/RESULTS-<slug>-<date>.md and fill every section.

# RESULTS: <runbook-slug> (<run-descriptor>)

> **How to use this template.** Copy this file to
> `docs/runbooks/RESULTS-<slug>-<YYYY-MM-DD>[-<descriptor>].md` (e.g.
> `RESULTS-study-tutor-nats-fleet-demo-2026-05-15-dress-rehearsal.md`)
> per execution of the matching runbook. Fill in every section. Mirrors
> `~/Projects/appmilla_github/jarvis/docs/runbooks/RESULTS-jarvis-architect-align-dddsw-demo-2026-05-08-followup-post-W2.md`
> exactly so cross-runbook comparisons are trivial.

**Date:** YYYY-MM-DD (morning | afternoon | evening — and a one-clause
run descriptor like "second walkthrough of the day" or "post-Bug-#7 fix")
**Operator:** <human name | "Claude Code (non-interactive, stdin-piped REPL driver)">
**Machine:** <e.g. GB10 (`promaxgb10-41b1`) — single-host all-local>
**Runbook executed:** [`<filename>.md`](<filename>.md) — version/HEAD if
relevant

## Participating-repo HEADs

Capture the exact `git rev-parse HEAD` of every repo whose code was on
the path during this run. Reproducibility requires all of them.

| Repo | HEAD | Last-commit summary |
|---|---|---|
| `study-tutor` | `<sha>` | <one-line summary of HEAD commit> |
| `jarvis` | `<sha>` | <one-line summary> |
| `specialist-agent` | `<sha>` | <one-line summary> |
| `nats-core` | `<sha>` | <one-line summary> |
| `fleet-gateway` (if on path) | `<sha>` | <one-line summary> |

Image tags (if applicable):

- `study-tutor:<tag>` — built <YYYY-MM-DD HH:MM TZ>
- `specialist-agent:<tag>` — built <YYYY-MM-DD HH:MM TZ>
- `<other>:<tag>` — built <YYYY-MM-DD HH:MM TZ>

**Companion files (prior runs of the same runbook, if any):**

- [`RESULTS-<slug>-<earlier-date>.md`](RESULTS-<slug>-<earlier-date>.md) —
  one-line characterisation (e.g. "morning run, blocked by Bug #N")

---

## Outcome

✅ GREEN | ⏸ STILL BLOCKED, but at a different layer | ❌ RED

One-paragraph summary of what changed vs the prior run (or what's new vs
the runbook's expected outcome). Reference the most-load-bearing piece of
evidence (the trace, the wire-tap envelope, the chat log).

## Demo blocking?

YES | NO. If YES, name the bug(s) and the next walkthrough's prerequisite.
If NO, name any non-blocking hygiene findings deferred to a follow-up.

---

## What's new vs <prior run>

If this is a follow-up to an earlier run, summarise the deltas in a
two-column table. If this is a first run, replace this section with
"First execution — no prior comparison."

| Topic | Prior run (`<sha>`, <descriptor>) | This run (`<sha>`, <descriptor>) |
|---|---|---|
| <e.g. Resolver lookup of `tutor_start_session`> | <prior outcome> | <this run outcome> |
| <e.g. Wire-tap envelopes on `agents.command.>`> | <count + correlation_ids> | <count + correlation_ids> |
| <e.g. Trace `outcome_type`> | <value> | <value> |
| <e.g. Root cause> | <prior characterisation> | <new characterisation> |

One-sentence editorial: did the prior fix do what it claimed? What layer
did we move to?

---

## Phase × Gate × Outcome × Evidence summary

Mirror the runbook's Phase × Gate table verbatim. For each row, fill in
the actual outcome (✅ pass / ⚠️ partial / ❌ fail / ⏭ skipped / ⏳
pending) and the evidence pointer (file path under `evidence/`, command
output, log line, or correlation_id).

| Phase | Gate | Outcome | Evidence |
|---|---|---|---|
| 0.1 | <gate description from runbook> | ✅ \| ⚠️ \| ❌ \| ⏭ \| ⏳ | <pointer> |
| 0.2 | … | … | … |
| 0.3 | … | … | … |
| 0.4 | … | … | … |
| 0.5 | … | … | … |
| 0.6 | … | … | … |
| 1.1 | … | … | … |
| 1.2 | … | … | … |
| 1.3 | … | … | … |
| 1.4 | … | … | … |
| 1.5 | … | … | … |
| 2.1 | … | … | … |
| 2.2 | … | … | … |
| 3 | Dispatch fires + result rendered | … | <chat log + traces> |
| 4.1 | Wire tap on `agents.command.>` | … | `evidence/<run>/command.log` |
| 4.2 | Wire tap on `agents.result.>` | … | `evidence/<run>/result.log` |
| 4.3 | Result captured | … | `evidence/<run>/<corr>.json` |
| 7.1 | Chat transcript | … | `~/.jarvis/transcripts/<corr>.txt` |
| 7.2 | Routing-history offload | … | `~/.jarvis/traces/<corr>.json` |
| 7.3 | command_history.md entry | … | — |
| 7.4 | RESULTS file | ✅ THIS FILE | — |
| 8 | Demo close | … | — |

---

## Bug catalogue

If this run surfaced bugs, document each one in priority order using the
canonical four-field shape (symptom / cause / fix / where-it-must-live).
Mirror the worked examples in the runbook's "Bug catalogue (template)"
section. Delete this section if the run was clean.

### Bug #N — <one-line title> (DEMO BLOCKER | NON-BLOCKING)

**Symptom:** What the operator saw. Include the literal log line, error
text, or wire envelope shape.

**Cause:** The actual mechanism. Cite the line of code or the contract.

**Confirmed by:** Concrete evidence — trace ID, wire-tap log file, direct
`nats request` diagnostic with timing. Reference the file under
`evidence/<run>/` that contains the proof.

**Fix options (pick one):**

- **(A)** Smallest blast-radius fix.
- **(B)** Alternative if (A) is constrained.
- **(C)** Cleanest topology fix if breakage is at the contract layer.

**Recommend (A | B | C)** — repository scope: `<which-repo>`.

**Important note (if relevant):** Whether this bug masks (or is masked
by) another bug, or whether it interacts with a known-issue.

---

(repeat the Bug #N block for each bug)

---

## What's working — narrative

Three to six bullets of what unambiguously did work end-to-end during
this run. The point is to make the partial-success layer visible:
infrastructure, catalogue propagation, supervisor reasoning, transport,
etc. This is also what tells the post-talk write-up where the demo
narrative is sound even if the dispatch path is blocked.

- **Infrastructure layer:** <what's green — NATS, JetStream, llama-swap,
  compose, registry, heartbeat, etc.>
- **Catalogue propagation:** <which capabilities surfaced; live KV
  watch behaviour>
- **Wire transport:** <what envelopes flowed and where>
- **Supervisor reasoning:** <what the LLM selected and how it framed the
  failure or success>
- **Capture / hygiene:** <traces, transcripts, log capture working as
  designed>
- **<other>**

---

## Next steps with concrete fix-and-rerun list

Numbered, in priority order. Each item should be actionable — a specific
file to patch, a specific env var to set, a specific test to run, plus
the expected re-verification step. Mirror the jarvis post-W2 results
file's "Next steps before <date>" section.

1. **Fix Bug #N (`<title>`)** — <one-sentence approach>. <where to apply
   the fix; which test to add; how to verify>.
2. **Fix Bug #N+1 (`<title>`)** — …
3. **<environmental fix or hygiene flag>** — …
4. **Re-run this runbook end-to-end.** Should green-light Phases <X-Y>.
   Save the resulting `<ResultPayload>` JSON to
   `evidence/<run>/<correlation_id>.json` per §4.3 — that's the artefact
   for the slide.
5. **Dress rehearsal** the day before (<YYYY-MM-DD>). Warm the model
   with one throwaway call before going on stage.

## Hygiene flags (non-blocking but worth addressing)

Optional. List anything noticed during the run that didn't block but
should be addressed before the next walkthrough or before the demo.

- **<flag 1>** — <description + recommended fix>
- **<flag 2>** — <description + recommended fix>

## Evidence index

All under [`docs/runbooks/evidence/<run>/`](evidence/<run>/):

- `chat-<date>.log` — <description>
- `wire-command-<date>.log` — <description; correlation_ids>
- `wire-result-<date>.log` — <description; correlation_ids>
- `trace-<tool>-<corr>.json` — <description>
- `<corr>.json` — captured ResultPayload (the slide artefact, if green)
