# RESULTS — Coach held-out role suite — coach-ft-v3 — 2026-07-09

> **MORNING CHECK (read first).**
> - **Serving set restored to R-G5 tutor-default baseline: ✅ VERIFIED.** `/running` =
>   `{gemma4-tutor, tutor-coach, embed, parakeet-tdt-0.6b-v3, qwen3-tts-0.6b}` — exactly the
>   `dgx-spark/examples/llama-swap-config.gb10-live-2026-07-06-tutor-default.yaml`
>   `hooks.on_startup.preload` set. coach-ft-v3 evicted (switched back via a `study-tutor`
>   request → `tutor` matrix set). gemma4-tutor + tutor-coach are now **warm** (at session
>   start they were on-demand-cold; the audio pair + embed were already up).
> - **Keepalive timer: LEFT INACTIVE/enabled — unchanged from session start, NOT re-paused
>   by this run.** It was found already stopped (`journalctl`: `Stopped ... .timer` at
>   **2026-07-03 06:17**, ~3 days, spanning the 2026-07-06 R-G5 llama-swap restart). This
>   session therefore never needed to pause it, and the deliberate coach-ft-v3 load ran with
>   the timer already down (the [probe-list foot-gun] could not fire).
>   **⚠️ COULD NOT UN-PAUSE: passwordless sudo is unavailable on this host** (`sudo -n
>   systemctl ...` → "a password is required"); interactive sudo would have stalled the
>   unattended run, so per the "if blocked, write state and stop cleanly" rider it was left
>   as found. **ACTION FOR RICH (one command), if the standing intent is keepalive-on:**
>   `sudo systemctl start llama-swap-keepalive.timer`. Safe to leave off in the meantime: the
>   tutor set is `ttl: 0` (never idle-unloads), so it stays resident without keepalive —
>   keepalive only revives *crashed* children. The **live** allowlist is already the R-G5
>   tutor set (`gemma4-tutor`/`tutor-coach`/`embed`) — it will NOT revive coach-ft-v3.
> - **runs/ record + this RESULTS committed & pushed: see closing commit.**

**Candidate:** coach-ft-v3 = fine-tuned Gemma-4-26B-A4B MoE (coach v3 LoRA → GGUF **Q4_K_M**,
`/opt/llama-swap/models/coach-ft-v3/coach-gemma4-26b-moe-v3.Q4_K_M.gguf`), served via
llama-swap :9000, ctx 98304, `-np 1`, `--reasoning off`, temp 0.1, top_p 0.9 (the deployed
serving posture per `agentic-dataset-factory/domains/coach-agent/SERVING-coach-ft.md` +
WS4 Amendment M3 96K/-np1 pin).
**Frozen thresholds:** `docs/research/ideas/coach-heldout-suite-scope.md` §3, frozen at
commit **`e3e4caf`** (G-C1..G-C4; G-C4 confirmed zero-tolerance at N=2).
**Verifier integrity at grade time:** `python3 -m pytest tests/ -q` → **229 passed** (green
before any grading). Oracle self-check: `pytest tasks/coach-held-00{1,2}/test` → 2 + 3
passed (grader + answer-key sound).
**Assets:** `python3 harness/link_assets.py` → 88 files verified against
`harness/ASSETS.sha256`, all pinned ✓ (PO private assets, needed by the tests/ battery; the
coach bundles are authored + in-repo).
**Runner divergence (by design, scope §1):** answer sheets were produced by the Coach seat's
own harness — one fresh judgment per bundle per rep — **not** by `harness/run_po_eval.py`
(untouched). Harness used: `run_coach_heldout.py` (committed beside this file), a
direct-serving stand-in: toolless `/v1/chat/completions` against the served checkpoint under
each frozen task's `instruction.md` output contract (verdict + findings[{class,locus}], the
QAV label-trio serving-parseable subset). **No grammar passed** — the `coach-verdict.gbnf`
enforces the COACHSPLIT `decision`/`issues` schema, which is the *wrong* schema for this
suite; `instruction.md`'s contract is operative and the prompt supplies it. The DC ids were
listed but **not defined** in the prompt (faithful to the frozen `instruction.md`, which
omits definitions — adding them would edit the frozen task to make it pass).
Per-rep records (`<task>/rep-<n>/config.json`) pin: model id + lineage + quant + template +
prompt version + sampling + the per-bundle SHA-256.

