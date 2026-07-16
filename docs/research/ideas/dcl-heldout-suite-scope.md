# DCL Held-Out Suite — Authoring Calibration Gate (Phase D / D4)

**Status:** **FROZEN 2026-07-16 (Rich, attended in-session — this commit IS the freeze;
close-out moment #4).** Thresholds frozen exactly as proposed (authoring tasks ≥2/3 reps
compile-clean each, repair task 3/3 — §5). From here, **thresholds may only ever be
*raised*** (never lowered), and any instrument revision reopens this doc BEFORE the next
re-freeze, never silently (the po-/gc-heldout lineage). *Mechanics note, honest:* the
coordinator's staged freeze commands were flawed (the doc was already committed unchanged,
so there was nothing to stage); this status flip + commit executes Rich's written in-session
freeze declaration of the same evening.
**Date:** 2026-07-16 (Phase-D coordinator session; built to
`ai-transition/docs/dcl-adoption-phase-d-design-2026-07-16.md` §4).
**Repo:** fleet-evals · new suite `dcl-heldout` (tasks `dcl-held-001-author-stats`,
`dcl-held-002-author-version`, `dcl-held-003-author-uptime`,
`dcl-held-004-repair-diagnostics`).
**Relationship to the frozen suites:** strictly additive, identical posture to the
po-/gc-/arch-/coach-/qav-heldout scopes — frozen files are never edited, frozen discovery
globs stay blind to `dcl-held-*` by construction, and the DCL spike dir
(`spike/dcl-authoring/`) is a frozen historical record that is never touched (§6).
**Consumer (named):** the decision **"may a local seat author DCL inside the machine
(autobuild / task-work) chain yet?"** — the D-ii / G3 fine-tune-or-not question from
`dcl-factory-evaluation-2026-07.md`. This suite is the calibration gate that must go green
*before* any seat is trusted to author DCL in that chain. Until the freeze + a graded run
exist, that trust does not exist.

---

## 0. The one-minute version (one mental model)

**Jargon, defined once.** *DCL* = the Capability Language, a small compiler-checked format
for writing a feature's behaviour spec (upstream `github.com/russelleast/Capability-Language`,
Apache-2.0). *Seat* = a served model role (here the local architect alias,
`qwen36-workhorse` on llama-swap `:9000`). *Compile-clean* = the DCL checker returns
`ok:true` with `errorCount == 0`. *Oracle* = the hand-authored reference answer that ships
in each task's `solution/`. *Rep* = one independent generation attempt at the task.

**The whole idea in one sentence.** Before we let a seat write DCL where it matters, we
make it write DCL here — four small authoring/repair tasks graded by the *real compiler* —
and we check, against thresholds Rich freezes up front, whether it lands compile-clean
often enough to trust. **The compiler grades; the runner never does; nothing here judges
taste.** A failing seat is a RESULT, not a problem — we already have the first data point
(§1).

---

## 1. Objective — what this gates, and the data point we start from

A **pre-registered, deterministic calibration gate** for DCL authoring. Four doc-shaped
tasks, each graded by the vendored DCL compiler on three axes only (compile-clean,
structural floor, oracle-on-bare-run), with a suite-level pass bar frozen by Rich **before**
any seat is graded against it. The gate answers one question: *can a seat author
compile-clean DCL reliably enough to be let into the machine chain?* It does not grade DCL
quality, taste, or modelling judgment — those are not mechanical, so they are out of scope
(§9).

**Data point 1 already exists (the spike's graded seat near-miss).** The DCL spike ran one
bounded, honest attempt of the local architect seat at the `/stats` authoring task
(`spike/dcl-authoring/seat-attempt/SEAT-RESULT.md`). Reading it straight: the seat produced
a **structurally well-formed** capability on its first finished try — all nine block types,
sensible wiring mirroring the few-shot — but **failed the compile gate with `errorCount 2`**,
by inventing two enum literals outside DCL v1.0's closed vocabulary (actor kind `machine`,
effect kind `in_memory`). "Near miss, fixable" — exactly the class of mistake the compiler
exists to catch, and exactly what it caught, line-located. That single point is not a gate;
it is the reason this suite exists. This suite turns that one anecdote into a pre-registered,
repeatable measurement.

