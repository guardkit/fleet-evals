# Oracle provenance — arch-held-001-adversarial-review

Authored for this suite 2026-07-08 (FEAT-EVAL-ARCH build, P16 session per
`ai-transition/docs/kickoff-prompts-fable-sessions-2026-07-07.md` Prompt 16).
Not harvested from any gold trace: no architect review trace of this shape
exists (zero architect eval coverage was the gap — WS4 §5). The review names
the four seeded flaws in `input/design.md`, one finding per flaw, each firing
exactly its own `test/reference/flaw_anchors.json` group — the catchability
demonstration `tests/test_arch_verifier_integrity.py` pins. Anti-stuffing is
demonstrated by the `stuffed-finding` broken fixture, never by the Oracle.
