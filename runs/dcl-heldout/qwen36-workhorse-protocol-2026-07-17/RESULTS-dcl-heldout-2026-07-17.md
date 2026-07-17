# RESULTS — dcl-heldout authoring calibration gate — qwen36-workhorse + §10 protocol — 2026-07-17

**Candidate:** `qwen36-workhorse` = Qwen3.6-35B-A3B, UD-Q4_K_XL GGUF, served on llama-swap `:9000` (Node A GB10 fleet host, llama.cpp `-ngl 999` full offload, single slot `-np 1`) — **under the §10 machine-chain authoring protocol** (standing vocabulary reference + ≤1 bounded compile→repair pass). This is the SECOND graded calibration run; the first (zero-shot, 2026-07-16, verdict NOT-YET) stands as the baseline record and was **not re-run** (`runs/dcl-heldout/qwen36-workhorse-2026-07-16/RESULTS-dcl-heldout-2026-07-16.md`).
**Suite:** `dcl-heldout` — DCL authoring/repair, graded by the vendored DCL compiler (`harness/dcl/bin/dcl-check.mjs` + `dcl.wasm`, upstream `russelleast/Capability-Language` @ `4f9fbe56`, Apache-2.0).
**Frozen thresholds:** `docs/research/ideas/dcl-heldout-suite-scope.md` §3, frozen at commit `8d2d6762c38ef0a3aab1c8d5904dd456e008500b` — **UNCHANGED by the §10 amendment**.
**§10 re-freeze (protocol amendment, thresholds untouched):** commit `8a3b9d187fce64cd642b48040ec2f99b84b358fe` (both shas stamped in every rep's `config.json` as `freeze_commit` + `refreeze_commit`).
**Scope doc (the frozen bar + sampling pins + single-slot law + the §10 protocol):** `docs/research/ideas/dcl-heldout-suite-scope.md`.
**Verifier integrity:** `python3 -m pytest tests/test_dcl_verifier_integrity.py -q` → **29 passed** (the three-sided proof, standing pre-grade gate; re-confirmed green at documentation time). Frozen instrument files (`tasks/**`, `harness/dcl_gates.py`, `harness/dcl/bin/**`, `tests/test_dcl_verifier_integrity.py`, the scope doc) are byte-identical to the §10 re-freeze commit `8a3b9d1` (`git diff --stat` empty over those paths).
**Runner divergence (by design):** answer sheets produced by `harness/run_dcl_heldout.py` (toolless generation per rep, no system tools, no retry-on-bad-content — a bad `.dcl` is a RESULT; under `--repair-loop` at most ONE bounded second call, and the checker invocation that decides it is a firing decision, NOT a grade). The runner NEVER grades; grading is the task's gate battery. Runner snapshot beside this doc: `run_dcl_heldout.py` (sha256 `fd6463cee3f3b00f0f47af7f94dc97afc89276a9bfba3a2c3353a3968d89e360`, byte-identical to `harness/run_dcl_heldout.py` at documentation time — the §10 protocol runner, additive commits `6280857` [E1: `--vocab-ref` + bounded compile→repair] + `415069a` [E1b: `--refreeze-commit` stamp]).
**Sampling pins (frozen, §4):** temperature `0.3`, top_p `0.9`, max_tokens `16384`, K = `3` reps/task, fresh session per rep, `timeout_seconds = 900`. (The served checkpoint's own defaults are `--temp 0.6 --top-p 0.95`; every request overrode them with the frozen pins — confirmed in each `config.json`.)

---

## The §10 protocol of record (as run — stated, not implied)

Authoring tasks `dcl-held-001/-002/-003` were generated with **both** protocol flags:

- **`--vocab-ref harness/dcl/vocab-reference.md`** — the compiler-verified closed vocabulary at upstream pin `4f9fbe56414eecbd100c337da770e1e24c2fcc85` (v1.0.6), verified by 227 accept/reject probes through the vendored checker (receipt: `harness/dcl/vocab-probes-receipt.md`). File sha256 `25121afe7415b15cba161fa2f3e728dad7095675f214a298317b51bb0e8fee2b`, recorded in every authoring rep's `config.json → vocab_ref`. The reference is appended to the composed task instruction; `prompt_sha256` covers the full composed prompt including it.
- **`--repair-loop` — bound: ≤ 1 compile→repair pass.** If the first generation compiles dirty, exactly ONE second call is made carrying the checker's verbatim diagnostics envelope plus the first attempt; **the graded candidate is the final response**. Both attempts and the checker envelope are persisted per rep (`attempt-1.dcl`, `attempt-1-checker.json`, `raw-response-2.json`); each rep records `zero_shot_clean` vs `repaired_clean` (informational split — the bar does not distinguish them).
- **Repair task `dcl-held-004`: protocol UNCHANGED — NO flags.** Its input already carries diagnostics; no vocabulary reference, no second loop. Receipt: the 004 `config.json`s carry neither `vocab_ref` nor `repair_loop`, and their `prompt_sha256` (`bd63d319…`) is **byte-identical to the 2026-07-16 baseline run's** 004 prompt sha.

## The frozen bar (verbatim, §3.2 — applied, never massaged; UNCHANGED by §10)

**A seat may be trusted to author DCL in the machine chain iff all of:**

- **≥ 2 of 3 reps compile-clean on *every* authoring task** (`dcl-held-001`, `-002`, `-003`), **AND**
- **3 of 3 reps compile-clean on the repair task** (`dcl-held-004`).

Per-rep axes (the mechanical gates, every rep — the compiler grades, nothing here judges taste):
1. **Compile-clean** (G1) — checker `ok:true`, `errorCount == 0`, exit 0 (the load-bearing axis).
2. **Structural floor** (G2) — a `capability` with an `intent`, at least one `outcome`, and a `lifecycle`.
3. **Oracle-on-bare-run** — the task's own `solution/` oracle passes its full gate on a bare run (standing pre-grade; a broken oracle = broken verifier, not a hard task).
4. **Repair only — semantic-preservation floor** (`dcl-held-004`) — the repair is compile-clean AND still declares `capability GetStats`, `intent StatsRequest`, `outcome StatsRetrieved`, `event StatsRetrievedEvent`.

A rep that truncates (`finish_reason == "length"`) is a **row FAIL recorded as `truncated-generation`** — distinct from a compile failure. **No rep truncated in the graded run of record** — all 14 seat calls (12 first-attempt + 2 repair) finished `stop`.

---

## Per-task × per-rep grade (the run of record)

Graded with `PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q` (real exit code captured separately into each `grade-exit.txt`, never masked through `tee`). **All 12 reps: `5 passed`, exit 0.** `errorCount` below is the vendored checker's count on the graded candidate (`response.dcl`); "loop fired" = a second call was made (`attempts: 2`, `raw-response-2.json` present).

| Task | Rep | Gate result | errorCount | zero_shot_clean | repaired_clean | loop fired | finish_reason (first / repair) | wall s (first + repair) | completion tok (first + repair) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| dcl-held-001-author-stats | 1 | 5 passed, exit 0 | 0 | true | — | no | stop | 143.13 | 8160 | PASS |
| dcl-held-001-author-stats | 2 | 5 passed, exit 0 | 0 | true | — | no | stop | 97.78 | 5615 | PASS |
| dcl-held-001-author-stats | 3 | 5 passed, exit 0 | 0 | true | — | no | stop | 95.80 | 5489 | PASS |
| dcl-held-002-author-version | 1 | 5 passed, exit 0 | 0 | false | true | **YES** | stop / stop | 96.02 + 74.72 | 5520 + 4227 | PASS |
| dcl-held-002-author-version | 2 | 5 passed, exit 0 | 0 | true | — | no | stop | 104.98 | 5990 | PASS |
| dcl-held-002-author-version | 3 | 5 passed, exit 0 | 0 | false | true | **YES** | stop / stop | 90.32 + 62.19 | 5051 + 3519 | PASS |
| dcl-held-003-author-uptime | 1 | 5 passed, exit 0 | 0 | true | — | no | stop | 110.93 | 6272 | PASS |
| dcl-held-003-author-uptime | 2 | 5 passed, exit 0 | 0 | true | — | no | stop | 105.74 | 5934 | PASS |
| dcl-held-003-author-uptime | 3 | 5 passed, exit 0 | 0 | true | — | no | stop | 80.64 | 4666 | PASS |
| dcl-held-004-repair-diagnostics | 1 | 5 passed, exit 0 | 0 | — (no protocol) | — | — (no loop by design) | stop | 57.18 | 3354 | PASS |
| dcl-held-004-repair-diagnostics | 2 | 5 passed, exit 0 | 0 | — (no protocol) | — | — (no loop by design) | stop | 72.18 | 4272 | PASS |
| dcl-held-004-repair-diagnostics | 3 | 5 passed, exit 0 | 0 | — (no protocol) | — | — (no loop by design) | stop | 68.58 | 4062 | PASS |

(Per-task battery: 5 tests — `checker_available`, `candidate_exists`, `compiles_zero_errors` [G1], `structural_floor` [G2], `broken_fixture_is_rejected` [false-green guard]; for `-004`, `repair_preserves_declared_semantics` replaces the structural test in the battery of 5. Every rep passed all 5. G2 structural floor and the semantic-preservation floor passed everywhere; nothing passed by being trivially empty.)

**Compile-clean tally (the bar's currency):**

| Task | reps compile-clean | required | met? |
|---|---|---|---|
| dcl-held-001-author-stats | 3/3 | ≥ 2/3 | **YES** |
| dcl-held-002-author-version | 3/3 | ≥ 2/3 | **YES** |
| dcl-held-003-author-uptime | 3/3 | ≥ 2/3 | **YES** |
| dcl-held-004-repair-diagnostics | 3/3 | 3/3 | **YES** |

## §3 verdict (applied verbatim — no post-hoc adjustment; thresholds unchanged by §10)

- **Authoring bar — ≥2/3 compile-clean on 001 AND 002 AND 003:** **met** — 3/3 on every authoring task (the bar required only ≥2/3).
- **Repair bar — 3/3 compile-clean on 004:** **met** — all 3 repair reps compile-clean AND preserved the declared `capability GetStats` / `intent StatsRequest` / `outcome StatsRetrieved` / `event StatsRetrievedEvent`.
- **Oracle-on-bare-run (standing, pre-grade):** **4/4 green** — the three-sided integrity battery (`tests/test_dcl_verifier_integrity.py`, 29 passed) asserts every task's `solution/` oracle compiles clean on a bare run; each per-task battery's false-green guard (`broken_fixture_is_rejected` / `broken_input_is_rejected`) also passed on every rep. The verifier is sound; the PASSes are the candidate protocol's, honestly earned.

## VERDICT: **BAR CLEARED — the candidate protocol (qwen36-workhorse + §10) may author DCL in the machine chain**

Authoring 3/3 compile-clean on every task (bar: ≥2/3) AND repair 3/3 — 12/12 reps passed their full gate battery. **The unit that cleared the bar is the protocol, not the bare seat**: `qwen36-workhorse` *plus* the standing compiler-verified vocabulary reference *plus* the ≤1 bounded compile→repair pass. The 2026-07-16 zero-shot record (0/9 authoring) stands unrevised beside this one; the same seat without the protocol remains NOT-YET.

**Caveat, stated plainly: machine-chain wiring is a separate step.** This verdict is the *gate*, not the wiring. guardkit's oracle uses compile-only today; wiring seat-authoring into the machine chain (who invokes the protocol, where the vocabulary reference and repair loop live in the chain, what consumes the authored DCL) is future work gated on this verdict — it does not happen by virtue of this document. And per §9, a green suite never says the DCL produced is *good* — that judgment stays human.

## Comparison — zero-shot baseline vs single-intervention variants vs the protocol

Per-task gate-pass counts (compile-clean per the task battery). Baseline = `runs/dcl-heldout/qwen36-workhorse-2026-07-16/` (read, never re-run). Variants = `calibration/dcl-authoring-variants/` — **informational numbers, not bar verdicts** (§10); each ran the three authoring tasks only, K=3, same frozen pins, same freeze shas stamped.

| Task | Zero-shot baseline (07-16) | A: vocab-only | B: loop-only | Protocol (vocab + loop) |
|---|---|---|---|---|
| dcl-held-001-author-stats | 0/3 | 3/3 | 2/3 † | 3/3 |
| dcl-held-002-author-version | 0/3 | 1/3 | 0/3 | 3/3 |
| dcl-held-003-author-uptime | 0/3 | 1/3 | 3/3 | 3/3 |
| **Authoring total** | **0/9** | **5/9** | **5/9** | **9/9** |
| dcl-held-004-repair-diagnostics | 3/3 | not run (004 protocol unchanged) | not run (004 protocol unchanged) | 3/3 |

† B-loop-only 001 rep-2 is the batch's one **`truncated-generation`** row: the repair call hit the token ceiling (`repair_finish_reason: "length"`) with an **empty** content channel — the empty file vacuously satisfies the checker (`ok:true`, `errorCount 0`, so `repaired_clean: true` in its config) but **fails G2 structural floor** (all four required blocks missing) and is a row FAIL under the §4 truncation law. Nominal compile-clean on B-001 was 3/3; honest gate currency is 2/3. This is exactly the false-green class G2 exists to catch.

Additivity receipts (byte-level): A-vocab-only's per-task `prompt_sha256` values are **identical to the protocol run's** (001 `bef6b3f9…`, 002 `e3c0d4db…`, 003 `8e931502…` — same composed prompt with the vocabulary appended); B-loop-only's are **identical to the 07-16 zero-shot baseline's** (001 `12eb75f3…`, 002 `6831dae4…`, 003 `ebc5b563…` — untouched prompts). Each variant isolates exactly one intervention.

## Environment + single-slot receipts

- **Served seat:** `qwen36-workhorse` on llama-swap `:9000` (`-np 1`, single slot). `/running` server line (unchanged from the 07-16 baseline run): `llama-server --port 5816 --model /opt/llama-swap/models/qwen36-35b/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf --alias qwen36-workhorse --ctx-size 131072 --batch-size 2048 --ubatch-size 2048 --threads 16 -ngl 999 --no-mmap --flash-attn on --jinja --reasoning auto --temp 0.6 --top-p 0.95 -np 1` (request-level sampling overrode the checkpoint defaults with the frozen pins temp 0.3 / top_p 0.9 / max_tokens 16384).
- **Single-slot law (§4, per rep):** before every seat call the runner probed `GET http://127.0.0.1:9000/running` and required alias `qwen36-workhorse` in state `ready`; every probe returned `ok:true` — recorded in each `config.json → single_slot_probe` for **all 30 rep dirs of this batch** (12 protocol + 9 A + 9 B). Calls strictly sequential, one bounded call in flight (the repair call, where fired, is the same rep's single bounded follow-up); nothing else drove the slot.
- **Batch volume:** 30 graded rep dirs; **39 seat generations total** (protocol 12 first-attempt + 2 repair; A-vocab-only 9; B-loop-only 9 first-attempt + 7 repair). Protocol-run wall ≈ 21 min of generation (1123 s first-attempt + 137 s repair).
- **Runner:** `harness/run_dcl_heldout.py --freeze-commit 8d2d6762… --refreeze-commit 8a3b9d18…` with `--vocab-ref harness/dcl/vocab-reference.md --repair-loop` on 001/002/003 and **no protocol flags** on 004. Per-rep `config.json` carries model, endpoint, sampling, `prompt_sha256` (system `419e455b…` + per-task user sha), freeze + refreeze shas, `wall_time` (+ `repair_wall_time` where fired), `usage`, `finish_reason` (+ `repair_finish_reason`), `vocab_ref` {path, sha256}, `repair_loop`, `zero_shot_clean`/`repaired_clean`, `attempts`, single-slot receipt.
- **Artifact integrity:** `response.dcl` byte-identical to the final attempt's `choices[0].message.content` (from `raw-response.json`, or `raw-response-2.json` where the loop fired) in **all 30 rep dirs**. No `ABORTED.json` anywhere in the batch.
- **node / vendored checker:** `node v24.15.0`; `sha256sum -c harness/dcl/bin/SHA256SUMS` → all OK (`dcl.wasm`, `wasm_exec.js`, `LICENSE`, `NOTICE`).

## Build-time calibration baseline (measured, §7 — unchanged from the 07-16 record)

| Item | Method | Result |
|---|---|---|
| Oracle catchability | each `solution/` oracle graded via the integrity battery | 4/4 tasks PASS their own gate on a bare run (`tests/test_dcl_verifier_integrity.py` 29 passed) |
| Compile-fail demo | each per-task `broken_fixture` / `broken_input` | FAIL exactly the compile gate (`broken_fixture_is_rejected` / `broken_input_is_rejected` passed every rep-battery run) |
| Semantic-preservation demo | `-004` preservation floor | `repair_preserves_declared_semantics` PASSED all 3 repair reps |
| Good-fixture demo | tricky-but-clean files per task | integrity battery green |
| Data point 1 (recorded) | the spike seat's finished attempt (`SEAT-RESULT.md`) | compile FAIL, `errorCount 2` (invented `machine` / `in_memory`) — the anecdote the suite generalised at baseline; **the §10 protocol is the pre-registered disposition of that finding, now measured** |

## INVALID reps

**None.** No rep aborted on transport; no `ABORTED.json` was written anywhere under this run root or the variant roots; no re-run-in-place was needed.

## Honest notes

**1. Inside the protocol, the vocabulary did most of the work; the loop closed the rest.** `zero_shot_clean: true` on **7 of 9** authoring reps — with the vocabulary reference in the prompt, the first generation already compiled clean 7/9 (vs 0/9 at the 07-16 baseline). The loop FIRED on only **2 of 9** reps (002 rep-1, 002 rep-3) and repaired both to clean in one bounded pass (`repaired_clean: true`). No protocol rep needed more than the single allowed repair; none was dirty after it.

**2. What the loop fixed in the protocol run (verbatim from the persisted envelopes).** 002 rep-1 first attempt: `errorCount 3` — `DCL_PARSE_EXPECTED_DECLARATION` (L17), `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` (L23, "authentication value must be valid"), `DCL_SEM_OBSERVE_TYPE_UNSUPPORTED` (L50). 002 rep-3 first attempt: `errorCount 4` — 2× `DCL_PARSE_EXPECTED_DECLARATION` (L9–10), 2× `DCL_LEX_UNEXPECTED_CHAR` (L30, the double-quote string-literal class the baseline flagged). Notably **zero invented-enum-literal errors** (`DCL_SEM_EFFECT_KIND_UNKNOWN` etc.) anywhere in the protocol run's first attempts — the class that dominated the baseline (5/9 reps) is gone with the vocabulary in the prompt.

**3. Dirty-dirty reps: none in the protocol run; three in B-loop-only (002 rep-1/2/3), and they are the informative failures.** Without the vocabulary, the loop reduced but could not clear 002: rep-1 went `errorCount 4 → 2` by swapping illegal double-quoted literals for equally illegal single-quoted ones (`DCL_LEX_UNEXPECTED_CHAR` both times); rep-2 went `3 → 2` still emitting an invented effect kind (`computation`, `DCL_SEM_EFFECT_KIND_UNKNOWN`) plus `DCL_SEM_OUTCOME_CAUSE_REQUIRED`; rep-3 went `3 → 2` reintroducing double-quoted literals. Diagnostics alone tell the seat *where* it broke the closed grammar, not *what the legal vocabulary is* — that knowledge is exactly what the reference supplies.

**4. One `truncated-generation` row in B-loop-only (001 rep-2) — and G2 caught the vacuous pass.** The repair call finished `length` with an empty content channel; the empty file compiles vacuously clean (`ok:true, errorCount 0` — so its config records `repaired_clean: true`) but fails the structural floor with all four blocks missing. Recorded per the §4 truncation law as a row FAIL distinct from a compile failure. Two lessons worth keeping: (a) the compile-clean axis alone can be gamed by emptiness — the G2 floor is load-bearing, and any future machine-chain wiring must gate on the full battery, never the checker alone; (b) repair calls inherit the token-ceiling lesson — the reasoning channel consumed the whole 16384 budget on that call.

**5. Error codes seen in failing A-vocab-only reps (residuals the vocabulary alone leaves).** No invented-literal errors anywhere in A — the residual failures are structural/reference-shaped: `DCL_PARSE_EXPECTED_DECLARATION` (002 rep-3 ×2, 003 rep-1 ×2, 003 rep-3 ×4), `DCL_PARSE_UNEXPECTED_TOKEN` ("unexpected }", 003 rep-3), `DCL_LEX_UNEXPECTED_CHAR` (002 rep-3 ×2 — the double-quote class persisting once), and one semantic near-miss `DCL_SEM_POLICY_CONCERN_VALUE_INVALID` (002 rep-2, `errorCount 1`). These are precisely the classes a diagnostics-carrying repair pass closes — and did, in the protocol run.

**6. Known instrument limits (from the §10 re-freeze, echoed so this sheet is never over-read):** the WASM checker's language-version gate is inert; unknown FIELD TYPES pass silently in the default context (the vocabulary reference is the only guard for type discipline); `retry` requires `idempotency` on the same target; `circuit_breaker` may only govern effects. They bound what "compile-clean" proves; they change no gate.

**7. Costs, honestly:** the protocol authoring prompt is ~4.4–4.5k tokens vs ~1.3–1.4k at the zero-shot baseline (per-rep `usage.prompt_tokens`) — the vocabulary reference rides along on every authoring call — and a fired loop adds one full second call (~62–75 s, ~3.5–4.2k completion tokens here). At the measured 7/9 zero-shot-clean rate the expected cost is one call plus a ~22% chance of a second.
