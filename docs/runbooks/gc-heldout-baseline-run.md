# Runbook — gc-heldout base-model baseline run (operator, GB10)

**Consumer:** the operator (Rich) executing the FIRST baseline measurement once the GB10
frees — the deferred-GPU half of flywheel ladder Step 9. This run must complete (and its
family record land) **before Rich freezes `docs/research/ideas/gc-heldout-suite-scope.md`,
which must happen before the suite's first candidate grade, which lands before the
qav-ft-v1 grade** (D-OBS-3).
**Status:** READY — not executed (build session 2026-07-10 was NO-GPU by design; a build
owned the box).
**Wall-clock estimate:** 150 generations (2 tasks × 25 rows × 3 reps) at temp 0.1 —
a lunch-break run on the GB10, per the ASSUM-001 sizing.

---

## 0. Preconditions (all must hold)

1. GB10 free (no AutoBuild/training run owns the box; check with the board session).
2. fleet-evals synced at/after the FEAT-EVAL-GC build commit; battery green ON THE GB10:
   `python3 -m pytest tests/ -q` → all pass. This includes the sandbox self-test — if
   `unshare -rn` is blocked on the GB10 kernel, the battery FAILS LOUDLY here and grading
   is blocked (G-G4): stop and report, do not work around.
3. **Pick the family from the first candidate, not from convenience:** the baseline must
   be the BASE model of qav-ft-v1's base+quant family, quantized AS THE CANDIDATE WILL
   SERVE. The coach-ft-v3 lesson is binding: candidate Q4_K_M vs base Q4_K_XL absorbs the
   margin in quant noise — that comparison is structurally refused by the harness.
   Record: `BASE_FAMILY` (e.g. `gemma-4-26b-moe`) and `QUANT` (e.g. `Q4_K_M`).

## 1. Serve the base model (llama-swap :9000)

- Serving truth: `dgx-spark/examples/llama-swap-config.gb10-live-2026-07-06-tutor-default.yaml`
  (sibling repo). Add/confirm a handle for the BASE model GGUF at `${QUANT}`; note the
  handle as `BASE_HANDLE`.
- **Keepalive/probe-list foot-gun (coach-ft-v3 morning-check rider):** the tutor-set
  keepalive probe list can evict an on-demand model mid-run. Confirm the keepalive timer
  state BEFORE the run: `systemctl status llama-swap-keepalive.timer` (inactive-as-found
  is fine for tutor set ttl:0). If you pause it, note it in the run record.
- **GB10 sudo rider (memory: unattended sessions cannot do this):** re-enabling the
  keepalive after the run needs interactive sudo:
  `sudo systemctl start llama-swap-keepalive.timer`
- Warm the handle once (any small completion) so rep 1 doesn't eat the load time.

## 2. Produce the answer sheets (K = 3 reps × 2 tasks)

```bash
cd ~/Projects/appmilla_github/fleet-evals
DATE=$(date +%F)
OUT=runs/gc-heldout/base-${BASE_FAMILY}-${QUANT}-baseline-${DATE}
for REP in 1 2 3; do
  for TASK in gc-held-001-humaneval gc-held-002-mbpp; do
    python3 harness/run_gc_heldout.py \
      --task-dir tasks/$TASK \
      --out $OUT/$TASK/rep-$REP \
      --model $BASE_HANDLE --rep $REP \
      --base-family $BASE_FAMILY --quant $QUANT \
      --lineage "base model (no adapter) — baseline measurement" \
      --temperature 0.1 --top-p 0.9
  done
done
```

Notes: the runner refuses loudly if pins are broken, the sandbox is unavailable, or the
out-dir holds another suite's records. A transport abort writes `ABORTED.json` and exits —
**re-run that rep in place under the same flags** (INVALID-not-failed; a mid-run eviction
is the documented GB10 reality). Sampling is the base-baseline posture (ASSUM-006).

## 3. Grade the reps and record solved counts

The floor test will (correctly) report "no frozen baseline for family ..." until step 4 —
run the contract/pins/sandbox gates and count solved rows per rep:

```bash
for REP in 1 2 3; do
  for TASK in gc-held-001-humaneval gc-held-002-mbpp; do
    PO_EVAL_OUTPUT_DIR=$PWD/$OUT/$TASK/rep-$REP \
      python3 -m pytest tasks/$TASK/test -q -k "not regression_floor"
    PO_EVAL_OUTPUT_DIR=$PWD/$OUT/$TASK/rep-$REP python3 - << EOF
from pathlib import Path
import os
from harness import gc_gates
task = Path("tasks/$TASK"); out = Path(os.environ["PO_EVAL_OUTPUT_DIR"])
grades = gc_gates.grade_rows(task, out)
print("$TASK rep $REP solved:", gc_gates.solved_count(grades), "/", len(grades))
EOF
  done
done
```

All `-k "not regression_floor"` gates must PASS for every rep (G-G1/G-G4). Record the six
solved counts.

## 4. Add the family record ADDITIVELY to `harness/gc_baselines.json`

For each task: `rep_solved = [r1, r2, r3]`, `baseline_solved = median` (the PROPOSED
aggregation rule — scope doc §3):

```json
"${BASE_FAMILY}/${QUANT}": {
  "measured": "<date>, GB10, ${BASE_HANDLE}, temp 0.1 / top_p 0.9",
  "run_record": "runs/gc-heldout/base-${BASE_FAMILY}-${QUANT}-baseline-<date>/",
  "benchmarks": {
    "gc-held-001-humaneval": { "baseline_solved": <median>, "rep_solved": [r1, r2, r3] },
    "gc-held-002-mbpp":      { "baseline_solved": <median>, "rep_solved": [r1, r2, r3] }
  }
}
```

**Self-consistency check (instrument alarm):** re-grade all 3 reps WITH the floor test
(`pytest tasks/$TASK/test -q`, full battery). Every rep must now pass its own family's
floor. If any rep of the BASE model fails its own floor, rep variance exceeds the margin —
that is a broken margin assumption, not a bad model: STOP, note it in the scope doc, and
raise it with Rich before any freeze.

## 5. Verify, commit, hand off

1. `python3 -m pytest tests/ -q` — the whole battery green (the baselines-file shape test
   covers the new family record).
2. Commit the run records + the baselines file:
   `RUN-EVAL-GC-BASELINE: base ${BASE_FAMILY}/${QUANT} baseline — <solved counts> (K=3, GB10)`
   — the `runs/` home is committed (the `61df81a` convention).
3. If you paused the keepalive: `sudo systemctl start llama-swap-keepalive.timer`
   (interactive sudo required).
4. Hand `docs/research/ideas/gc-heldout-suite-scope.md` to Rich → **he freezes by
   commit** (subset composition, −2 margin, no-absolute-floor, gate table, median
   aggregation) → the suite is armed; the first candidate grade may proceed, and from it
   every fine-tune RESULTS carries the paired general-capability verdict (S10 §2.5).
