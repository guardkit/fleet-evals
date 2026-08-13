# RUNBOOK: serve-candidates (register + serve eval candidate seats in llama-swap)

**Purpose:** take the llama-swap fleet on this host from its serving state to
an eval-ready state — every candidate seat in the venue's `candidates.yaml`
registered, provenance-resolved, and swappable without thrash — so a scored
fleet-evals run can generate.
**Machine:** spark (llama-swap `:9000`, `/opt/llama-swap`, ~121 GB unified
memory, ceiling 115 GB).
**OPERATOR-ONLY.** Every phase below that touches `/opt/llama-swap` (config
edits, model downloads, systemctl/service restarts, keepalive flock) is an
**operator act — Rich attended**. Build sessions and unattended agents never
execute this runbook; they only read it. Broker isolation is irrelevant here
(no NATS anywhere in this estate), but the rule still stands: no `nats://`,
no `:4222`.
**Conventions:** [`RUNBOOK-CONVENTIONS.md`](RUNBOOK-CONVENTIONS.md) (fresh
bring-up shape; gates halt; results recorded per
[`templates/RESULTS-template.md`](templates/RESULTS-template.md)).

Execution modes:

```
fresh    — first eval-ready bring-up of a venue's seats
re-run   — re-verify before a scored run; idempotent phases no-op, gates re-prove
update   — a candidates.yaml change (new seat, new checksum) → run only the affected phases
```

---

## THE THREE PINNED BLOCKERS (read before anything else)

No scored run may generate a single token until all three are resolved. They
are operator acts, not harness work, and they are stated here plainly so no
session "discovers" them mid-run:

1. **No `gemma4-base` seat and no base GGUF exist on this host.** The
   2026-05-18 run downloaded the base onto the GB10, not here. Registering it
   means a ~16 GB download (`unsloth/gemma-4-26B-A4B-it-GGUF`, `UD-Q4_K_M`),
   a new model block in `/opt/llama-swap/config/config.yaml`, and a
   llama-swap restart — **an operator act** (Phase 2).
2. **`/opt/llama-swap/models/gemma4-tutor/system-prompt.txt` does NOT exist
   on this host.** The canonical text survives only as study-tutor's
   `roles/tutor/prompts/player.md`; its pinnable, SHA'd extraction is
   `venues/study-tutor-multisubject/prompts/english.txt`
   (sha256 `998a6f1ac3d7601b75f8b4dbb82ac05bd3c8b2f87c167f78a466f3715e832104`,
   provenance in `PROMPTS-PROVENANCE.md`). Every run pins THAT file — never a
   prompt recovered from the serving host, because there is nothing there to
   recover.
3. **The served `gemma4-tutor` weights' provenance is UNVERIFIED.** Local
   file `/opt/llama-swap/models/gemma4-tutor/gemma-4-26b-a4b-it.Q4_K_M.gguf`
   has sha256
   `675424b0021ad7b78699e4bf1da404ca57c70f5c581a9ce11209fbe22b7a3144`, and its
   filename matches the BASE model's filename in the 2026-04-23 findings doc.
   HF `RichWoollcott/studytutor-gcse-26b-moe` is **safetensors+LoRA only — no
   GGUF comparator exists**, so the checksum cannot be matched against any
   published artefact. Resolution (re-quantise the merged safetensors and
   compare, or publish the original GGUF, or otherwise establish chain of
   custody) is **REQUIRED before any generation**: if the served file is
   actually the base GGUF, an eval would be base-vs-base and every "fine-tune"
   number a fiction.

---

## PINS (runbook v1, set 2026-08-07)

