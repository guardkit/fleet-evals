# Frontier baseline — po-held-005-idea

- **Model:** Claude Fable (claude-fable-5), attended session 2026-07-05 (the
  in-window frontier model; TASK-EVI-005).
- **Assembly:** serving-faithful — system = `player_idea.md` verbatim, user =
  `input/brief.md`, exactly as `run_po_eval.py --suite po-heldout-idea --dry-run`
  assembles (proven 6/6 in TASK-EVI-004's commit).
- **Gate result at authoring:** 7/7 PASS (recorded in the extension scope §6).
- **Calibration role:** carries the natural compound-assumption shape — ASM-001
  matches 2 body-asserted anchor groups (integration + clinician_workflow),
  exactly at the ASSUM-009 threshold, and must license both. This fixture
  failing = the anti-stuffing rule has drifted penalty-side.
