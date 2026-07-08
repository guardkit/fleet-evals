# Oracle provenance — qav-held-001-gold-negatives

Authored for this suite 2026-07-08 (FEAT-EVAL-QAV build, WS2 B12 Opus session).
Four reject verdicts, one per real gold-negative bundle: the owning documented
DC class + a locus naming the in-bundle signal (BDD authoring-sweep null,
unwired production call sites, hardcoded-None producer, kwargs-TypeError
swallowed by soft-fail).

These are the **real rows** — WS2 B12's single registration of the four
escaped-seam completions (SMP-002, SMP-003, 10AC, DD4F). The bundle evidence
matches `adf qav.gold_negatives` `GoldNegative.reconstructed_bundle`
field-for-field (drift-guarded by the integrity test when the sibling repo is
present). The coach-heldout suite carries only class-KIN analogues and
mechanically bans these markers; the markers live HERE.

`ground_truth_source` records the layer that actually caught each escape
(operator or merge review) — it is row metadata, never a model output, because
a judge cannot know which layer would have caught it.