This is the repo's **first `runs/` record** — it sets the convention:
`runs/<suite>/<candidate>-<date>/<task-id>/rep-<n>/{config.json, verdicts/, responses/, grade.txt}`
with the RESULTS at the run root. (Eval-harness shakedown named in ai-transition OBS-5; the
coach-ft-v4 §6.2 gate reads "frozen suites + coach-heldout" from here on.)

## Per-task × per-rep

Cell = PASS / FAIL(test). K=3, both tasks. All 6 rollouts completed with per-rep records →
the run is **VALID** (no aborted/missing reps). Grade a rep with:
`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`

| Task | Rep | G-C1 contract | G-C2 must-catch | G-C3 catch-floor | G-C4 false-block | rep verdict |
|---|---|---|---|---|---|---|
| coach-held-001-escape-kin | 1 | PASS | **FAIL** | — | — | FAIL |
| coach-held-001-escape-kin | 2 | PASS | **FAIL** | — | — | FAIL |
| coach-held-001-escape-kin | 3 | PASS | **FAIL** | — | — | FAIL |
| coach-held-002-catch-and-green | 1 | PASS | — | **FAIL** | PASS | FAIL |
| coach-held-002-catch-and-green | 2 | PASS | — | **FAIL** | PASS | FAIL |
| coach-held-002-catch-and-green | 3 | PASS | — | **FAIL** | PASS | FAIL |

Axis roll-up: **G-C1 = 6/6 PASS · G-C2 = 0/3 · G-C3 = 0/3 · G-C4 = 3/3 PASS.**

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **G-C1 — Contract shape (needs 6/6):** ✅ **MET (6/6).** Every rep emitted one parseable
  verdict file per bundle, verdict enum pinned, approve ⇒ empty findings, reject ⇒ ≥1
  admissible-DC-class finding with a non-empty locus. coach-ft-v3 honoured the `instruction.md`
  contract (did **not** fall back to its trained COACHSPLIT `decision`/`issues` schema).
- **G-C2 — Must-catch 100% (needs 3/3 on 001; 3-of-4 is a FAIL):** ❌ **NOT MET (0/3).**
  All 4 escape-kin bundles are *rejected* every rep (no false-approvals), but only **CE-01**
  (DC-08 BDD-hole) is fully caught (owning class + firing signal). The three composition-seam
  rows **CE-02 / CE-03 / CE-04 (owning DC-03)** are consistently mis-attributed to **DC-05** —
  the owning class is absent, so the must-catch test fails. Escaped-as-mis-attributed:
  CE-02, CE-03, CE-04.
- **G-C3 — Regression floor (needs 3/3 on 002):** ❌ **NOT MET (0/3).** Both catch-kin bundles
  are *rejected* every rep, but neither is caught to contract: **CK-01 (owning DC-14, narrative
  false-green)** is mis-attributed (DC-03/DC-05) though its signal fires; **CK-02 (owning DC-05,
  sys.modules stub)** gets the class **right** but names a generic locus
  (`plan_audit.variances[0].detail`) that does not fire the `sys.modules`/`conftest`/`stub`
  anchor. Either miss fails the floor.
- **G-C4 — False-block ceiling (needs 3/3 on 002; zero honest greens blocked, N=2):** ✅
  **MET (3/3).** Both honest greens — including the deliberately **ugly** HG-02 — approved with
  empty findings every rep. No false blocks.

## VERDICT: **NO-DEPLOY**

Per §3 pre-registered disposition (verbatim): *"coach-ft-v4 does not train/deploy against this
candidate — coach-ft-v3 stays the serving Coach; the failing axis is named in the RESULTS doc;
re-grade only after a model or task-instrument revision."*

