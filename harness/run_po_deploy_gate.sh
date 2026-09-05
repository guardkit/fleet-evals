#!/usr/bin/env bash
# THE FACTORY DEPLOY GATE — grades the PO seat on the modes the factory actually uses.
#
# WHY THIS EXISTS (Rich's ruling, 2026-08-23). The frozen `po-heldout` suite puts THREE of its four
# tasks on extract, by design: its scope says "extract gets three of four tasks because extract is the
# deployment mode with real stakes". That was true when it was frozen in July. It is not what the
# factory uses now. The consequence is measured, not theoretical — the v4 controlled run scored 3/12,
# and 75% of that denominator was a mode Rich does not use, while the tune's real result was buried:
#
#     po-held-001/002/003  extract     base 0/3 each   tune 0/3 each
#     po-held-004          greenfield  base 0/3        tune 3/3
#     po-held-007          feature-spec                tune 17/17
#
# This gate grades feature-spec, the revise path, greenfield and idea. Extract is DEFERRED, not
# abandoned: its missing `<think>` is a real unresolved defect (po-lane-state §23.4) and `po-heldout`
# still exists to measure it. Two gates, two questions: "is the seat good at what we use it for" and
# "did we fix extract yet".
#
# THE REVISE PATH was added 2026-09-05, and it is here because of a live defect. Rich sent the note
# "drop example 3, seven exactly is the rule" back on a spec card. The forge re-dispatched the spec
# writer with the note at the top of its prompt; the writer returned the same six worked examples with
# example 3 reworded, its coach scored 1.0, and the second card he was shown was identical to the
# first with no word that nothing had changed. One of his three touches silently did nothing. These
# two tasks measure it: po-held-009 sends a note that drops an example, po-held-010 a note that
# changes one word. Both are graded by ordinary code on the produced list, not by a model.
#
# It spans two runners because the artefacts differ — 007 produces a FILE TREE, the others produce
# response.txt. That is a property of the modes, not an accident.
#
# THE BAR IS NOT SET HERE. Composition is a lane decision; a pass mark is Rich's. This reports
# per-task and per-gate and states no verdict.
set -uo pipefail
MODEL="${MODEL:?set MODEL, e.g. po-ft-v6}"
ENDPOINT="${ENDPOINT:-http://127.0.0.1:9310/v1}"
TEMP="${TEMP:-0}"          # greedy: the ~1-in-3 feature-spec repetition loop appears at temp 0.3
TOPP="${TOPP:-0.95}"
MAXTOK="${MAXTOK:-16384}"  # production's registered-mode cap
REPS="${REPS:-3}"          # greedy decode is deterministic, so REPS=1 is sufficient at TEMP=0
cd "$(dirname "$0")/.."

echo "=== PO DEPLOY GATE — model=$MODEL temp=$TEMP ==="
echo "  modes graded: feature-spec (007) · revise (009, 010) · greenfield (004) · idea (005)"
echo "  extract DEFERRED — see po-heldout and po-lane-state §23.4"
echo

echo "--- feature-spec (po-held-007, file-tree artefact) ---"
python3 harness/run_po_spec_eval.py --model "$MODEL" --endpoint "$ENDPOINT" \
  --temperature "$TEMP" --max-tokens "$MAXTOK" --rep "$REPS" --grade \
  || echo "  !! 007 RETURNED NONZERO — read the run dir, do not treat as pass"

echo
echo "--- the revise path (po-held-009, po-held-010: did the note actually land?) ---"
for T in po-held-009-spec-revise-drop-example po-held-010-spec-revise-one-word; do
  python3 harness/run_po_spec_eval.py --model "$MODEL" --endpoint "$ENDPOINT" --task "$T" \
    --temperature "$TEMP" --max-tokens "$MAXTOK" --rep "$REPS" --grade \
    || echo "  !! $T RETURNED NONZERO — read the run dir, do not treat as pass"
done

echo
echo "--- greenfield + idea (po-held-004, po-held-005) ---"
# NOTE 2026-08-23: po-held-005 has an assembler in run_po_eval but has NEVER BEEN RUN. First contact
# may surface harness defects rather than model defects — po-held-008's first run found a structural
# cap that no model could clear. Read a 005 failure with that in mind before blaming the seat.
# `--task` filters WITHIN a suite and discover_task_dirs() matches the suite EXACTLY, so the suite must
# be named or the task resolves to nothing. Omitting it here would have made po-held-005 (suite
# po-heldout-idea) silently match zero tasks and — behind `|| true` — report as though it had passed.
# That is the same defect shape as §22: a check whose coverage is narrower than its claim.
for PAIR in "po-heldout:po-held-004-greenfield-discipline" "po-heldout-idea:po-held-005-idea"; do
  S="${PAIR%%:*}"; T="${PAIR##*:}"
  python3 harness/run_po_eval.py --model "$MODEL" --endpoint "$ENDPOINT" \
    --suite "$S" --task "$T" --temperature "$TEMP" --top-p "$TOPP" --max-tokens "$MAXTOK" \
    --rep "$REPS" --grade \
    || echo "  !! $T RETURNED NONZERO — read the run dir, do not treat as pass"
done
echo
echo "=== DEPLOY GATE COMPLETE — read per-task grades above; no verdict is asserted here ==="
