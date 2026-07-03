# AutoBuild agent adapter — FEAT-ABL-003 (skeleton)

A Harbor custom agent that runs `guardkit autobuild` **inside** a task
environment container under the P4 fleet-memory env contract, collects the
retrieval log + config hash, lets Harbor's verifier produce the reward
(frozen ABL-002 task-folder contract), and emits per-rollout JSON
`{task, arm, rep, reward, retrieval_items, config_hash, wallclock, tokens}`.

Local only per DF-001 — nothing here performs cloud tracking.

## Files

| File | Role |
|---|---|
| `autobuild_agent.py` | `AutoBuildAgent` — Harbor `BaseAgent` (setup + run): env injection, in-container exec, artifact collection |
| `rollout_record.py` | Per-rollout JSON emission from Harbor trial/job dirs (CLI: `python3 -m adapter.rollout_record`) |
| `compose/llama-swap-extra-hosts.yaml` | `--extra-docker-compose` overlay baking in the portable container→host llama-swap route (`host-gateway`) |
| `smoke/smoke_command.sh` | Trivial stand-in for `guardkit autobuild` used by the smoke test |

## Invocation

Run from the fleet-evals repo root. `PYTHONPATH=$PWD` is required — Harbor
imports the agent via `importlib` (`module.path:ClassName`) and the console
script does not put the cwd on `sys.path`.

Real form (once FEAT-ABL-001 has landed in guardkit and the task image ships
guardkit; models pinned at the §5 freeze):

```bash
PYTHONPATH=$PWD ~/harbor-venv/bin/harbor run \
  -p tasks/<task-id> \
  -a adapter.autobuild_agent:AutoBuildAgent \
  --ak arm=off \                                  # or: --ak arm=fixture:v1
  --ak pg_dsn='postgresql://...fixture DSN...' \
  --ak feature_id=FEAT-XXXX \
  --ak coach_model=<pinned> --ak player_model=<pinned> \
  --extra-docker-compose adapter/compose/llama-swap-extra-hosts.yaml \
  -o ~/harbor-ablation/jobs --job-name <task>-<arm>-<n> -n 1 -k 3 -q -y
```

Then emit the per-rollout JSON (one line per trial; reps numbered per
(task, arm) in `started_at` order, matching `-k`):

```bash
python3 -m adapter.rollout_record ~/harbor-ablation/jobs/<job-name> -o rollouts.jsonl
```

### Agent kwargs (`--ak key=value`)

| kwarg | default | meaning |
|---|---|---|
| `arm` | `off` | `off`, `fixture:<id>`, or `on` (+`fixture_id`) → `FLEET_MEMORY_RETRIEVAL` |
| `fixture_id` | — | with `arm=on`, becomes `fixture:<id>` |
| `pg_dsn` | — | **required** (P4: explicit); fixture DSN, or via `--ae FLEET_MEMORY_PG_DSN=...` |
| `embed_model` / `embed_dims` | `nomic-embed-text-v1.5` / `768` | P4 pins (guardkit defaults `"embed"`/1024 would silently degrade the on-arm) |
| `feature_id` | — | feature id for the default `guardkit autobuild` command |
| `coach_model` / `player_model` | — / `-m` value | pinned models for the default command |
| `command` | guardkit autobuild template | full override, taken literally; `command=@<host path>` uploads that script and runs it via bash |
| `workdir` | container `WORKDIR` | cwd for the command |
| `retrieval_log_src` | `/app/.guardkit/logs/retrieval.jsonl` | in-container retrieval-log path (SEAM — see below) |
| `solution_dir` | — | debug/smoke helper: host dir uploaded to `/solution` before the command runs |
| `timeout_sec` | task agent timeout | per-exec timeout for the command |

### Artifacts per trial (`<trial>/agent/`)

- `autobuild.log` — full stdout+stderr of the in-container command
- `fleet-memory-env.txt` — proof-of-injection probe: `FLEET_MEMORY_*` exactly as the command saw them (DSN redacted)
- `retrieval.jsonl` — retrieval log copied from `retrieval_log_src` (absent until ABL-001)
- `rollout-config.json` + `rollout-meta.json` — redacted rollout config (its sha256 is the config hash) and run metadata (arm, config_hash, exit_code, wallclock_sec)
- `instruction.md` — the instruction the rollout was given