```
llama-swap endpoint        http://localhost:9000/v1
llama-swap config          /opt/llama-swap/config/config.yaml
gemma4-tutor GGUF          /opt/llama-swap/models/gemma4-tutor/gemma-4-26b-a4b-it.Q4_K_M.gguf
                           (ctx 32768, gemma4-tutor.jinja, ttl 0; aliases study-tutor/gcse-tutor)
gemma4-tutor sha256(local) 675424b0021ad7b78699e4bf1da404ca57c70f5c581a9ce11209fbe22b7a3144  (provenance UNVERIFIED)
base GGUF (to register)    unsloth/gemma-4-26B-A4B-it-GGUF  UD-Q4_K_M  (~16 GB — NOT ON HOST)
nearest-base-DON'T-USE     coach = gemma-4-26B-A4B-it-UD-Q4_K_XL, temp 0.1  (wrong quant for parity + wrong temp)
workhorse (Lane 7)         Qwen3.6-35B-A3B-UD-Q4_K_XL
matrix set "tutor"         preloaded default since 2026-07-26 (~37 GB pair)
full-set footprint         ~107 GB of 121; MEM_CEILING_GB 115
keepalive                  timer revives the tutor set; pause discipline = flock (documented)
```

---

## Phase 0: Recon (read-only — safe for any session)

No side effects; emits a drift report per conventions §4–5.

```bash
# 0.1 fleet is up and which seats exist
curl -s http://localhost:9000/v1/models | python3 -c "
import json,sys; ids=[m['id'] for m in json.load(sys.stdin)['data']]
print(sorted(ids))
print('PASS' if 'gemma4-tutor' in ids else 'FAIL: gemma4-tutor seat missing')"

# 0.2 blocker-1 status: does a base seat exist yet?
curl -s http://localhost:9000/v1/models | grep -q '"gemma4-base"' \
  && echo "base seat: PRESENT" || echo "base seat: ABSENT (blocker 1 open)"

# 0.3 blocker-3 status: served tutor GGUF checksum (read-only)
sha256sum /opt/llama-swap/models/gemma4-tutor/gemma-4-26b-a4b-it.Q4_K_M.gguf
#   expect 675424b0…3144; PROVENANCE REMAINS UNVERIFIED EITHER WAY (see blocker 3)

# 0.4 blocker-2 status: confirm there is no host system-prompt.txt to recover
test -f /opt/llama-swap/models/gemma4-tutor/system-prompt.txt \
  && echo "UNEXPECTED: system-prompt.txt exists — diff it against prompts/english.txt" \
  || echo "confirmed absent (pin venues/.../prompts/english.txt, blocker 2)"
```

## Phase 1: Pre-flight gates (halt on FAIL)

- **Gate 1.1 — provenance:** the venue `candidates.yaml` has a non-null,
  resolution-documented `gguf_sha256` for EVERY candidate. `provenance:
  UNVERIFIED` or `gguf_sha256: null` on any seat → **STOP** (blockers 1/3).
- **Gate 1.2 — prompt pin:** `sha256sum -c` over
  `venues/study-tutor-multisubject/prompts/` against `PROMPTS-PROVENANCE.md`
  passes (blocker 2).
