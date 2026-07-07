# Oracle provenance — po-held-008-feature-plan

Authored for this suite 2026-07-07 (WS1 Session H, FEAT-EVAL-SPEC build;
Claude Fable 5, attended). Not model output and NOT harvested from the
FEAT-RAG-08 gold pair — that trace predates the 2026-07-05 feature-plan
template change (`5ad48fcf`), so this oracle is written directly against the
pinned current-main contract (CONTRACT-feature-spec-plan-outputs.md Parts
B+D; guardkit main 28587b61).

Shape: 5 tasks over 4 waves for the pinned member-directory-search spec
triple; explicit task_type on every task (declarative / feature ×3 /
testing); mode assignment per the pinned rule (complexity ≥4 → task-work);
lint acceptance criterion on the three feature tasks; README +
IMPLEMENTATION-GUIDE with the mandatory data-flow and dependency Mermaid
diagrams; Step-11 tagged spec copy generated mechanically from the pinned
input by inserting standalone `@task:` lines (strip-inverse verified at
authoring time — the spec-preservation gate's own transformation).

`guardkit feature validate FEAT-MDS-01` = exit 0 against the installed CLI
(pinned @ 28587b61), proven by the verifier-integrity Oracle run.
