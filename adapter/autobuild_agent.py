"""AutoBuildAgent — Harbor custom agent for the phase-ablation study (FEAT-ABL-003).

Given a Harbor task environment, this agent:

1. Applies the **P4 env contract** plus arm selection (``FLEET_MEMORY_RETRIEVAL``)
   into the environment for every command it runs.
2. Executes ``guardkit autobuild <feature> --coach-model <pinned> --model <pinned>``
   **inside** the environment container (the command is configurable via
   ``--ak command=...`` so the exec path can be exercised before ABL-001 lands).
3. Copies out the retrieval log and writes the rollout config + config hash.
4. Leaves the reward to Harbor's verifier (``tests/test.sh`` →
   ``/logs/verifier/reward.txt``), per the frozen ABL-002 task-folder contract.

Per-rollout JSON emission is a separate, post-hoc step: see
``adapter/rollout_record.py``.

Local-only per DF-001: no cloud tracking anywhere on this path.

Invocation (from the fleet-evals repo root, so ``adapter`` is importable)::

    PYTHONPATH=$PWD ~/harbor-venv/bin/harbor run \
      -p tasks/<task-id> \
      -a adapter.autobuild_agent:AutoBuildAgent \
      --ak arm=off \
      --ak pg_dsn=postgresql://... \
      --ak feature_id=FEAT-XXXX \
      --ak coach_model=<pinned> --ak player_model=<pinned> \
      -o ~/harbor-ablation/jobs -n 1

Agent kwargs (``--ak key=value``) are documented in ``adapter/README.md``.

SEAMS — blocked on FEAT-ABL-001 (marked ``SEAM(ABL-001)`` inline):
guardkit does not yet implement the ``FLEET_MEMORY_RETRIEVAL`` gate nor the
``items:[{id,score}]`` retrieval log. This adapter already injects the env var
and already collects the log from ``DEFAULT_RETRIEVAL_LOG_SRC``; both become
meaningful once ABL-001 lands in guardkit.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext
from harbor.models.trial.paths import EnvironmentPaths

ADAPTER_VERSION = "0.1.0"

# --- P4 env contract (phase-ablation-build-plan.md, Prerequisite P4) ---------
# These MUST be set explicitly on every rollout: guardkit's fleet-memory
# client defaults ("embed", 1024) do not match the live store and would
# silently degrade the on-arm.
P4_EMBED_MODEL = "nomic-embed-text-v1.5"
P4_EMBED_DIMS = "768"

# SEAM(ABL-001): guardkit does not yet emit a retrieval log. This is the
# adapter's assumed in-container location for the ``items:[{id,score}]``
# JSONL that FEAT-ABL-001 will add (guardkit/knowledge/query_logger.py).
# Confirm/adjust this path when ABL-001 lands. Overridable via
# ``--ak retrieval_log_src=...``.
DEFAULT_RETRIEVAL_LOG_SRC = "/app/.guardkit/logs/retrieval.jsonl"

# Default command template. Placeholders are only substituted for THIS
# template (a user-supplied ``--ak command=...`` is taken literally, since
# arbitrary shell text may contain braces).
DEFAULT_COMMAND_TEMPLATE = (
    "guardkit autobuild {feature_id}"
    " --coach-model {coach_model} --model {player_model}"
)

# In-container artifact names (under /logs/agent, mounted from the trial's
# agent/ dir by Harbor's Docker environment).
AUTOBUILD_LOG_NAME = "autobuild.log"
RETRIEVAL_LOG_NAME = "retrieval.jsonl"
ENV_PROBE_NAME = "fleet-memory-env.txt"
COMMAND_SCRIPT_NAME = "adapter-command.sh"
ROLLOUT_META_NAME = "rollout-meta.json"
CONFIG_NAME = "rollout-config.json"

_DSN_CREDENTIALS_RE = re.compile(r"://([^:/@]+):([^@]+)@")


def redact_dsn(dsn: str) -> str:
    """Redact the password component of a URL-style DSN for on-disk records."""
    return _DSN_CREDENTIALS_RE.sub(r"://\1:<redacted>@", dsn)


def resolve_arm(arm: str, fixture_id: str | None) -> str:
    """Map the ``arm`` kwarg to a ``FLEET_MEMORY_RETRIEVAL`` value.

    Accepted forms:
      - ``off``            → ``off``
      - ``fixture:<id>``   → passed through as-is
      - ``on``             → ``fixture:<fixture_id>`` (requires ``fixture_id``)
    """
    if arm == "off":
        return "off"
    if arm.startswith("fixture:") and len(arm) > len("fixture:"):
        return arm
    if arm == "on":
        if not fixture_id:
            raise ValueError(
                "arm=on requires --ak fixture_id=<id> "
                "(becomes FLEET_MEMORY_RETRIEVAL=fixture:<id>)"
            )
        return f"fixture:{fixture_id}"
    raise ValueError(
        f"Invalid arm {arm!r}: expected 'off', 'on' (+fixture_id) or 'fixture:<id>'"
    )


def build_env_contract(
    *,
    retrieval: str,
    pg_dsn: str,
    embed_model: str = P4_EMBED_MODEL,
    embed_dims: str = P4_EMBED_DIMS,
) -> dict[str, str]:
    """The P4 env contract + arm selection, applied to every in-container exec.

    All four P4 vars are always explicit — including on the off-arm, where
    FLEET_MEMORY_ENABLED stays ``true`` so the retrieval *gate* (not the
    loader) is the only difference between arms. SEAM(ABL-001): guardkit
    ignores FLEET_MEMORY_RETRIEVAL until the gate lands in
    fleet_memory_client.py:_load_fleet_config_from_env / search().
    """
    return {
        "FLEET_MEMORY_ENABLED": "true",
        "FLEET_MEMORY_PG_DSN": str(pg_dsn),
        "FLEET_MEMORY_EMBED_MODEL": str(embed_model),
        "FLEET_MEMORY_EMBED_DIMS": str(embed_dims),
        "FLEET_MEMORY_RETRIEVAL": str(retrieval),
    }


def compute_config_hash(config: dict[str, Any]) -> str:
    """sha256 over the canonical (sorted-keys) JSON of the redacted config."""
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AutoBuildAgent(BaseAgent):
    """Runs guardkit autobuild inside the task container under the P4 contract."""

    @staticmethod
    def name() -> str:
        return "autobuild-adapter"

    def version(self) -> str:
        return ADAPTER_VERSION

    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        *,
        arm: str = "off",
        fixture_id: str | None = None,
        pg_dsn: str | None = None,
        embed_model: str = P4_EMBED_MODEL,
        embed_dims: str | int = P4_EMBED_DIMS,
        feature_id: str | None = None,
        coach_model: str | None = None,
        player_model: str | None = None,
        command: str | None = None,
        workdir: str | None = None,
        retrieval_log_src: str = DEFAULT_RETRIEVAL_LOG_SRC,
        solution_dir: str | None = None,
        timeout_sec: int | float | None = None,
        **kwargs,
    ):
        super().__init__(logs_dir=logs_dir, model_name=model_name, **kwargs)

        # Fail fast on structural misconfiguration (P4 requires explicitness).
        self._retrieval = resolve_arm(str(arm), fixture_id)
        self._arm = str(arm)
        dsn = pg_dsn or self._extra_env.get("FLEET_MEMORY_PG_DSN")
        if not dsn:
            raise ValueError(
                "P4 env contract: the fixture DSN must be explicit. "
                "Pass --ak pg_dsn=postgresql://... or --ae FLEET_MEMORY_PG_DSN=..."
            )
        self._pg_dsn = str(dsn)
        self._embed_model = str(embed_model)
        self._embed_dims = str(embed_dims)

        self._feature_id = feature_id
        self._coach_model = coach_model
        # Player model falls back to Harbor's -m/--model, mirroring built-ins.
        self._player_model = player_model or model_name
        self._command = str(command) if command is not None else None
        self._workdir = workdir
        self._retrieval_log_src = str(retrieval_log_src)
        self._solution_dir = Path(solution_dir) if solution_dir else None
        self._timeout_sec = int(timeout_sec) if timeout_sec else None

        if self._solution_dir and not self._solution_dir.is_dir():
            raise ValueError(f"solution_dir does not exist: {self._solution_dir}")
        if self._command and self._command.startswith("@"):
            script = Path(self._command[1:])
            if not script.is_file():
                raise ValueError(f"command=@<path>: script not found: {script}")
            self._command_script: Path | None = script
        else:
            self._command_script = None

    # -- env contract ---------------------------------------------------------

    @property
    def env_contract(self) -> dict[str, str]:
        return build_env_contract(
            retrieval=self._retrieval,
            pg_dsn=self._pg_dsn,
            embed_model=self._embed_model,
            embed_dims=self._embed_dims,
        )

    # -- command resolution ---------------------------------------------------

    def _resolve_command(self, env_paths: EnvironmentPaths) -> str:
        if self._command_script is not None:
            return f"bash {(env_paths.agent_dir / COMMAND_SCRIPT_NAME).as_posix()}"
        if self._command is not None:
            return self._command  # taken literally; no placeholder substitution
        missing = [
            name
            for name, value in (
                ("feature_id", self._feature_id),
                ("coach_model", self._coach_model),
                ("player_model (--ak player_model or -m)", self._player_model),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Default guardkit autobuild command requires: " + ", ".join(missing)
            )
        return DEFAULT_COMMAND_TEMPLATE.format(
            feature_id=self._feature_id,
            coach_model=self._coach_model,
            player_model=self._player_model,
        )

    # -- rollout config / hash ------------------------------------------------

    def _rollout_config(self, resolved_command: str) -> dict[str, Any]:
        """Redacted, publishable rollout config. Its hash is the config hash.

        The DSN appears only as a sha256 fingerprint, so a rotated fixture DSN
        still changes the hash without any secret landing on disk.
        """
        return {
            "schema": 1,
            "adapter_version": ADAPTER_VERSION,
            "arm": self._arm,
            "fleet_memory_retrieval": self._retrieval,
            "fleet_memory_enabled": "true",
            "fleet_memory_pg_dsn_sha256": hashlib.sha256(
                self._pg_dsn.encode("utf-8")
            ).hexdigest(),
            "fleet_memory_embed_model": self._embed_model,
            "fleet_memory_embed_dims": self._embed_dims,
            "command": resolved_command,
            "coach_model": self._coach_model,
            "player_model": self._player_model,
            "workdir": self._workdir,
            "retrieval_log_src": self._retrieval_log_src,
        }

    # -- Harbor agent interface -----------------------------------------------

    async def setup(self, environment: BaseEnvironment) -> None:
        """No in-container installation: guardkit ships in the task image."""
        return

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        env_paths = EnvironmentPaths.for_os(environment.os)
        agent_dir = env_paths.agent_dir
        contract = self.env_contract

        # Host-side record of the instruction the rollout was given.
        (self.logs_dir / "instruction.md").write_text(instruction)

        # Optional debug/smoke helper: upload a solution-style dir to /solution
        # (mirrors the oracle agent) so a stand-in command can exercise the
        # exec path deterministically before ABL-001/ABL-004 land.
        if self._solution_dir is not None:
            await environment.upload_dir(
                source_dir=self._solution_dir,
                target_dir=str(env_paths.solution_dir),
            )

        # command=@<host-script> convention: upload and run via bash, avoiding
        # CLI quoting pain for multi-line commands.
        if self._command_script is not None:
            await environment.upload_file(
                source_path=self._command_script,
                target_path=str(agent_dir / COMMAND_SCRIPT_NAME),
            )

        # Proof-of-injection probe: record the FLEET_MEMORY_* env exactly as a
        # command inside the container sees it (DSN redacted — trial dirs feed
        # public evidence copies).
        probe = (
            "env | grep '^FLEET_MEMORY_' "
            "| sed 's|^\\(FLEET_MEMORY_PG_DSN=\\).*|\\1<redacted>|' "
            f"| sort > {(agent_dir / ENV_PROBE_NAME).as_posix()}"
        )
        await environment.exec(command=probe, env=contract)

        resolved_command = self._resolve_command(env_paths)
        autobuild_log = (agent_dir / AUTOBUILD_LOG_NAME).as_posix()
        wrapped = f"( {resolved_command} ) > {autobuild_log} 2>&1"

        self.logger.info(
            "AutoBuildAgent: arm=%s retrieval=%s command=%r",
            self._arm,
            self._retrieval,
            resolved_command,
        )

        started = time.monotonic()
        result = await environment.exec(
            command=wrapped,
            cwd=self._workdir,
            env=contract,
            timeout_sec=self._timeout_sec,
        )
        wallclock_sec = round(time.monotonic() - started, 3)

        # Collect the retrieval log from the guardkit-side location into the
        # mounted agent log dir. SEAM(ABL-001): the log does not exist until
        # FEAT-ABL-001 lands in guardkit; absence is tolerated (recorded).
        copy_cmd = (
            f"cp {self._retrieval_log_src} "
            f"{(agent_dir / RETRIEVAL_LOG_NAME).as_posix()}"
        )
        copy_result = await environment.exec(command=copy_cmd)
        retrieval_log_collected = copy_result.return_code == 0

        # Non-mounted environments (not the default Docker env) need explicit
        # downloads; mounted ones already have these files host-side.
        if not environment.capabilities.mounted:
            for name in (AUTOBUILD_LOG_NAME, RETRIEVAL_LOG_NAME, ENV_PROBE_NAME):
                try:
                    await environment.download_file(
                        source_path=str(agent_dir / name),
                        target_path=self.logs_dir / name,
                    )
                except Exception as e:  # tolerated: absence recorded in meta
                    self.logger.warning("download of %s failed: %s", name, e)

        config = self._rollout_config(resolved_command)
        config_hash = compute_config_hash(config)
        (self.logs_dir / CONFIG_NAME).write_text(json.dumps(config, indent=2))

        meta = {
            "schema": 1,
            "adapter_version": ADAPTER_VERSION,
            "arm": self._arm,
            "fleet_memory_retrieval": self._retrieval,
            "config_hash": config_hash,
            "command": resolved_command,
            "exit_code": result.return_code,
            "wallclock_sec": wallclock_sec,
            "retrieval_log_collected": retrieval_log_collected,
            "retrieval_log_src": self._retrieval_log_src,
            "coach_model": self._coach_model,
            "player_model": self._player_model,
            "pg_dsn_redacted": redact_dsn(self._pg_dsn),
        }
        (self.logs_dir / ROLLOUT_META_NAME).write_text(json.dumps(meta, indent=2))

        # A failed autobuild is a legitimate scored outcome: do not raise —
        # the verifier still runs and produces the (0) reward.
        context.metadata = {"autobuild_adapter": meta}
        # SEAM(ABL-001/guardkit): guardkit autobuild does not emit
        # machine-readable token usage yet. Populate
        # context.n_input_tokens / n_cache_tokens / n_output_tokens here once
        # a usage artifact exists; adapter/rollout_record.py already passes
        # them through to the per-rollout JSON.