- **Gate 1.3 — protocol:** the venue `PROTOCOL.md` Status is REGISTERED
  (Rich's gate tap). DRAFT → the harness will refuse anyway; stop here.
- **Gate 1.4 — memory budget:** projected resident set of ALL eval seats
  loaded together `< 115 GB` (conventions §8, memory-ceiling row). The
  gemma4 pair is ~37 GB; adding workhorse-family seats for a 4-way bake-off
  must be re-projected, not assumed.

## Phase 2: Seat registration (OPERATOR ACT — blocker 1)

For each candidate seat not yet in `/v1/models` (today: `gemma4-base`; for
the bake-off later: refresh/qwen seats when they exist):

1. Download the pinned GGUF to `/opt/llama-swap/models/<seat>/` (base:
   ~16 GB, `UD-Q4_K_M` — the same quant family as 2026-05-18, recorded as the
   honest close-not-identical parity caveat).
2. Add a model block to `/opt/llama-swap/config/config.yaml` mirroring the
   `gemma4-tutor` block: same `llama-server` binary, same ctx, `ttl 0`, and
   `--chat-template-file gemma4-tutor.jinja` for the base (its stock template
   emits `<|channel>` tokens that 500 llama-server — the 2026-05-18 execution
   caveat; record it in RESULTS).
3. Restart llama-swap (service restart — operator).
4. **Gate 2.1:** `curl -s :9000/v1/models` lists the seat; one warm-up
   completion returns 200 and its output contains no `<|channel>`.
5. Record the seat's `gguf_sha256` in the venue `candidates.yaml` in the same
   commit as this RESULTS entry.

## Phase 3: Matrix-set + keepalive eviction discipline (OPERATOR ACT)

The trap, plainly: the `tutor` matrix set (~37 GB pair) is the preloaded
default (since 2026-07-26). **Requesting any model outside the set (e.g.
`workhorse`, `coach`) EVICTS the tutor pair; the keepalive timer then revives
it.** An eval that alternates candidates across set boundaries will
load→kill→load **thrash** for the whole run.

Discipline — do BOTH where possible, and at minimum (a) or (b):

- **(a) One matrix set for all eval seats.** Add a temporary `eval` matrix
  set to config.yaml containing every candidate seat, and make it the active
  set for the run. Check the footprint against Gate 1.4 first (full current
  set is already ~107 GB of 121 — a 4-way bake-off does NOT fit alongside the
  rest of the fleet; the eval set replaces, not augments).
- **(b) Pause the keepalive while generating.** Use the documented flock
  (the same discipline as the llama-swap hot-reload gotcha set) so the timer
  cannot revive the tutor set mid-swap. **Un-pause is part of Phase 5 —
  leaving keepalive paused after the run is a fleet regression.**
- **Generation stays batched by model** (the harness already does this — all
  of candidate 1's calls, then all of candidate 2's): one swap per candidate
  per track, never per item. Per-item swapping caused cold-swap 500s on
  2026-05-18.

**Gate 3.1:** during a dry two-swap exercise (one warm-up call per seat, in
run order), llama-swap logs show exactly one load per seat and zero
keepalive-triggered reloads.

## Phase 4: Hand-off to the harness

The serving side is now eval-ready. The scored run itself is the venue
protocol's business (`uv run python -m harness.generate.run_ab_eval --venue …
--run-dir runs/…` etc.); this runbook's outputs feed the run's MANIFEST.json:
seat names, endpoints, GGUF sha256s, quant per seat, template substitutions,
matrix/keepalive state.

## Phase 5: Restore + Decision Gate

Restore the fleet: remove/deactivate the temporary `eval` matrix set, restore
the `tutor` default, un-pause keepalive (**Gate 5.1:** keepalive timer active
+ tutor set resident again).

| Gate | Check | Result |
|---|---|---|
| 1.1 | all candidates provenance-resolved (blockers 1+3 closed) | |
| 1.2 | prompt SHAs verify vs PROMPTS-PROVENANCE.md (blocker 2 pinned) | |
| 1.3 | venue PROTOCOL.md REGISTERED | |
| 1.4 | memory projection < 115 GB | |
| 2.1 | every seat serves; no `<|channel>` in warm-up output | |
| 3.1 | one load per seat; zero keepalive reloads during dry swap | |
| 5.1 | fleet restored: tutor set default, keepalive active | |

Record the run in a `RESULTS-serve-candidates-<date>.md` per the template.

## Appendix: Rollback

Remove added model blocks + the `eval` matrix set from config.yaml, restart
llama-swap, confirm `/v1/models` matches the pre-run list from Phase 0.1, and
delete downloaded GGUFs only if disk pressure demands it (a kept base GGUF
saves the next run 16 GB of download — note it in RESULTS either way).

---

## Blocker resolutions (2026-08-13, Rich attended — all three CLOSED)

1. **CLOSED** — `gemma4-base` registered: HF `unsloth/gemma-4-26B-A4B-it-GGUF`
   `UD-Q4_K_M` downloaded (sha256 verified vs upstream `f2c28b3d…f293f`), seat
   live on `:9000` via `-watch-config` hot-reload (no restart needed), Gate 2.1
   PASS (coherent warm-up, zero `<|channel>` tokens under the tutor jinja).
2. **CLOSED at seed time** — every run pins `prompts/english.txt` by sha256.
3. **CLOSED** — served-GGUF provenance PROVEN: the GB10's
   `gcse-tutor-gemma4-26b-moe-2026-04-18` quantisation is byte-identical to the
   served file (sha256 match, run by Rich on `promaxgb10-41b1`); adapter chain
   NAS↔HF also sha-proven. Details in `candidates.yaml`.

Phase 3 (matrix/keepalive discipline) remains a per-run act; Phase 1 gates are
now all passable. The venue is **eval-ready**.