**Failing axes named: G-C2 (must-catch) and G-C3 (regression floor).** coach-ft-v3 remains the
serving Coach (unchanged — this suite gates *v4*, and this run establishes the v3 baseline; it
does not re-gate v3's current serving, scope §Consumer). A strong training-loss curve does not
rescue this verdict.

**What the FAIL is — and is NOT (the v4 signal, for OBS-5 / the §6.2 loop):** the accept/reject
**judgment** is essentially perfect and stable across reps — **6/6** must-catch + catch-kin
bundles rejected, **2/2** honest greens (incl. the ugly one) approved, zero rubber-stamping,
zero blanket-rejection. The gates fail entirely on the contract's **attribution vocabulary**:
(1) **DC-class** — coach-ft-v3 has no reliable map from the defect to the frozen Phase-1 DC
taxonomy; it collapses composition-seam (DC-03) and narrative-false-green (DC-14) onto **DC-05**.
(2) **Locus specificity** — loci are frequently generic bundle-field paths
(`plan_audit.variances[0].detail`, `independent_tests.stdout_tail`) rather than the specific
in-bundle signal. This is the expected train==serve gap: coach-ft-v3 was trained on the
COACHSPLIT `decision`/`issues` grammar, not this DC-class + signal-locus contract. **v4's target
is attribution (owning DC class + specific signal locus), not the accept/reject decision.**

## Non-gating diagnostics

| Metric | Value (per rep, r1/r2/r3) | Notes |
|---|---|---|
| Escapes rejected (of 4, task-001) | 4 / 4 / 4 | direction perfect; G-C2 fails on class attribution |
| Catch-kin rejected (of 2, task-002) | 2 / 2 / 2 | direction perfect; G-C3 fails on class/locus |
| Honest greens approved (of 2: HG-01, HG-02) | 2 / 2 / 2 | the false-block lever — clean |
| Reject bundles with owning DC class present (of 6) | 2 / 2 / 1 | CE-01 (DC-08) + CK-02 (DC-05); CK-01 drifted DC-03→DC-05 at r3 |
| Reject bundles whose findings fire the in-bundle anchor (of 6) | 4 / 5 / 5 | CE-04 + CK-02 the persistent locus misses |
| Contract parse-rate | 8/8 · 8/8 · 8/8 | all fenced/inline JSON parsed first try |
| Warm judgment latency | ~0.4–1.6 s / bundle | `finish_reason=stop` throughout; no reasoning-leak, no truncation |

Per-bundle class/signal grid (own = owning class; got = model class; cls/sig = Y/N):

```
001 rep1  CE-01[own=DC-08 got=DC-08 cls=Y sig=Y]  CE-02[own=DC-03 got=DC-05 cls=N sig=N]  CE-03[own=DC-03 got=DC-05 cls=N sig=Y]  CE-04[own=DC-03 got=DC-05 cls=N sig=N]
001 rep2  CE-01[Y/Y]  CE-02[N/Y]  CE-03[N/Y]  CE-04[N/N]
001 rep3  CE-01[Y/Y]  CE-02[N/Y]  CE-03[N/Y]  CE-04[N/N]
002 rep1  CK-01[own=DC-14 got=DC-03 cls=N sig=Y]  CK-02[own=DC-05 got=DC-05 cls=Y sig=N]
002 rep2  CK-01[N/Y]  CK-02[Y/N]
002 rep3  CK-01[own=DC-14 got=DC-05 cls=N sig=Y]  CK-02[Y/N]
```

## INVALID reps

None. All 6 rollouts (2 tasks × K=3) completed with per-rep `config.json` + `verdicts/` +
`responses/` + `grade.txt`. No aborts, no missing reps, no re-runs.

## Notes / follow-ups (additive — never edit the frozen suite)

- **Root cause is attribution, not detection.** The v4 retrain (or an instrument revision that
  *reopens the frozen doc before the next freeze*, never silently) should target: (a) mapping
  defects to the Phase-1 DC taxonomy — especially DC-03 (composition seam) and DC-14 (narrative
  false-green), both currently collapsed onto DC-05; (b) naming the specific in-bundle signal
  in the locus rather than the containing bundle field.
- **Candidate broken-fixture material for the additive floor (scope §5 "every wild catch joins
  `tests/broken_fixtures/`"):** the *right-verdict / wrong-class* pattern (reject + DC-05 where
  DC-03/DC-14 is owed) is a distinct failure mode from the existing `generic-locus` and
  `approves-the-seam` fixtures — worth a `mislabels-the-class` broken fixture so a future
  candidate that regresses to it is caught by the integrity battery, not only by a live grade.
- **Methodology note for the convention:** the prompt deliberately did not define the DC
  classes (instruction.md omits them). If a future decision is that the served Coach *should*
  be handed the taxonomy at judgment time, that is a **task-instrument revision** and must
  reopen `coach-heldout-suite-scope.md` before re-freezing — it is not a runner knob to twiddle
  between candidates.

[probe-list foot-gun]: the keepalive allowlist must equal the live preload set; loading an
on-demand model with the timer live would let the 5-min probe switch sets and evict it
mid-run. Here the timer was already down, so it was inert — but the discipline (pause before
load, restore after) is why the load step was gated on the timer state.
