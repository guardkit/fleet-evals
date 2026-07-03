# Fix the failing unit suite after the TASK-RLY-006 merge

The repository at `/app` is fleet-memory, a LangGraph checkpoint and memory
store. FEAT-MEM-04 wave 4 (TASK-RLY-006, summarised below) was just completed
and approved: the autobuild loop reported every task green. However, the
**full unit test suite is currently failing**.

Your job: find and fix the regression so the full unit suite passes.

```bash
python -m pytest tests/ -q     # integration tests are deselected by default
```

## Constraints

- The functionality TASK-RLY-006 introduced must remain intact: the MEMORY
  stream handler stays registered, and `RelayService` stays constructed and
  exposed in the `app.py` lifespan with its writer dependencies. Do not fix
  the suite by removing, bypassing, or unwiring the feature.
- Fix the source, not the tests: do not modify, delete, skip, or deselect
  existing tests, and do not change the pytest configuration to avoid a
  failing test.

## Context — what TASK-RLY-006 was (original spec, abridged)

**Title:** Thin MEMORY-stream durable consumer — ack/nak/DLQ dispatch and
settings (FEAT-MEM-04, wave 4, complexity 6).

The only NATS-aware module in the feature. A thin `@broker.subscriber` on the
MEMORY stream (durable consumer) that wires `RelayService.ingest` to JetStream
ack semantics, plus Settings additions for the DLQ contract. Registered on the
module-level singleton broker via import side-effect in `app.py`.

Files: `src/fleet_memory/relay/handler.py`; edits to
`src/fleet_memory/settings.py` and `src/fleet_memory/app.py`.

Ack contract (ack-after-commit): clean `ingest` return → ACK;
`PoisonEpisodeError` → reject to the dead-letter subject with reason;
`TransientIngestError` (and unenumerated exceptions) → nak for redelivery up
to `max_deliver`.

Settings additions: `dlq_subject`, `max_deliver: int = 5`,
`chunk_target_tokens: int = 1000`, `chunk_overlap_ratio: float = 0.15`, all
under the `FLEET_MEMORY_` prefix.

`RelayService` is constructed in the lifespan (it already opens the store) and
exposed; the handler pulls it from broker context (mirroring how `store` is
exposed in `app.py`).
