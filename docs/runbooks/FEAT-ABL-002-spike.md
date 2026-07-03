# FEAT-ABL-002 — Harbor spike runbook (2026-07-03)

**Verdict: HARBOR VIABLE — ADOPTED.** No fallback needed. All four proof
points landed inside the 1-day timebox (~1.5 h wall-clock from install to
scored rollout). Acceptance per `phase-ablation-scope.md` §4 / §8.1 met
verbatim: one task, one rollout, one reward score, on the GB10.

| Proof point (build-plan Step 0) | Result | Evidence |
|---|---|---|
| 1. `pip install harbor` + sample task end-to-end, Docker env | ✅ harbor 0.17.0, aarch64 wheels only, no compiles; sample oracle rollout reward **1.0** in 29 s | `spike/rollouts/sample-oracle-1/` |
| 2. ARM64 task image, repo pinned via `git archive` | ✅ `abl-spike-001:pin`, `arch=arm64`, 600 MB, built natively on aarch64 | `tasks/abl-spike-001-task-status-json/environment/` |
| 3. Container→host llama-swap route | ✅ HTTP 200 from inside the task container — both bare (Tailscale MagicDNS) and with `--add-host promaxgb10-41b1:host-gateway`; `/v1/models` served through the same route | §Networking below |
| 4. One rollout, reward collected | ✅ Harbor oracle rollout on the spike task: **reward 1.0**, 13 s (cached image) | `spike/rollouts/abl-spike-oracle-1/` |
| (stretch) real-model rollout via llama-swap | see §Model rollout | `spike/rollouts/abl-spike-model-1/` |

## Where it actually ran — Spark B deviation

The build plan targeted **Spark B** (`spark-fcf6`) via an SSH alias `Spark`.
From this GB10 session there is **no working credential path to Spark B**: no
`~/.ssh/config` alias, no ssh-agent, Tailscale SSH not enabled on the target,
and the only on-disk key (`fleet_memory_nas_ed25519`) is refused
(`Permission denied (publickey,password)`). The earlier "BatchMode key auth
works" verification evidently ran from a different machine. Installing a key
non-interactively was not possible.

**Resolution:** the spike ran on **Spark A — the GB10 itself**
(`promaxgb10-41b1`, aarch64, Docker 29.2.1). Scope §4's acceptance literally
reads "on the GB10", so this satisfies the letter of the gate; the Spark-B
preference was only contention mitigation, and the GPU was idle (PO pilot
between runs, load 0.45) for the entire spike. Same arch, same Docker major
version — no portability delta expected. **Follow-up for ABL-006:** provision
key auth GB10→Spark B (or run rollouts from a host that has it) before the
60-rollout run.

## Install steps (proof 1)

```bash
python3 -m venv ~/harbor-venv
~/harbor-venv/bin/pip install harbor        # 0.17.0, ~2 min
# sample task:
~/harbor-venv/bin/harbor init -t sample-hello --org ablspike
# fill instruction.md / solution/solve.sh / tests/test_outputs.py, then:
~/harbor-venv/bin/harbor run -p sample-hello -a oracle -o jobs -n 1 -q -y
# → Mean 1.000, 1 trial, 0 exceptions, 29 s
```

ARM64 friction: **none.** Every dependency (pydantic-core, pyarrow, xxhash,
tiktoken, …) shipped aarch64 manylinux wheels; nothing compiled from source.
`python:3.12-slim-bookworm` is multi-arch and builds arm64 natively on the
GB10 — no cross-build, no emulation.

## The frozen task-folder contract

Harbor 0.17's on-disk task anatomy, now the contract ABL-003/004 build
against (one correction vs the scope §3.2 sketch — **`tests/` is plural**,
not `test/`):

```
tasks/<task-id>/
├── task.toml          # schema_version "1.3"; [task] name = "org/name";
│                      # [metadata] free-form — suite = "ablation-spike" lives here
├── instruction.md     # the FEAT's original spec text
├── environment/       # Dockerfile + build context (pinned-repo tarball)
├── tests/             # test.sh + test_outputs.py — copied to /tests/ and run
│                      # IN the environment; writes /logs/verifier/reward.txt (1|0)
└── solution/          # solve.sh (+ patch) — oracle uploads the WHOLE dir and
                       # executes solve.sh inside the environment
```

