# fleet-evals — read this first

**This repo is the factory's judging estate**: the ruled venue system for
multi-subject model evaluation — pre-registered protocols, blinded n-way
judging, immutable runs with manifests. It was seeded from study-tutor's
`scripts/eval/` harness (2026-05-18 base-vs-finetune eval) and generalised
per the Lane 1 design pin.

**Consumers of this estate:**

- **study-tutor** (`~/Projects/appmilla_github/study-tutor`) — the
  multi-subject tutor validation (English golden set, the 17-prompt probes
  with the Chemistry labeling defect to re-run, base-vs-finetune re-runs).
  study-tutor is READ-ONLY input to this repo: copy from it, never write.
- **The software factory** (ai-transition's software-factory mission/plan
  pair) — model bake-offs (e.g. Lane 7 workhorse candidates) run as n-way
  venues here.

**FLAG — no GitHub repo yet.** This repo is LOCAL-ONLY by rule: creating a
GitHub repo for it is flagged to Rich and is his call. Never `git remote
add`, never push, never create a remote.

Standing rules a session must hold:

- **Pre-registration is code-enforced.** A venue with no `PROTOCOL.md` — or
  one whose Status line is still DRAFT — cannot start a run
  (`harness/common.py::require_protocol`). The DRAFT → REGISTERED flip is
  Rich's gate tap, not a session's. Do not "just this once" around it.
  Ground rules ADR: `docs/decisions/ADR-EVAL-001-blinding-and-preregistration.md`.
- **Runs are immutable evidence** — `runs/<run>/` is append-only history
  with a `MANIFEST.json`; corrections are new runs.
- **Broker isolation:** never connect to any NATS broker (no `nats://`, no
  `:4222`).
- **Hermetic tests:** `uv run pytest` must pass offline (no network beyond
  package installs). Model inference (llama-swap `:9000`, Anthropic API) is
  strictly an attended, scored-run activity — never part of a build or a
  test.
- **Never touch `/opt/llama-swap`** (no config edits, model downloads, or
  systemctl) — serving-side changes are operator acts.

Layout: `harness/` (the pipeline: generate → deterministic score → blind
judge → resolve → aggregate, + multi-turn + criterion tracks, + rubrics),
`venues/` (one dir per pre-registered venue), `runs/` (immutable evidence),
`runbooks/` (inherited conventions + templates), `tests/` (golden-master
tests against the 2026-05-18 fixtures).

House conventions inherited: `runbooks/RUNBOOK-CONVENTIONS.md` (from
dgx-spark) and `runbooks/templates/RESULTS-template.md` (from study-tutor).