## 2. Tasks (N = 4; the folders exist under `tasks/dcl-held-00N-<slug>/`)

| Task | What the seat does | Oracle (in `solution/`) |
|---|---|---|
| `dcl-held-001-author-stats` | Author the `/stats` capability from the recorded planning inputs (the promoted spike task — same instruction + inputs S2 used, plus a DCL syntax few-shot) | the S2 hand-authored `capability.dcl` (spike copy, verbatim) |
| `dcl-held-002-author-version` | Author the `/version` capability from its recorded inputs (api_test FEAT-B70F artifacts, self-contained in `input/`) | authored reference capability |
| `dcl-held-003-author-uptime` | Author the `/uptime` capability from its recorded inputs (same shape as 002) | authored reference capability |
| `dcl-held-004-repair-diagnostics` | Given a **rejected** `.dcl` + the compiler's verbatim diagnostics, produce a compile-clean repair that **preserves the declared semantics** (the seat near-miss class + the factory recovery-lattice pattern as an eval task) | the reference repair (compile-clean AND declared names preserved) |

Three authoring tasks + one repair task: authoring is the capability under test; repair is
the near-miss recovery path (compiler-in-the-loop fix), which the spike showed is the
plausible bridge from "structurally right" to "compile-clean" — so it gets its own,
stricter bar (§3).

Each task's `task.toml` pins the real-task contract: `reps = 3`, `timeout_seconds = 900`,
`output_env = "PO_EVAL_OUTPUT_DIR"` (the repo-wide env-var convention, not PO-specific),
grading `command = "python3 -m pytest test/ -q"`. Candidate output is the raw
`response.dcl` in `$PO_EVAL_OUTPUT_DIR/`; oracle validation runs the same gates with the
env pointed at `solution/`.

## 3. Pre-registered gates + thresholds (Rich amends at freeze, then they only rise)

### 3.1 Per-task gates (the mechanical axes, every rep)

Every rep of every task is graded on exactly these, by the vendored compiler — no text
matching, no LLM judge:

1. **Compile-clean** — the checker returns `ok:true` with `errorCount == 0` on the
   candidate `response.dcl`. This is the load-bearing axis; it is the exact axis the spike
   seat failed.
2. **Structural floor** — the capability declares the required shape blocks (a `capability`
   with an `intent`, an `outcomes` block, and a `lifecycle`) so a file that compiles by
   being trivially empty cannot pass. (The spike seat *passed* this axis; it is a floor, not
   the bar.)
3. **Oracle-on-bare-run** — the task's own `solution/` oracle passes its full gate battery
   on a bare run (`ok:true`, zero errors). A task whose oracle cannot pass its own gate is a
   **broken verifier, not a hard task** (the standing verifier-integrity rule, §5).
4. **Repair task only — semantic-preservation floor** (`dcl-held-004`): the repaired file
   is compile-clean AND still declares the same `capability` / `intent` / `outcome` / `event`
   names as the rejected input (a repair that "fixes" errors by deleting the semantics is a
   fail, not a pass).

### 3.2 Suite calibration bar (PROPOSED — this is what Rich freezes)

**A seat may be trusted to author DCL in the machine chain iff all of:**

- **≥ 2 of 3 reps compile-clean on *every* authoring task** (`dcl-held-001`, `-002`, `-003`),
  **AND**
- **3 of 3 reps compile-clean on the repair task** (`dcl-held-004`).

The repair bar is strictest (3/3) on purpose: a compile-repair loop consumes the compiler's
verbatim diagnostics, so "still can't land it clean given the exact errors" is the strongest
possible negative signal about seating this model in the chain. The authoring bar (≥2/3)
tolerates one flaky rep, because the near-miss the spike found — a single invented
enum-literal — is precisely the sampling-variance failure a compile-repair pass or a fuller
grammar reference would close.