- **Reward** = whatever `tests/test.sh` writes to `/logs/verifier/reward.txt`.
  Binary here (PyTest suite exit code), per scope §3.5.
- The verifier runs **inside the environment container**: preinstall pytest in
  the image so verification is offline (the scaffold's default test.sh
  downloads `uv` from the network every run — replaced).
- The oracle agent uploads the whole `solution/` dir, so a landed-diff `.patch`
  file next to `solve.sh` works (`git apply` from `solve.sh`).

## The spike task: `tasks/abl-spike-001-task-status-json/`

Re-implements guardkit **FEAT-9DDE** (`/task-status --json` producer +
wiring), per build-plan Appendix A row 1:

- **Environment:** guardkit pinned at pre-FEAT `3450f602c` via
  `git archive` → tarball (107 MB, sha256 pinned in
  `environment/CONTEXT.sha256`, tarball itself **gitignored** — regenerate
  with `environment/prepare_context.sh`; fleet-evals is public, the guardkit
  snapshot is not committed here). Image: `python:3.12-slim-bookworm` + git,
  curl, pytest, pyyaml; `git init` + baseline commit so the agent gets a
  clean repo at the pin.
- **Instruction:** composed verbatim from the FEAT-9DDE spec sources
  (`.guardkit/features/FEAT-9DDE.yaml`, TASK-TSJ-001/002).
- **Verifier:** 7 independent PyTests authored from the **landed** diff
  (schema-v1 key order, kanban sort, summary counts, parse_error degradation,
  single-task null-filling + byte-stability, exit-1-with-stderr, bin-entry +
  spec wiring). Hermetic: synthetic task trees under `tmp_path`, producer
  invoked as a subprocess.
- **Solution:** landed diff `3450f602c..f9c4070be` restricted to the
  behaviour-bearing paths (producer, bin-entries, both command specs, the two
  landed test files), applied by `solve.sh`.
- **Oracle-validation gate (scope §3.2):**
  - RED: pristine pin → **7/7 FAIL** (no vacuous pass possible)
  - GREEN: solution applied → **7/7 PASS**
- Discovery safety: the frozen PO held-out gates only glob `po-held-*` /
  `suite == "po-heldout"`; the spike task is invisible to them.
  Re-verified after authoring: `python3 -m pytest tests/ -q` → **33/33 green**.

## Networking proof (proof 3)

From inside the task container on the GB10:

```
docker run --rm abl-spike-001:pin \
  curl -s -w "%{http_code}" http://promaxgb10-41b1:9000/health   # → 200
docker run --rm --add-host promaxgb10-41b1:host-gateway abl-spike-001:pin \
  curl -s -w "%{http_code}" http://promaxgb10-41b1:9000/health   # → 200
# /v1/models returns the full model list through the same route.
```

Surprise: the bare-DNS case **works on this host** — containers inherit the
host's resolv.conf, which points at Tailscale MagicDNS, which resolves
`promaxgb10-41b1` to its tailnet IP (the host's own `/etc/hosts` 127.0.0.1
mapping is not consulted). The `--add-host …:host-gateway` form is the
**portable** route (works without Tailscale DNS) and is what ABL-003 should
bake in — via Harbor's `--extra-docker-compose` overlay (`extra_hosts:`) for
in-container agents.

## Rollouts (proof 4)

| Job | Agent / model | Reward | Runtime | Artifacts |
|---|---|---|---|---|
| `sample-oracle-1` | oracle | **1.0** | 29 s | `spike/rollouts/sample-oracle-1/` |
| `abl-spike-oracle-1` | oracle | **1.0** | 13 s | `spike/rollouts/abl-spike-oracle-1/` |
| `abl-spike-model-1` | terminus-2 · `openai/qwen3-coder-30b` via llama-swap (`api_base=http://promaxgb10-41b1:9000/v1`), max_turns 20 | **0.0** (6/7 tests passed — near miss) | 5 min 26 s | `spike/rollouts/abl-spike-model-1/` |

