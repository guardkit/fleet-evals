# Frontier baseline — po-held-006-scope

- **Model:** Claude Fable (claude-fable-5), attended session 2026-07-05 (the
  in-window frontier model; TASK-EVI-005; Context B decision: both tasks get a
  frontier sheet).
- **Assembly:** serving-faithful — system = `player_scope.md` verbatim, user =
  `## Existing Roadmap` + reference_roadmap.json + `## Constraint` +
  constraint.md, exactly as the runner assembles.
- **Gate result at authoring:** 9/9 PASS (recorded in the extension scope §6).
- **Calibration role:** carries paraphrased constraint echo ("six-week window",
  "pair of engineers", "MVP pilot loop") — the constraint-anchor alternates must
  tolerate faithful paraphrase. A different selection from the Oracle
  ({001,002,004,007,008} vs {001,002,004,008}) proving the gates accept any
  dependency-closed, constraint-carried cut, not one blessed answer.