**These numbers are PROPOSED. Rich may amend any of them AT the freeze — that is the whole
point of the freeze.** After the freeze, thresholds may only ever be *raised* between
candidates, never lowered mid-grade, and any change to the instrument (tasks, gates, checker
pin) reopens this doc before the next freeze.

**Disposition of a FAIL:** the suite reports NOT-YET; the failing task + axis are named in
the RESULTS doc; the routed action is a prompt/grammar-reference change or the D-ii/G3
fine-tune, **not** a threshold edit and **not** letting a seat author DCL in the chain. A
green suite is a necessary gate, not a promotion by itself.

## 4. Sampling pins, reps, and runner discipline (all pinned)

- **Sampling (freeze values):** `temperature 0.3`, **`max_tokens 16384`**. K = **3 reps**
  per task, fresh session per rep, per-rep config recorded alongside `response.dcl`
  (model id + lineage + base/quant family + template + sampling), generation
  `timeout_seconds = 900`.
- **The token-ceiling lesson is pinned, not folklore.** The spike's *first* attempt
  truncated at `max_tokens 4096` with `finish_reason == "length"` and an **empty** answer —
  all 4096 tokens went to the reasoning channel under `--reasoning auto`; the model never
  reached the DCL. Only raising the ceiling to 16384 produced a graded answer
  (`SEAT-RESULT.md`, ~5.5k reasoning tokens on the finished try). A rep that truncates
  (`finish_reason == "length"`) is a **row FAIL recorded as `truncated-generation`**, a
  diagnostic distinct from a compile failure — never an INVALID run, never a silent skip.
- **The runner never grades (repo law).** Answer sheets are produced by a fresh toolless
  generation per rep against the served checkpoint; grading is the task's gate battery
  (`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task>/test -q`). The generator and
  the grader are separate programs, as with `harness/run_gc_heldout.py` — *"This runner NEVER
  grades: grading is the task's gate battery."* No fabricated or empty response is ever
  graded; an aborted rep writes an `ABORTED.json` and is re-run in place under the same
  pinned config (INVALID, not a failure), never skipped.
- **Single-slot discipline on `:9000` (repo law).** The served seat is a single-slot
  llama-swap handle (`-np 1`); before any generation the runner confirms the slot is free
  and idle (`GET /9000/running` shows the model `ready`, no `autobuild`/`feature-build`/
  `task-work`/orchestrator process running) and takes calls **sequentially, one bounded call
  at a time** — exactly the check the spike recorded before claiming the seat. Nothing else
  drives the slot during a grade.

## 5. Integrity battery — the three-sided proof (standing, pre-grade gate)

Before the suite may grade *anything*, `tests/test_dcl_verifier_integrity.py` must be green.
For **every task** it asserts the three-sided proof:

1. **The oracle passes its own gate** (`solution/response.dcl` → compile-clean + structural
   floor, and for `-004`, semantic-preservation). *A verifier whose oracle cannot pass is
   broken, not a hard task.*
2. **Every broken fixture fails its owning gate** (`tests/broken_fixtures/<task>/`): one
   fixture per defect class — including the seat near-miss class verbatim (invented enum
   literals `machine` / `in_memory`) and an undeclared-outcome typo — each fails the specific
   gate that owns it, `ok:false`, exit 1. *A verifier that cannot fail a known-bad file is
   also broken.*
3. **Every good fixture passes** (`tests/good_fixtures/<task>/`): legitimate-but-tricky
   compile-clean files that must PASS, so the gate is proven not stricter than registered.

Plus **floor-never-shrinks**: the fixture counts and the structural floor are pinned in the
integrity test and may only grow. This battery runs in plain `python3 -m pytest`, must be
green at grade time, and — per the false-green-corpus rule — never shrinks: every wild DCL
failure caught in the machine chain later joins `tests/broken_fixtures/`.

## 6. Additivity invariant (proven, not asserted)

Every path this suite adds is **new**. The invariant, tested at build end:

- The DCL spike dir `spike/dcl-authoring/` is **untouched** (frozen historical record); tasks
  vendor their own checker at `harness/dcl/bin/` (byte-identical, `SHA256SUMS` + provenance
  carried) and never reach into `spike/`.
- All frozen suites' discovery globs stay **blind** to `dcl-held-*` by construction; the
  pre-change `tests/` node-verdicts re-run **byte-identical** (0 lost, N added, 0 failures) —
  the po-/gc-heldout precedent.
- `git status` over previously-tracked files stays empty throughout the build (every
  `dcl-heldout` path is a new file).

## 7. Build-time calibration (sanctioned while PROPOSED; measured, not estimated)

| Item | Method | Expected at build |
|---|---|---|
| Oracle catchability | each `solution/` oracle graded as an answer sheet, by the compiler | 4/4 tasks PASS their own gate on a bare run |
| Compile-fail demo | each `broken_fixtures/<task>` (incl. the seat near-miss `machine`/`in_memory` class) | FAIL exactly the compile gate, `ok:false`, errors line-located |
| Semantic-preservation demo | a `-004` fixture that "repairs" by dropping a declared name | FAILS the preservation floor, passes compile alone |
| Good-fixture demo | tricky-but-clean files per task | PASS the whole battery |
| Data point 1 (recorded) | the spike seat's finished attempt (`SEAT-RESULT.md`) | compile FAIL, `errorCount 2` — the anecdote this suite generalises |

Build-time results land in the RESULTS template's baseline table (measured at build end, per
the po-/gc-heldout convention). If any recorded value changes on re-measurement, that is a
defect to investigate, not a number to silently update.

## 8. Freeze procedure (per the po-heldout precedent, `6f9b9b7`)

**The freeze IS Rich's commit of this doc.** The procedure:

1. The suite is handed to Rich built and green (per-task gates + the three-sided integrity
   battery + additivity invariant all proven).
2. Rich reviews §3, **amends the thresholds if he wants** (the ≥2/3-authoring / 3/3-repair
   bar, the sampling pins — these are his freeze values), and **freezes by committing this
   file**. That commit's SHA is the freeze reference.
3. **Only then** may a seat be graded. The frozen-thresholds SHA is recorded in **every
   future RESULTS doc and every run's `config.json`**, so a graded verdict always carries the
   exact thresholds it was judged against — nothing is re-derived at grade time.
4. After the freeze, thresholds may only *rise*; any instrument revision reopens this doc
   before the next freeze, never silently.

**This is Rich's moment #4 (the freeze) in the Phase-D done-bar.** Nothing in this lane
grades a seat before that commit exists.

## 9. Explicitly out of scope (so the gate is never over-read)

DCL *quality* / modelling taste / whether the capability is the *right* one for the endpoint
— not mechanical, not graded here · executing derived assertions against a live service
(that is the D3 live-gate's job, over api_test — this suite grades the authored `.dcl`, not a
running deploy) · the derivation rules R1–R10 (D2's tool; this suite is authoring-only) ·
seating a seat in the machine chain (this suite is the *gate* on that decision, not the
action) · running or training the fine-tune itself (the D-ii / G3 slot). **Standing
constraint:** this suite measures authoring reliability only; a green verdict is a necessary
floor, never a statement that the DCL produced is good — that judgment stays human.

---

**Next step:** Rich reviews this scope + the built suite, amends §3 if needed, and **freezes
by committing this file** (moment #4). The recorded SHA then rides with every RESULTS doc and
run `config.json`. When a candidate seat is graded:

```bash
cd fleet-evals
python3 -m pytest tests/test_dcl_verifier_integrity.py -q   # three-sided battery — green before any grade
# generate reps (runner never grades; single-slot :9000; temp 0.3 / max_tokens 16384):
#   per task under tasks/dcl-held-*, K=3 reps, per-rep config recorded, aborted reps re-run in place
PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task>/test -q   # compiler-graded, per rep
# then apply §3 verbatim in RESULTS-dcl-heldout-<date>.md (frozen-thresholds SHA recorded)
```
