# RESULTS — R-b code-review seat (P2 / V-01) — S-4 calibration measurement — 2026-07-13

**What this is:** the S-4 calibration MEASUREMENT for the R-b review seat — numbers only.
The **BAR is Rich's** (catch-rate floor + over-flag ceiling), set outside this workflow; the
seat stays advisory-only until his bar is met. Nothing here promotes anything to blocking.

**Gold set:** the forge **FEAT-SPL-002 / FEAT-DD4F post-merge review** (2026-07-06), merge range
`d13d88f..1fcb72c` — the "16 serious findings CONFIRMED, 0/32 refutations" record cited at
`guardkit/guardkit/qa/formats/review_findings.py:5`. Source of record:
`forge/docs/reviews/feat-spl-002-post-merge-review-2026-07-06.md`. Reconstructed to `gold/gold-set.json`
(16 serious + 9 low; see reconstruction note there).

**Pipeline under test:** guardkit S1 `diff_ingest` → S2 review contract (`review_seat._REVIEW_SYSTEM`,
the 4-dimension F14 discipline) → S3 `review_seat.emit_review_findings`. Local seat only
(`qwen36-workhorse` @ llama-swap :9000), single-slot-guarded (`/running` checked free before every
call; no factory drive was mid-generation).

---

## The two headline numbers (measured, Run B — the seat's fair-config capability)

| Metric | Value | Against |
|---|---|---|
| **Catch-rate** | **3/16 (19%)** unambiguous · **4/16 (25%)** incl. one substantive partial | the 16 serious gold findings |
| **Over-flag rate** | **14/19 (74%)** of emitted findings map to no gold finding; of those **3/19 (16%)** flag code the gold review verified *correct* | the 19 findings the seat emitted |

**Caught (serious):** G01 serve-boot wrong-kwargs (the CRITICAL) · G07 rearm log-only stub ·
G10 boot-sweep FAILs RUNNING (RT-08) · G11 escalation phase-1 CAS-guard race (partial — got the
CAS half, missed the request-id-persistence half). **Also caught 1 LOW:** L02 private `_store._connection` access.

## The load-bearing caveat — reachability (read this before reading the 19%)

Of the 16 serious gold findings, **~11 are structurally out of reach for a diff-only seat**:
- **6 need cross-repo contract knowledge the diff does not carry** — G04/G08/G14/G16 (and part of
  G12/G15) require the `nats-core` payload schemas (`ApprovalRequestPayload`, `NotificationPayload`,
  `BuildPausedPayload`) and jarvis's reply/validation behaviour. The seat only ever sees the forge diff.
- **5 are whole-system "absence" findings** — G02/G03/G05/G09/G13 require repo-wide *"is X called
  anywhere?"* grep reasoning (nothing subscribes the consumer; dispatch is a stub; no GitRunner impl;
  no escalation driver; defer wired nowhere), which a diff cannot answer.

Only **~5 gold findings are diff-local-reachable** (G01, G06, G07, G10, G11). **On that reachable
subset the seat caught 4/5 (80%)** — it missed only G06 and, worse, *inverted* it (it flagged the
*correct* transition table as suspicious, G1-F1). So the honest reading is: **the seat is competent
on defects it can see; the 19% headline is dominated by a gold set built from cross-repo/whole-system
findings a diff-scoped seat cannot reach.** Whether to hold the seat to the raw 16 or to the reachable
subset is a framing choice for Rich's bar.

## Run A — the pipeline AS SHIPPED is inoperable on a real diff (a fixable config finding)

`run_advisory_review` with its built defaults (`_default_seat_call` → qwen36 **reasoning ON**,
`max_tokens=4096`) emitted **0 findings**: `error = "seat output contains no JSON object"`. Cause
(reproduced deterministically): on a ~40k-token diff the seat's reasoning consumes the entire 4096-token
budget (`finish_reason=length`), so `content` is empty and there is no JSON to parse. **This is a
pipeline-config finding, not a seat-quality one** — the fix is in `review_seat._default_seat_call`:
disable thinking (`chat_template_kwargs.enable_thinking=false`, verified working) and/or raise
`max_tokens`. Run B applied exactly that fair config and got usable output. **Flagged for the S-3/S-5
owner; out of scope for this measurement stage** (recorded, not silently patched).

---

## Method notes (honesty-to-state)

- **Scoping:** the gold review read the whole 219-file merge with 5 agents that had cross-repo grep.
  This single-seat run was scoped to the **`src/forge/` reviewable code surface (17 files, 154,700
  rendered chars)** — all 16 serious gold findings live in these files. Task-`.md` and test files were
  excluded as non-code noise the seat could not use (recorded in `gold/diff-manifest.json`). One
  consequence: gold LOW **L09** lives in a test file, so it is outside the seat's surface; and two Run B
  "no tests" notes (G3-F4, G4-F4) are scoping artifacts — tests DO exist (gold confirms 142 planning
  tests pass), the seat just wasn't shown them.
- **Run B grouping:** the 17 files were fed in 4 subsystem groups (boot-wiring / checkpoint-escalation /
  store-migration / wire-handoff-config) sized so nothing truncated and cross-file finding pairs
  (e.g. serve.py↔_serve_planning.py signatures) stayed together. Findings were unioned.
- **F14 honesty rules held:** all 4 emitted records are schema-valid; **`confirmed` = 0** across all —
  the reading-only seat has no execution channel, so under LPA-15 it can never *earn* a confirmed
  verdict (every finding is `refuted`, the not-yet-confirmed bucket). Critical/high findings the seat
  did not defend with ≥2 refuters were auto-downgraded to medium (never dropped), per LPA-14.
- **Single-slot law:** `/running` was probed free before every seat call; no collision with a factory drive.
- **The seat is a reference signal, not the seat of record** for the bar — these are inputs to Rich's
  S-4 judgement, not a pass/fail this stage renders.

## Artifacts in this directory

| Path | What |
|---|---|
| `gold/gold-set.json` | the reconstructed gold set (16 serious + 9 low) with per-finding match keys |
| `gold/diff-manifest.json` | the exact src surface fed to the seat (17 files, chars, scoping note) |
| `seat-output/runA-asshipped-outcome.json` | Run A outcome (0 findings, the parse-fail error) |
| `seat-output/runB-<group>-raw.txt` | each group's raw seat completion |
| `seat-output/runB-<group>-f14.json` | each group's schema-valid emitted F14 record |
| `seat-output/runB-union.json`, `runB-meta.json` | the 19-finding union + per-group timing/size |
| `scoring/scoring-sheet.json` | per-finding CATCH/OVER-FLAG judgement for all 19 |
| `harness.py` | the measurement harness (S1→S3 driver; both runs, reproducible) |

## For Rich — the two numbers your bar sits above

- **Catch-rate the seat cleared here:** **19% (3/16)** on the raw serious gold set — **or 80% (4/5)**
  on the diff-local-reachable subset. The gap between those two is entirely the ~11 cross-repo /
  whole-system findings a diff-only seat structurally cannot reach.
- **Over-flag the seat produced here:** **74%** of its emissions were non-gold, **16%** were
  affirmatively wrong (flagged verified-correct code — the coach-0.00-shaped risk, present but small).
- **Before any of this is trusted:** Run A shows the shipped pipeline emits *nothing* on a real diff
  until the seat-call config is fixed (thinking-off / more tokens). That fix precedes a meaningful bar.