## What works today (smoke test, recorded 2026-07-03)

The adapter's exec + env-injection + artifact-collection path is proven
end-to-end through `harbor run` against the ABL-002 spike task, with
`smoke/smoke_command.sh` standing in for `guardkit autobuild` (it applies the
task's oracle patch and writes an ABL-001-shaped fake retrieval log at the
seam path):

```bash
PYTHONPATH=$PWD ~/harbor-venv/bin/harbor run \
  -p /home/richardwoollcott/Projects/appmilla_github/fleet-evals/tasks/abl-spike-001-task-status-json \
  -a adapter.autobuild_agent:AutoBuildAgent \
  --ak arm=off \
  --ak pg_dsn=postgresql://smoke:smoke@localhost:5432/fixture_smoke \
  --ak solution_dir=/home/richardwoollcott/Projects/appmilla_github/fleet-evals/tasks/abl-spike-001-task-status-json/solution \
  --ak command=@$PWD/adapter/smoke/smoke_command.sh \
  -o ~/harbor-spike/jobs --job-name abl003-adapter-smoke-1 -n 1 -q -y
```

Observed result: **reward 1.0** (verifier 7/7), 1 trial, 0 exceptions, 14 s
total runtime. `fleet-memory-env.txt` showed all five contract vars injected;
`retrieval.jsonl` was collected from the seam path; and

```bash
python3 -m adapter.rollout_record ~/harbor-spike/jobs/abl003-adapter-smoke-1
```

emitted:

```json
{"task": "fleet-evals/abl-spike-001-task-status-json", "arm": "off", "rep": 1, "reward": 1.0, "retrieval_items": 2, "config_hash": "e4c33d696f75b17b07a82b48ced06272c05db57d020d985f0a10314a38c6ce35", "wallclock": 0.092, "tokens": null}
```

(The task's `environment/` build-context tarball is gitignored — regenerate
with `environment/prepare_context.sh` or point `-p` at a checkout that has it.)

## SEAMS — blocked on FEAT-ABL-001 (guardkit)

The `FLEET_MEMORY_RETRIEVAL` gate and the `items:[{id,score}]` retrieval log
**do not exist in guardkit yet**. The adapter already produces/consumes both
sides of the seam; exact touchpoints to revisit when ABL-001 lands:

1. **Arm gate** — the adapter injects `FLEET_MEMORY_RETRIEVAL`
   (`autobuild_agent.py::build_env_contract`) on every exec; guardkit ignores
   it until the gate lands in
   `guardkit/knowledge/fleet_memory_client.py::_load_fleet_config_from_env`
   (~:620) and the arm gate inside `search()` (~:302-316). **No adapter change
   expected** — the env var already flows; verify end-to-end behaviour only.
2. **Retrieval log path** — the adapter collects from
   `autobuild_agent.py::DEFAULT_RETRIEVAL_LOG_SRC`
   (`/app/.guardkit/logs/retrieval.jsonl`), an **assumed** location. Confirm
   the real path/filename that ABL-001's `query_logger.py` writes and update
   the constant (or pass `--ak retrieval_log_src=...`).
3. **Retrieval log schema** — `rollout_record.py::count_retrieval_items`
   parses JSONL lines with `items: [{id, score}]`. Confirm against ABL-001's
   landed schema. Absent log → `retrieval_items: null` (distinct from `0`,
   which the ABL-006 validity guardrail — ≥1 item per on-arm rollout — relies
   on).
4. **Tokens** — `tokens` is `null`: guardkit autobuild emits no
   machine-readable usage yet. Touchpoints: end of
   `autobuild_agent.py::AutoBuildAgent.run` (populate
   `context.n_input_tokens/n_cache_tokens/n_output_tokens` from whatever
   usage artifact guardkit grows) and `rollout_record.py::_tokens`
   (passthrough already in place).
5. **Task images with guardkit** — the default command assumes `guardkit` is
   on PATH inside the task image; the ABL-004 corpus packaging must install
   it (the spike image only contains the pinned target repo). Pinned
   `coach_model`/`player_model` values are set per-run until the §5 freeze.
