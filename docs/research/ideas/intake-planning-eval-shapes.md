# Intake / Planning-Stage Eval Shapes (Tier 2 — shapes only, no suite)

**Status: SHAPES ONLY — a design note, not a verdict scope. Nothing here gates
anything; no tasks, no thresholds, no freeze.** Filed by the P16 session (2026-07-08,
Claude Fable 5) with the Tier-1 suites (`arch-heldout-suite-scope.md`,
`coach-heldout-suite-scope.md`) because the gap analysis names the third hole in the
same breath: "no architect, QA-Verifier, **intake/planning**, or whole-outer-loop eval
coverage of any kind" (`factory-gap-analysis-2026-07-07.md` §3.6). A future session
promotes at most one shape at a time to a real additive suite with its own PROPOSED
scope doc.

## Why shapes only tonight

The intake/planning chain is not yet a stable measurement target: forge Mode P is
built-but-inert (`planning.enabled=False`), the jarvis intake publish grant and the
Mode P return-channel consumer are WS1 build items still landing, and FEAT-SPL-003
(assumption dialogue) was specced only on 2026-07-07. Freezing eval thresholds against
a surface that WS1 is actively rewiring would guarantee instrument churn — the frozen
suites' first rule is that the instrument outlives the candidate.

## Shape 1 — jarvis intake fidelity (doc-shaped, nearest-term)

- **Seat:** the jarvis planning-intake path (Slack message → intake record →
  planning-intake publish).
- **Row:** an authored Slack-thread transcript; answer sheet = the intake record +
  published payload the seat emits.
- **Gates (sketch):** payload schema vs the pinned wire contract; source-fidelity
  anchors (the §2.1 instrument, a third reuse of frozen `idea_gates`) — nothing in the
  intake record that the thread does not license; drop-detection (every actionable
  thread item lands or is explicitly deferred); DF-009 posture (intake never
  auto-originates approval).
- **Blocked on:** the WS1 intake wiring landing (ACL grant + started-event, WS1 doc
  §1/§2); the wire contract to pin against.

## Shape 2 — Mode P chain coherence (tree-shaped, kin of po-held-007/008)

- **Seat:** the forge Mode P chain (intake → `/feature-spec` → `/feature-plan`,
  008-006: Mode P mints the FEAT id).
- **Row:** a pinned intake record; answer sheet = the chain's artifact tree.
- **Gates (sketch):** the existing G-S1..G-S5 batteries apply to the chain's spec/plan
  halves **unchanged** (same instruments, new producer); chain-specific additions are
  only: FEAT-id minting discipline, intake→spec traceability anchors, and
  return-channel record shape (acks/checkpoints that today "evaporate unread").
- **Blocked on:** G2b PASS for the 007/008 terminal itself (grade the tool before the
  chain that drives it); the return-channel consumer (WS1 §7).

## Shape 3 — whole-outer-loop smoke (last, smallest)

- One authored end-to-end rollout record (intake → plan tree → task states) checked for
  join integrity only: every stage's output is the next stage's pinned input, no stage
  invents identifiers. Explicitly NOT a quality gate — a plumbing gate.

## Promotion rule

Promote a shape only when its seat's wire contract is pinned and its WS1 blockers are
closed; each promotion is its own additive suite + PROPOSED scope doc + verifier
integrity battery, per house pattern. Do not promote all three at once.