```bash
# oracle (the acceptance rollout):
~/harbor-venv/bin/harbor run -p tasks/abl-spike-001-task-status-json \
  -a oracle -o ~/harbor-spike/jobs --job-name abl-spike-oracle-1 -n 1 -q -y

# real-model rollout through llama-swap (host-side agent; OPENAI_API_KEY must
# be set to anything non-empty for litellm):
OPENAI_API_KEY=dummy ~/harbor-venv/bin/harbor run \
  -p tasks/abl-spike-001-task-status-json \
  -a terminus-2 -m openai/qwen3-coder-30b \
  --ak api_base=http://promaxgb10-41b1:9000/v1 --ak max_turns=20 \
  -o ~/harbor-spike/jobs --job-name abl-spike-model-1 -n 1 -q -y
```

The model rollout used the same Player model (qwen3-coder-30b) as the
original FEAT-9DDE autobuild. In 20 turns it implemented the producer and the
bin-entry registration correctly — **6/7 verifier tests passed**, failing only
`test_command_specs_wired` (one of the two `--json` spec edits missing), so
the binary reward is 0.0. A real, scored, near-miss rollout through the full
pipeline: exactly the shape of datapoint the ablation grades. Full per-turn
trajectory and terminal recording are in the job dir (`trajectory.json`,
`recording.cast`; evidence copies in `spike/rollouts/abl-spike-model-1/`).

## Gotchas (in discovery order)

1. **`task.toml` `authors` must be objects** —
   `authors = [{ name = "...", email = "..." }]`, not strings. A pydantic
   validation failure here makes Harbor **silently** treat the task dir as an
   empty dataset → `ValueError: Either datasets or tasks must be provided.`
   Debug with `TaskConfig.model_validate_toml(...)` /
   `Task.is_valid_dir(dir)` from `harbor.models.task.task`.
2. **`tests/` not `test/`** — scope §3.2's sketch said `test/`; Harbor's
   contract is `tests/`. Contract frozen as `tests/`.
3. **Scaffold test.sh fetches uv from the network at verify time** — replace
   with preinstalled pytest for offline, deterministic verification.
4. **GB10 `/etc/hosts` maps `promaxgb10-41b1` → 127.0.0.1** — harmless for
   containers (they don't read the host's hosts file) and for host-side
   agents (llama-swap listens on `:9000` all-interfaces), but remember it
   when reasoning about name resolution on this box.
5. **`OPENAI_API_KEY` must be set (any value)** for litellm-backed agents
   against llama-swap's OpenAI-compatible endpoint.
6. **Job dirs are heavyweight** (trajectories, recordings, image locks) —
   keep `-o` outside the repo (`~/harbor-spike/jobs`) and copy only the small
   evidence files (`result.json`, `reward.txt`, `pytest.log`) into
   `spike/rollouts/`.

## Timings

| Step | Wall clock |
|---|---|
| venv + `pip install harbor` (aarch64) | ~2 min |
| sample task e2e (build ubuntu env + oracle + verify) | 29 s |
| `git archive` context (107 MB) | ~10 s |
| spike image build (native arm64) | ~2 min |
| RED/GREEN oracle gates (docker run) | < 1 s each |
| Harbor oracle rollout (cached image) | 13 s |
| terminus-2 + qwen3-coder-30b rollout (20 turns, incl. llama-swap model load) | 5 min 26 s |

## Harbor vs fallback — decision

**Harbor adopted.** The pre-declared fallback (harness-native runner on the
same contract) was never triggered: the only failure in the whole spike was
the `authors` TOML typing (5-minute fix), everything else worked first try on
aarch64. The fallback remains documented in the build plan should Harbor
regress, and the corpus stays Harbor-portable by construction either way.

## Follow-ups feeding ABL-003/004/006

- ABL-003 (AutoBuild adapter): guardkit autobuild runs **inside** the task
  container → needs the P4 env contract vars via `[environment.env]` /
  `--ae`, and the `extra_hosts` compose overlay for the llama-swap route.
  Custom agent path: Harbor accepts `module.path:ClassName` for `-a`.
- ABL-004 (corpus ×10): `prepare_context.sh` + `CONTEXT.sha256` +
  gitignored tarball is the packaging pattern for every pinned-repo task.
- ABL-006: provision GB10→Spark B key auth, or accept Spark A execution
  (contention risk returns when the 82 h run starts).
- `harbor run -k 3` gives K=3 attempts per trial natively — maps directly to
  scope §3.4's repetition policy.
