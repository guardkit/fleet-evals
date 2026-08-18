# RESULTS — study-tutor multi-subject eval, run 2026-08-13 (PROTOCOL v2)

**Venue:** `venues/study-tutor-multisubject` · **Protocol:** REGISTERED v1 2026-08-07,
v2 judging amendment 2026-08-13 (Rich: "amend: subscription + local judges") — both
BEFORE any generation. **Question:** does one English fine-tune, differentiated only by
per-subject system prompts, tutor Socratically across GCSE subjects — and does it beat
the base model at it?

## The registered verdict (the two judges' agreement set)

| | items |
|---|---|
| **base wins (both judges agree)** | **106** |
| fine-tune wins (both agree) | 7 |
| tie (both agree) | 1 |
| judges split | 22 |
| **per-item agreement** | **114/136 = 84%** |

**The base model won the agreement set in ALL EIGHT subjects.** Per-judge tallies:
Judge A (Claude) base 114 / ft 19 / tie 3; Judge B (Qwen) base 120 / ft 13 / tie 3.

Judge A dimension means (1–5): base leads every dimension; the decisive gaps are
**aqa_alignment 4.12 vs 2.91** and **scaffolding 4.50 vs 3.19**; subject_accuracy
4.78 vs 4.46; the fine-tune's 2026-05-18 socratic-stance advantage is GONE
(4.21 base vs 4.09 ft). Full tables: `results-table.md`; per-item: `judgements.jsonl`
(A), `judgements-local-final.jsonl` (B); blinding artefacts + key in this dir.

## What this replicates

The 2026-05-18 English-only eval (base 15–1) — now at 8.5× the sample (136 items),
across 8 subjects, two independent blind judges from different model families,
position-randomised, under a pre-registered decision rule. The direction is the same
and stronger.

## Deviations from the registered protocol (all pre-verdict, all worded)

1. **Judge B model:** gpt-oss-120b's weights were found ABSENT from the host (config
   ghost); substituted `workhorse` (Qwen3.6-35B — still non-Gemma) on Rich's word
   ("sure try the qwen3.6 workhorse"), recorded before any judgement existed.
