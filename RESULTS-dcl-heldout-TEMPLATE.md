# RESULTS — dcl-heldout authoring calibration gate — <candidate-id> — <date>

**Candidate:** <served alias + lineage + base/quant family, e.g. `qwen36-workhorse` = Qwen3.6-35B-A3B, UD-Q4_K_XL, llama-swap :9000 — or the D-ii/G3 fine-tune once it exists>
**Suite:** `dcl-heldout` — DCL authoring/repair, graded by the vendored DCL compiler (`harness/dcl/bin/dcl-check.mjs` + `dcl.wasm`, upstream `russelleast/Capability-Language`)
**Frozen thresholds:** `docs/research/ideas/dcl-heldout-suite-scope.md` §3, frozen at commit `8d2d6762c38ef0a3aab1c8d5904dd456e008500b`
**Scope doc (the frozen bar + sampling pins + single-slot law):** `docs/research/ideas/dcl-heldout-suite-scope.md`
**Verifier integrity at grade time:** `python3 -m pytest tests/test_dcl_verifier_integrity.py -q` → <N> passed (MUST be green before ANY grade — the three-sided proof is standing)
**Runner divergence (by design):** answer sheets produced by `harness/run_dcl_heldout.py` (ONE fresh toolless generation per rep, no system tools, no retry-on-bad-content — a bad `.dcl` is a RESULT). The runner NEVER grades; grading is the task's gate battery. Per-rep `config.json` pins: model + endpoint + sampling + `prompt_sha256` + `freeze_commit` + `wall_time` + `usage` + `finish_reason` + the single-slot probe receipt.
**Sampling pins (frozen, §4):** temperature `0.3`, max_tokens `16384`, K = `3` reps/task, fresh session per rep, `timeout_seconds = 900`.

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

A rep that truncates (`finish_reason == "length"`) is a **row FAIL recorded as `truncated-generation`** — distinct from a compile failure, never an INVALID run, never a silent skip.

---

## Per-task × per-rep grade

Grade a rep with:
`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest tasks/<task-id>/test -q`
Each cell: PASS / FAIL(test name).

| Task | Rep | G1 compile-clean | G2 structural floor | semantic-preservation (004) | finish_reason | compile-clean? | verdict |
|---|---|---|---|---|---|---|---|
| dcl-held-001-author-stats | 1 |  |  | — |  |  |  |
| dcl-held-001-author-stats | 2 |  |  | — |  |  |  |
| dcl-held-001-author-stats | 3 |  |  | — |  |  |  |
| dcl-held-002-author-version | 1 |  |  | — |  |  |  |
| dcl-held-002-author-version | 2 |  |  | — |  |  |  |
| dcl-held-002-author-version | 3 |  |  | — |  |  |  |
| dcl-held-003-author-uptime | 1 |  |  | — |  |  |  |
| dcl-held-003-author-uptime | 2 |  |  | — |  |  |  |
| dcl-held-003-author-uptime | 3 |  |  | — |  |  |  |
| dcl-held-004-repair-diagnostics | 1 |  |  |  |  |  |  |
| dcl-held-004-repair-diagnostics | 2 |  |  |  |  |  |  |
| dcl-held-004-repair-diagnostics | 3 |  |  |  |  |  |  |

**Compile-clean tally (the bar's currency):**

| Task | reps compile-clean | required | met? |
|---|---|---|---|
| dcl-held-001-author-stats | <k>/3 | ≥ 2/3 |  |
| dcl-held-002-author-version | <k>/3 | ≥ 2/3 |  |
| dcl-held-003-author-uptime | <k>/3 | ≥ 2/3 |  |
| dcl-held-004-repair-diagnostics | <k>/3 | 3/3 |  |

## §3 verdict (applied verbatim — no post-hoc adjustment)

- **Authoring bar — ≥2/3 compile-clean on 001 AND 002 AND 003:** <met / NOT met — name the failing task(s) + rep(s)>
- **Repair bar — 3/3 compile-clean on 004:** <met / NOT met — name the failing rep(s)>
- **Oracle-on-bare-run (standing, pre-grade):** <4/4 green at grade time / BLOCKED — repair the verifier, then grade>

## VERDICT: TRUSTED-TO-AUTHOR / NOT-YET

<A FAIL is a RESULT, not a problem — report it plainly. If NOT-YET: name the failing task + axis + the rep-level detail (e.g. an invented enum literal, an undeclared outcome, a truncation). The pre-registered disposition (§3) is a prompt / grammar-reference change or the D-ii/G3 fine-tune — **never** a threshold edit, **never** letting a seat author DCL in the chain on a failing sheet. A green suite is a NECESSARY gate, not a promotion by itself; it never says the DCL produced is *good* — that judgment stays human (§9).>

## Environment + single-slot receipts

- **Served seat:** <alias> on llama-swap `:9000` (`-np 1`, single slot), resolved from `/opt/llama-swap/config/config.yaml`.
- **Single-slot law (§4, per rep):** before every seat call the runner probed `GET http://127.0.0.1:9000/running` and required the alias `ready`; no `autobuild`/`feature-build`/`task-work`/orchestrator process drove the slot; calls strictly sequential, one bounded call in flight. Per-rep receipt: `<rep-dir>/config.json` → `single_slot_probe`.
- **Runner:** `harness/run_dcl_heldout.py --freeze-commit 8d2d6762c38ef0a3aab1c8d5904dd456e008500b` (per-rep `config.json` carries model, endpoint, sampling, `prompt_sha256`, `freeze_commit`, `wall_time`, `usage`, `finish_reason`).
- **node / vendored checker:** `node <version>`; `sha256sum -c` over `harness/dcl/bin/SHA256SUMS` green; checker byte-identical to `spike/dcl-authoring/bin/`.

## Build-time calibration baseline (measured at build, §7 — not estimated)

| Item | Method | Result |
|---|---|---|
| Oracle catchability | each `solution/` oracle graded as an answer sheet | <4/4 tasks PASS their own gate on a bare run> |
| Compile-fail demo | each `broken_fixtures/<task>` (incl. the seat near-miss `machine`/`in_memory` class) | <FAIL exactly the compile gate, `ok:false`, errors line-located> |
| Semantic-preservation demo | a `-004` fixture that "repairs" by dropping/renaming a declared name | <FAILS the preservation floor, passes compile alone> |
| Good-fixture demo | tricky-but-clean files per task | <PASS the whole battery> |
| Data point 1 (recorded) | the spike seat's finished attempt (`SEAT-RESULT.md`) | compile FAIL, `errorCount 2` (invented `machine` / `in_memory`) — the anecdote this suite generalises |

<If any recorded value changes on re-measurement, that is a defect to investigate, not a number to silently update (§7).>

## INVALID reps

<Any aborted rep (transport `ABORTED.json`) is re-run in place under the same pinned config — never skipped, never graded partial. List re-run evidence here.>

## Honest notes

<Root-cause notes for any failure; the exact compiler diagnostics (code, line) for a compile FAIL; anything that should become a new broken fixture (`tests/broken_fixtures/dcl-held-*/` — floors never shrink, every wild machine-chain catch joins the corpus). A FAIL verdict against the frozen bar is a RESULT, reported plainly.>
