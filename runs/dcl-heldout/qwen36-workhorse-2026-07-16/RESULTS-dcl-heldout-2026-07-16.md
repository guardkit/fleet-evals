# RESULTS — dcl-heldout authoring calibration gate — qwen36-workhorse — 2026-07-16

**Candidate:** `qwen36-workhorse` = Qwen3.6-35B-A3B, UD-Q4_K_XL GGUF, served on llama-swap `:9000` (Node A GB10 fleet host, llama.cpp `-ngl 999` full offload, single slot `-np 1`). This is the FIRST graded calibration run of the frozen suite (the local architect/product-owner seat — the D-ii / G3 fine-tune-or-not candidate).
**Suite:** `dcl-heldout` — DCL authoring/repair, graded by the vendored DCL compiler (`harness/dcl/bin/dcl-check.mjs` + `dcl.wasm`, upstream `russelleast/Capability-Language` @ `4f9fbe56`, Apache-2.0).
**Frozen thresholds:** `docs/research/ideas/dcl-heldout-suite-scope.md` §3, frozen at commit `8d2d6762c38ef0a3aab1c8d5904dd456e008500b`.
**Scope doc (the frozen bar + sampling pins + single-slot law):** `docs/research/ideas/dcl-heldout-suite-scope.md`.
**Verifier integrity at grade time:** `python3 -m pytest tests/test_dcl_verifier_integrity.py -q` → **29 passed** (the three-sided proof, standing pre-grade gate). Full `tests/` pre-grade gate: **347 passed** (verifier-integrity law, green before any grading).
**Runner divergence (by design):** answer sheets produced by `harness/run_dcl_heldout.py` (ONE fresh toolless generation per rep, no system tools, no retry-on-bad-content — a bad `.dcl` is a RESULT). The runner NEVER grades; grading is the task's gate battery. Per-rep `config.json` pins: model + endpoint + sampling + `prompt_sha256` + `freeze_commit` + `wall_time` + `usage` + `finish_reason` + the single-slot probe receipt. Runner snapshot beside this doc: `run_dcl_heldout.py` (sha256 `b698181d…`, byte-identical to `harness/run_dcl_heldout.py` at grade time).
**Sampling pins (frozen, §4):** temperature `0.3`, top_p `0.9`, max_tokens `16384`, K = `3` reps/task, fresh session per rep, `timeout_seconds = 900`. (Note: the served checkpoint's own defaults are `--temp 0.6 --top-p 0.95`; every request overrode them with the frozen pins — confirmed in each `config.json`.)

---

## The frozen bar (verbatim, §3.2 — applied, never massaged)

**A seat may be trusted to author DCL in the machine chain iff all of:**

- **≥ 2 of 3 reps compile-clean on *every* authoring task** (`dcl-held-001`, `-002`, `-003`), **AND**
- **3 of 3 reps compile-clean on the repair task** (`dcl-held-004`).

Per-rep axes (the mechanical gates, every rep — the compiler grades, nothing here judges taste):
1. **Compile-clean** (G1) — checker `ok:true`, `errorCount == 0`, exit 0 (the load-bearing axis).
2. **Structural floor** (G2) — a `capability` with an `intent`, at least one `outcome`, and a `lifecycle`.
3. **Oracle-on-bare-run** — the task's own `solution/` oracle passes its full gate on a bare run (standing pre-grade; a broken oracle = broken verifier, not a hard task).
4. **Repair only — semantic-preservation floor** (`dcl-held-004`) — the repair is compile-clean AND still declares `capability GetStats`, `intent StatsRequest`, `outcome StatsRetrieved`, `event StatsRetrievedEvent`.

A rep that truncates (`finish_reason == "length"`) is a **row FAIL recorded as `truncated-generation`** — distinct from a compile failure. **No rep truncated this run** — all 12 finished `stop`.

---

## Per-task × per-rep grade

Graded with `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q` (real exit code captured separately into each `grade-exit.txt`, never masked through `tee`).

| Task | Rep | G1 compile-clean | G2 structural floor | semantic-preservation (004) | errorCount | finish_reason | wall (s) | comp_tok | compile-clean? | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| dcl-held-001-author-stats | 1 | FAIL(compiles_zero_errors) | PASS | — | 3 | stop | 91.12 | 5464 | NO | FAIL |
| dcl-held-001-author-stats | 2 | FAIL(compiles_zero_errors) | PASS | — | 2 | stop | 94.31 | 5615 | NO | FAIL |
| dcl-held-001-author-stats | 3 | FAIL(compiles_zero_errors) | PASS | — | 2 | stop | 101.24 | 6026 | NO | FAIL |
| dcl-held-002-author-version | 1 | FAIL(compiles_zero_errors) | PASS | — | 3 | stop | 89.43 | 5305 | NO | FAIL |
| dcl-held-002-author-version | 2 | FAIL(compiles_zero_errors) | PASS | — | 3 | stop | 105.20 | 6273 | NO | FAIL |
| dcl-held-002-author-version | 3 | FAIL(compiles_zero_errors) | PASS | — | 7 | stop | 83.35 | 5002 | NO | FAIL |
| dcl-held-003-author-uptime | 1 | FAIL(compiles_zero_errors) | PASS | — | 1 | stop | 96.64 | 5764 | NO | FAIL |
| dcl-held-003-author-uptime | 2 | FAIL(compiles_zero_errors) | PASS | — | 3 | stop | 89.10 | 5358 | NO | FAIL |
| dcl-held-003-author-uptime | 3 | FAIL(compiles_zero_errors) | PASS | — | 1 | stop | 97.95 | 5890 | NO | FAIL |
| dcl-held-004-repair-diagnostics | 1 | PASS | — | PASS | 0 | stop | 64.26 | 3842 | YES | PASS |
| dcl-held-004-repair-diagnostics | 2 | PASS | — | PASS | 0 | stop | 65.95 | 3982 | YES | PASS |
| dcl-held-004-repair-diagnostics | 3 | PASS | — | PASS | 0 | stop | 74.49 | 4479 | YES | PASS |

(For the authoring tasks the per-task battery is 5 tests — `checker_available`, `candidate_exists`, `compiles_zero_errors` [G1], `structural_floor` [G2], `broken_fixture_is_rejected` [false-green guard]. Every authoring rep scored **1 failed, 4 passed**: only G1 failed; G2 structural floor and the false-green guard passed on every rep. For `-004` the battery is 5 tests including `repair_preserves_declared_semantics` — all 5 passed every rep.)

**Compile-clean tally (the bar's currency):**

| Task | reps compile-clean | required | met? |
|---|---|---|---|
| dcl-held-001-author-stats | 0/3 | ≥ 2/3 | **NO** |
| dcl-held-002-author-version | 0/3 | ≥ 2/3 | **NO** |
| dcl-held-003-author-uptime | 0/3 | ≥ 2/3 | **NO** |
| dcl-held-004-repair-diagnostics | 3/3 | 3/3 | **YES** |

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **Authoring bar — ≥2/3 compile-clean on 001 AND 002 AND 003:** **NOT met.** All three authoring tasks scored **0/3** compile-clean (every one of the 9 authoring reps failed G1). This is not a one-flaky-rep miss the ≥2/3 tolerance was designed to absorb — it is a clean miss on all three tasks.
- **Repair bar — 3/3 compile-clean on 004:** **met.** All 3 repair reps compile-clean AND preserved the declared `capability GetStats` / `intent StatsRequest` / `outcome StatsRetrieved` / `event StatsRetrievedEvent`.
- **Oracle-on-bare-run (standing, pre-grade):** **4/4 green at grade time** — the three-sided integrity battery (`tests/test_dcl_verifier_integrity.py`, 29 passed) asserts every task's `solution/` oracle compiles clean on a bare run; each per-task battery's false-green guard (`broken_fixture_is_rejected` / `broken_input_is_rejected`) also passed. The verifier is sound; the FAILs below are the candidate's, not the grader's.

## VERDICT: **NOT-YET** (not trusted to author DCL in the machine chain)

A FAIL against the frozen bar is a RESULT, reported plainly. The seat **passes the repair bar 3/3** but **fails the authoring bar on all three tasks (0/3 each)**, so the suite reports **NOT-YET**. Per the §3 pre-registered disposition, the routed action is a **prompt / grammar-reference change or the D-ii / G3 fine-tune** — **not** a threshold edit, and **not** letting this seat author DCL in the chain on a failing sheet. A green suite would be a necessary gate, not a promotion by itself, and never a statement that the DCL produced is *good* — that judgment stays human (§9).

The split is the informative signal: **structure is not the problem** (G2 structural floor passed 9/9 authoring reps — the seat reliably produces the required shape blocks, as the spike found), and **with the compiler's verbatim diagnostics in hand the seat repairs cleanly 3/3**. What it cannot yet do is land compile-clean DCL *zero-shot* from a README-level few-shot — it keeps stepping outside DCL v1.0's closed vocabulary. That is exactly the D-ii / G3 gap this suite exists to measure.

## Environment + single-slot receipts

- **Served seat:** `qwen36-workhorse` on llama-swap `:9000` (`-np 1`, single slot). `/running` server line at grade time:
  `llama-server --port 5816 --model /opt/llama-swap/models/qwen36-35b/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf --alias qwen36-workhorse --ctx-size 131072 --batch-size 2048 --ubatch-size 2048 --threads 16 -ngl 999 --no-mmap --flash-attn on --jinja --reasoning auto --temp 0.6 --top-p 0.95 -np 1` (request-level sampling overrode the checkpoint defaults with the frozen pins temp 0.3 / top_p 0.9 / max_tokens 16384).
- **GPU note:** Node A GB10 fleet host; full-offload (`-ngl 999`) 35B-A3B MoE at UD-Q4_K_XL; generations ran ~83–105 s wall (authoring) / ~64–74 s (repair), ~5.0k–6.3k completion tokens each under `--reasoning auto` (the reasoning-heavy budget the token-ceiling lesson pinned 16384 for — no rep came near the ceiling; max completion was 6273 tokens).
- **Single-slot law (§4, per rep — 12/12 receipts):** before every one of the 12 seat calls the runner probed `GET http://127.0.0.1:9000/running` and required alias `qwen36-workhorse` in state `ready`; every probe returned `ok:true` (recorded in each `<rep-dir>/config.json` → `single_slot_probe` = `{"url": "http://127.0.0.1:9000/running", "ok": true}`). Calls were strictly sequential, one bounded call in flight; nothing else drove the slot during the grade. No probe refused; no call was concurrent.
- **Runner:** `harness/run_dcl_heldout.py --freeze-commit 8d2d6762c38ef0a3aab1c8d5904dd456e008500b`. Per-rep `config.json` carries model, endpoint, sampling, `prompt_sha256`, `freeze_commit`, `wall_time`, `usage`, `finish_reason`, single-slot receipt. Prompt determinism confirmed: `prompt_sha256` is byte-stable across the 3 reps of each task (001 `12eb75f3…`, 002 `6831dae4…`, 003 `ebc5b563…`, 004 `bd63d319…`) and distinct across tasks. Artifact integrity confirmed: `response.dcl` is byte-identical to `raw-response.json`'s `choices[0].message.content` for all 12 reps.
- **node / vendored checker:** `node v24.15.0`; `sha256sum -c harness/dcl/bin/SHA256SUMS` → all OK (`dcl.wasm`, `wasm_exec.js`, `LICENSE`, `NOTICE`); checker byte-identical to `spike/dcl-authoring/bin/`. Frozen files (`tasks/dcl-held-*`, `harness/dcl_gates.py`, `harness/dcl/bin/**`, `tests/test_dcl_verifier_integrity.py`, the scope doc) are byte-identical to freeze commit `8d2d676` (`git diff --stat` empty).

## Build-time calibration baseline (measured, §7 — not estimated)

| Item | Method | Result |
|---|---|---|
| Oracle catchability | each `solution/` oracle graded via the integrity battery | 4/4 tasks PASS their own gate on a bare run (`tests/test_dcl_verifier_integrity.py` 29 passed) |
| Compile-fail demo | each per-task `broken_fixture` / `broken_input` | FAIL exactly the compile gate (`broken_fixture_is_rejected` / `broken_input_is_rejected` passed every rep-battery run) |
| Semantic-preservation demo | `-004` preservation floor | `repair_preserves_declared_semantics` PASSED all 3 repair reps (and is asserted in the integrity battery) |
| Good-fixture demo | tricky-but-clean files per task | integrity battery green |
| Data point 1 (recorded) | the spike seat's finished attempt (`SEAT-RESULT.md`) | compile FAIL, `errorCount 2` (invented `machine` / `in_memory`) — the anecdote this suite generalises; **this run confirms and generalises it** (below) |

## INVALID reps

**None.** No rep aborted on transport; no `ABORTED.json` was written anywhere under this run root; no re-run-in-place was needed. All 12 reps produced a graded answer sheet on the first attempt.

## Honest notes

**The verdict is a real, honest FAIL — 0/3 on every authoring task, 3/3 on repair.** Reported plainly, not massaged. Detail and diagnostic patterns:

**1. The spike's invented-enum-literal class GENERALISES — it is the dominant authoring failure.** The spike's single data point (invented actor kind `machine`, effect kind `in_memory`, `errorCount 2`) was not a one-off. `DCL_SEM_EFFECT_KIND_UNKNOWN` — the seat inventing effect kinds outside DCL v1.0's closed vocabulary — appears in **5 of the 9 authoring reps**, with newly-invented literals `computation` (001-r1, 002-r2, 003-r1, 003-r2) and `system` (002-r1). The compiler catches each, line-located. This is precisely the class the scope doc predicted a fuller grammar/enum reference or a compile-repair pass would close — and the repair result below is the direct evidence for that prediction.

**2. A NEW failure class the spike did not surface — invalid string-literal lexing.** `DCL_LEX_UNEXPECTED_CHAR` on an ASCII double-quote appears in 3 reps (001-r1 L36, 002-r3 L36, 003-r2 L31): the seat writes predicate lines like `rule IsGet: input.method is "GET"`, using double-quoted string literals where the DCL v1.0 lexer does not accept them (verified ASCII `0x22`, not smart quotes). A sibling of the invented-vocabulary class — the model reaching for a general-purpose-language idiom the closed DCL grammar rejects.

**3. Other single/low-frequency classes (all real compiler errors, line-located):** `DCL_SEM_CAUSATION_DECISION_UNKNOWN` (unknown v0.2 causation decision — 001-r2, 002-r1); `DCL_SEM_AMBIGUOUS_LIFECYCLE_TRANSITION` (same source step + trigger → multiple targets — 001-r2, 001-r3); `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` (idempotency value — 001-r3); `DCL_PARSE_EXPECTED_DECLARATION` / `DCL_PARSE_EXPECTED_TOKEN` / `DCL_PARSE_EXPECTED_IDENTIFIER` (malformed declaration blocks — 002-r2, 002-r3, 003-r3); `DCL_SEM_LIFECYCLE_TRIGGER_KIND` (002-r1). Worst rep was 002-r3 at `errorCount 7`; best authoring reps (003-r1, 003-r3) were `errorCount 1` — genuine near-misses, but a near-miss is still a compile FAIL under the frozen bar.

**4. Structure is NOT the failure mode.** G2 structural floor passed on **all 9** authoring reps: the seat reliably emits a `capability` with an `intent`, an `outcome`, and a `lifecycle` — the shape is there, exactly as the spike found ("structurally right, not compile-clean"). The gap is entirely in DCL's closed vocabularies and fine-grained syntax.

**5. Repair (004) is the strong positive signal — and it validates the routed action.** All 3 repair reps landed compile-clean (`errorCount 0`) AND preserved every declared name, at meaningfully lower token cost (~3.8k–4.5k vs ~5.0k–6.3k for authoring). Given the compiler's verbatim diagnostics, the seat closes the exact gap it cannot close zero-shot. This is direct corroboration of §3's disposition: a compile-repair loop (or a grammar-reference-enriched prompt, or the G3 fine-tune) is the plausible bridge — the seat is not "can't do DCL," it is "can't land it clean cold from a README-level few-shot yet."

**6. Candidate broken-fixture proposals (floors never shrink, §5).** The two new authoring failure classes not already in the near-miss corpus are worth folding into `tests/broken_fixtures/` on a future instrument revision (which reopens the scope doc first, never silently): (a) an invented **effect kind** `computation` (extends the existing `in_memory` near-miss fixture to a second invented effect-kind literal), and (b) the **double-quoted string-literal in a predicate** (`is "GET"`) `DCL_LEX_UNEXPECTED_CHAR` class. Recorded here as observations; not added this run (frozen suite untouched, additive posture held).
