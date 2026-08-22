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

---

## Amended 2026-08-22 — the coverage map was added, and why it had to be

**This reference answer FAILED the exam's re-pointed fifth bar when that bar was
first run against it.** That is recorded here rather than quietly fixed, because
it is the more useful fact: the reference was authored 2026-07-07, five weeks
before Rich ruled the routing law into existence (2026-08-14), so it declared
neither `feature_files:` nor `scenarios:` — exactly like every other plan
written before that date. The bar was not relaxed to accommodate it.

**What was added, and only this:** a `feature_files:` entry naming the pinned
input specification, and a `scenarios:` map with one entry per scenario in that
specification — nine of them, each key copied character-for-character from
`input/features/member-directory-search/member-directory-search.feature`, each
stamped `verifier: toolchain` with a `test_ref:` naming the test that proves it.
No `routing_law:` flag: switching the law on is a repo and human decision, and
the planning template says the plan writer never emits it.

**Why `toolchain` for all nine.** The pinned specification is stack-generic —
no request, response, status code, endpoint, message bus, device or browser
appears anywhere in it — so the honest home is the repo's own test suite, which
the template requires to name the test it relies on. The exam does not grade
whether a home was the *apt* choice; that stays Coach territory (extension scope
§5). It grades that a home was chosen, from the allowed list, and backed.

**Everything else about this reference is unchanged**, including the Step-11
tagged spec copy under `features/`. That copy is a legacy artefact — the current
tool cannot emit one — but it is harmless, it still satisfies the
spec-preservation bar, and removing it would have been a change this ruling did
not ask for.
