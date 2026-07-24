# RESULTS — QAV held-out deployment gate — qav-ft-v4 — 2026-07-24 — **THE STOP-RULE FIRES**

**Candidate:** `qav-ft-v4` = the Option-B ratified corpus (559 rows: batch-A api_test spines,
the pure-vacancy cohort 3→26, DC-05 boundary axis 4→34/16 — adf `v4-corpus-2026-07-24.md`
@aa2e51e, engine @40ace76+ced9a34) → train 345/345 (eval_loss 0.285→0.223→0.236 on the
class-complete 93-row eval) → Phase-5.2 gate **6/6 bare JSON, 5/6 verdicts — both historic
thin-prompt rows REJECTED for the first time in four tunes**, held-out DC-14+DC-12 classes
correct → GGUF Q4_K_M sha `9ce387b7c77ccae551d8efc3…` (16,796,000,992 B, the fourth
byte-identical size) → `qav-ft-v4` on llama-swap. Frozen thresholds @`2165802`; runner sha
`4d1d3292…`; 6/6 rep-runs first-attempt valid; v3/v2/v1/stock columns banked.

## VERDICT: **NO-DEPLOY — and the claim's stop-rule fires: THE TUNING LOOP PARKS.**

No v5 on this corpus. The failure is now precisely characterized across four tunes and it is
not a data-volume problem.

## The four-tune arc (what four cycles actually established)

| Layer | v1 | v2 | v3 | v4 |
|---|---|---|---|---|
| Serving contract (bare JSON, no truncation) | ✅ 24/24 | ✅ | ✅ | ✅ |
| Verdict (reject the bad, approve the good) | ✅ 21/24* | ✅ 21/21 | ✅ | ✅ 21/21 |
| Evidence-reading (anchors: locus names the in-bundle signal) | ~7/15 | 9/15 | 9/15 | **14/15 — essentially solved** |
| Owning-class attribution | 2/15 | 0/15 | 1/15 | **0/15** |

\* v1 verdict layer: 12/12 GN + RC-01 ×3 rejected, 9/9 greens (same as all successors).

**The attractor migration — the finding that parks the loop:** each corpus lever moved the
class-guess to the newest well-supported class instead of installing the exam's class map.
v2 (DC-12 grew 0→69): everything wiring-shaped read DC-12. v3 (contrast pairs): the attractor
broke into wobble. v4 (DC-05 grew 4→34 with boundary controls; vacancy 3→26): **GN-1/2/3 now
read DC-05 deterministically, GN-4 stays DC-12, and RC-01 flipped to DC-03** — the vacancy
class itself. The model reads evidence correctly (its loci fire the anchors; the gate catches
rows three prior tunes missed) and then names the class by corpus-support gradient, not by the
taxonomy's semantics. The exam's owning-class ground truth encodes *judgment* distinctions
(which null the task owns; narrative-vs-plan-vs-tamper) that synthetic same-spine contrast at
this scale demonstrably does not pin down.

## What v4 demonstrably added (non-gating)

The Phase-5.2 gate's first-ever catches of `43c8de…`/`13f964…` (0-for-3 across every prior
tune's gate) + correct held-out DC-14/DC-12 gate classes + the best anchor showing (14/15,
GN-2 rep-2 the only unfired leg) + zero regressions anywhere in the verdict/contract layers.

## Post-park options (NAMED for Rich, deliberately not claimed)

1. **Organic growth, then revisit** — the standing default: the factory's real future defects
   accumulate as record-native rows with human-adjudicated classes; the loop un-parks when the
   class-boundary data is real rather than synthetic.
2. **A serving-side lever, not a corpus lever:** put the DC taxonomy definitions in the served
   system prompt so class-naming becomes reference-lookup instead of weight-memory. The sealed
   exam pins the system-line sha, so testing this requires a fleet-evals decision (a new frozen
   task or a re-freeze) — a Rich call, not a lane act.
3. **The product question:** the verdict + locus layers are deploy-grade by every measure this
   suite runs; only the class label fails. Whether the seat's deploy bar should require the
   class name (vs the OFFICE deriving/reviewing it) is a product judgment about the QAV seat's
   contract — Rich's, not the loop's.

## Integrity + serving receipts

Runner snapshot sha == HEAD; single-slot law honored (warm→verified→zero refusals); grades =
separate unmasked pytest exits per rep-task; the only writes are `runs/qav-ft-v4-…/` + this
doc. Config backup `config.yaml.bak-20260724-*-pre-qav-ft-v4`; `qav_exam` now carries all
four candidates + stock; rollback = the dated .baks. All four tuned candidates stay parked on
llama-swap as probe entries (R3-02: probe, not adoption — moot under NO-DEPLOY + park).