2. **Judge A tier:** run on Sonnet 5 subagents during the 2026-08-13 Anthropic
   Fable/Mythos elevated-error incident. The protocol wording ("a fresh-context Claude
   subagent") pins no tier.
3. **MFL rubric correction + re-judge:** the drafted French/Spanish rubrics wrongly
   claimed four skill-mapped AOs; the AO fact-check (against AQA's own spec pages)
   caught it MID-JUDGING — both MFL batches were stopped, rubrics corrected to the real
   structure (AO1 spoken 35% / AO2 written 45% / AO3 grammar+vocab 20%, across four
   equally weighted skill papers), and French+Spanish re-judged from scratch on BOTH
   judges. No wrong-rubric judgement ever entered a results file.
4. **Science AO3 truncation:** the science rubrics initially carried a truncated AO3
   summary (missing the "make judgements" and "develop/improve experimental
   procedures" strands); judged batches used it. Assessed immaterial (the six scored
   dimensions are unchanged; the line is framing); corrected for future runs.
5. **Qwen thinking-channel fix:** Judge B's first runs starved the verdict channel
   (measured: 11k chars of reasoning, zero verdict); fixed with
   `chat_template_kwargs: {enable_thinking: false}` — a harness fix, not a judging
   change.

## Honest scope limits

- **The multi-turn track did NOT run** (scenarios exist English-only); single-turn only.
- Golden sets are the 2026-08-13 adversarially-reviewed seeds (english 24, others 16) —
  the protocol's n≥24/subject growth target stands for future runs.
- Subject rubrics beyond English are first-generation (base-6 dimensions + real AO
  framing); no subject-expert sign-off yet.
- **PENDING: Rich's mandatory human spot-check** (`SPOT-CHECK-for-rich.md`, 4 pairs,
  identities revealed). The verdict is not final until his word.

## What it means (input to ruling-queue item 3 — the serving ruling, Rich's alone)

If the spot-check holds: the evidence says **serve the stock base model** under the
per-subject prompts. Knock-on effects, stated not decided: no fine-tune weights to
host ⇒ the ADR-031 D4.2 licence conflict becomes moot FOR SERVING; the Lane 7 bake-off
gains a measured bar (a refreshed fine-tune must beat base on THIS harness); the
fine-tune's training recipe (short conversational turns) is the identified weakness —
aqa_alignment and scaffolding are where it loses.

---

## Dated addendum — 2026-08-13, construct scope (Rich's challenge, accepted)

Rich's question on reading the verdict: *"in real-world usage it's absolutely brilliant
at tutoring — the way it holds a conversation and elicits interaction from the student —
are the evals checking the correct behaviour?"* The honest answer: **this run measures
single-turn reply quality, NOT conversational tutoring.** The construct mismatch
systematically favours the base: the fine-tune was trained for short conversational
turns by design (2026-05-18 RESULTS, verbatim), and the dimensions it lost on
(aqa_alignment, scaffolding) reward single-reply comprehensiveness. The two instruments
that historically moderated exactly this bias — the multi-turn track (2026-05-18:
2–0–1, nearly level, vs 15–1 single-turn) and the length-neutral criterion track — did
not run here. The eval also judged the BARE model; production is the Player–Coach loop.
Rich's attended real-session receipts are evidence under law 8, not anecdote.

**Re-scoped claim:** the base writes stronger standalone replies under subject prompts,
and the fine-tune slips more on facts. **The serving ruling (queue item 3) must NOT be
made on this run alone** — it waits for the multi-turn + criterion tracks and an
engagement/elicitation dimension (protocol v3 extension, Rich's word same day: "yes
please proceed with your recommendations").

---

## v3 extension results — 2026-08-13, same day: the three-instrument read

Rich's construct challenge was tested, not deflected. All three instruments now in:

| Instrument | What it measures | Verdict |
|---|---|---|
| Pairwise single-turn (2 judges) | best standalone reply | base 106 / ft 7 / tie 1 |
| Criterion track (length-neutral, response scored alone) | pre-registered behaviours + red flags | base 73.9% vs ft 67.0%; flags 4 vs 12 — a MODEST gap |
| **Multi-turn session (7 dims incl. engagement_elicitation)** | whole-conversation tutoring | **agreement set: base 20 / ft 0** (20/24 agreement) |

**The engagement dimension itself — built for the fine-tune's claimed strength —
scores base HIGHER on both judges** (Claude 4.17 vs 3.71; Qwen 4.92 vs 3.50).
The pairwise blowout was inflated by the comparison format (the criterion track
proves the underlying behaviour gap is ~7 points, not 15:1), but the DIRECTION
survives every instrument, including the conversational one.

**Honest limits that remain:** (1) scripted students cannot REWARD elicitation —
the fixed turns mean judges score eliciting BEHAVIOUR, not its effect on a real
student; (2) the bare model was judged, not the production Player–Coach loop;
(3) Rich's positive real-session experience is evidence about THE SYSTEM with
the fine-tune in it — and, crucially, **the base model has never been tried in
that loop**. His experience and these results are compatible: the system may be
great AND the base might make it better.

**The named next evidence step (recommendation, Rich's to order):** a real-world
attended trial — flip the serving seat to `gemma4-base` for a handful of Rich's
own sessions in the real loop (one env/config change; trivially reversible) and
judge by feel plus the phone receipts. That is the ONE instrument nobody has
run, it is the construct closest to S0, and it converts the serving ruling from
"trust the harness" into "I felt the difference myself."

**Mid-run defects caught and voided (the receipts discipline working):** Judge
B's first session run saw EMPTY transcripts (renderer assumed the wrong turn
shape) and honestly tied all 24 with degenerate scores — caught by the
all-tie anomaly + its own rationales, voided
(`multiturn_raw-local.VOID-empty-render.jsonl` kept), renderer fixed, re-run;
its second run died at item 20 on LaTeX-backslash JSON (escape repair +
progressive writes added, resumed, completed). Scenario review also caught and
fixed one internal inconsistency (history Putsch/Chancellor) BEFORE generation;
the Elizabethan essay-phrasing taste-flag is recorded here for Rich's eyes.

---

**SPOT-CHECK COMPLETE — Rich, 2026-08-14 ("I've read them — spot-check ok").** The
protocol's mandatory human backstop is discharged; the verdicts above are FINAL for
this run. Next evidence step (Rich's word, same day): the attended base-in-the-loop
trial — prepared in study-tutor `RUNBOOK-base-in-loop-trial.md`.
