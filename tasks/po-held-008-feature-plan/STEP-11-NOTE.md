# Why this exam no longer requires a tagged `.feature` copy

**Read this before adding the requirement back.** Dated 2026-08-22.

## The short version

This exam used to require the answer to contain
`features/member-directory-search/member-directory-search.feature` — a copy of
the input specification with `@task:<TASK-ID>` tag lines inserted, linking each
scenario to the plan task that will build it. That file is called the Step-11
tagged copy.

**Nothing in the chain writes that file any more, and the plan writer would
refuse the whole plan if it tried.** So the exam was failing the tool for not
doing something the tool is forbidden to do. Two of the nine tests could never
pass. They have been corrected to grade the tagged copy *if it is there* and to
say so plainly *if it is not*, instead of erroring before any grading happens.

Nothing else about the exam changed. The pinned input specification is
untouched, its checksum still holds, and the seven other tests are byte-for-byte
what they were.

## What was measured, on 2026-08-22

1. **The plan writer's output grammar admits four artefact shapes and no
   others.** In `specialist-agent`,
   `src/specialist_agent/roles/architect/modes/feature_plan_oracle.py` defines
   `ARTIFACT_NAME_GRAMMAR` as exactly `.guardkit/features/{id}.yaml`,
   `tasks/backlog/{slug}/TASK-*.md`, `tasks/backlog/{slug}/IMPLEMENTATION-GUIDE.md`,
   `tasks/backlog/{slug}/README.md`. Calling
   `is_recognized_artifact_name("features/member-directory-search/member-directory-search.feature")`
   returns `False`, and a plan containing such a block raises
   "unknown artifact block name" — which discards **the entire plan**, not just
   that block. A model that obeyed the old instruction would have scored zero.

2. **The specification file the plan is given is explicitly never emitted.**
   `specialist_agent/modes/types.py` carries the spec `.feature` content into
   the plan run as `spec_feature`, with the comment that it is
   "NEVER emitted: never returned in an artifact map, never written to
   output_path, never sliced or committed."

3. **forge does not add the tagged copy either.** `bdd_linker` and `@task:`
   tagging appear nowhere in forge's planning code. forge's spec stage does
   commit the specification at `features/<slug>/<slug>.feature` — but
   **untagged**, as the spec writer produced it.

4. **The two tests failed only for the missing file.** Grading the real drive
   output of 2026-08-22 gave 6 passed, 1 failed, 2 errors; both errors were the
   fixture assertion `tagged spec copy missing: .../member-directory-search.feature`
   at `test/conftest.py:36`, raised before either test body ran.

## When and why the requirement went stale

| Date | What happened |
|---|---|
| 2026-04-22 | Step 11 (BDD scenario linking) **is built**, in guardkit's interactive `/feature-plan` slash command (`55b94054`). It really worked: a `bdd-linker` subagent matched scenarios to tasks and `bdd_linker.apply_mapping` inserted the tag lines. |
| 2026-07-07 | **This exam is pinned**, against that slash command (`installer/core/commands/feature-plan.md @ 5ad48fcf`). Requiring the tagged copy was correct on the day it was written. |
| 2026-07-09 | The **headless plan tool** is created in `specialist-agent` (`945f50c`) — a different implementation of the same job, and the one this exam now grades. It never implemented Step 11. `bdd_linker` and `@task:` have never appeared in that repo's source at any commit. |
| 2026-08-14 | **Rich retires Step 11** (guardkit `a87862ef`, the Q10 ruling on the BDD-replacement options card). The template text becomes "BDD scenario linking — RETIRED. DO NOT RUN", with the instruction not to write `@task:` tags into any `.feature` file, because those tags were what armed the retired BDD-execution oracle. The `.feature` file is kept as the specification; scenario verification moves to frozen executable twins under the routing law. |
| 2026-08-15 | `specialist-agent` moves its template pin to follow the ruling (`templates/pins.py`). |
| 2026-08-22 | The exam is corrected — this note. |

So: **correcting the exam removes a stale requirement, it does not waive a live
one.** The behaviour was real once, in a different tool, and was then
deliberately retired. Grading it in 2026 measures the calendar, not the model.

## What the correction actually did

* `test_spec_preserved_verbatim` — **strengthened, not weakened.** It used to
  check one canonical path and error if that path was missing. It now checks
  *every* copy of this spec anywhere under `features/` in the graded tree, so a
  rewritten copy at a non-canonical path can no longer slip past, and a tree
  with no copy passes — a plan that emits no copy demonstrably did not rewrite
  the spec. Every assertion the old test made survives.
* `test_bdd_linkage_coherence` — **made conditional.** All four of its
  assertions (no dangling tag, at least one scenario linked, every `@smoke`
  scenario linked, every feature-type task owns a scenario) are kept exactly as
  they were and still run against any tree that carries a tagged copy. They are
  skipped when there is no copy, and when a copy is present but untagged —
  because an untagged copy is precisely what a forge worktree holds after the
  ruling, and failing it would punish a plan for obeying the ruling.
* One broken-fixture expectation was updated: `stub-plan` used to be caught by
  three tests including this one (it has an untagged copy). It is now caught by
  the other two, `test_plan_structure_floor` and `test_mandatory_diagrams`. A
  deliberately stubbed plan still fails the exam.

## The honest cost, and what would fix it

**For any answer the current tool produces, plan/spec coherence is not graded at
all.** Not leniently graded — not graded. None of the four artefact shapes
carries a mapping from scenario to task, so there is nothing to check. The exam
can no longer tell you whether a plan's tasks actually cover the scenarios the
specification asked for, or whether it invented tasks nothing asked for.

That is a real gap, and closing it is a decision about the *tool*, not about
this exam. Two options exist, and both need someone to rule on them:

1. **Give the plan writer the routing-law map.** The current
   `/feature-plan` template already says this command "writes the authoritative
   map" into the feature YAML: a `feature_files:` list plus a `scenarios:` block
   keyed by verbatim scenario title, each with a `verifier:` stamp from a closed
   vocabulary. That is the modern successor to `@task:` tagging and it lives
   inside `.guardkit/features/{id}.yaml`, which the plan writer *can* emit. The
   measured drive of 2026-08-22 did **not** emit it, and forge has code that
   fills the key in when "the 008 plan-writer omitted the key" — so today it is
   tolerated rather than required. If it were required, this exam could grade
   coverage again with real teeth.
2. **Build Step 11 into the plan tool** — widen the artefact grammar to admit
   the tagged copy and have the tool write it. This reverses a 2026-08-14
   ruling and re-arms the tagging that ruling removed, so it is not a small
   change.

**Do not re-add the requirement to this exam without first building whichever
mechanism is chosen.** An exam that grades a behaviour no tool performs does not
measure the model — it just subtracts two marks from every score, which is what
it did between July and today.

---

## Added 2026-08-22 after adversarial review — two things the first pass got wrong

**1. A SKIP ON THE LINKAGE AXIS SCORES GREEN. This is the important one.**
`harness/run_po_eval.py:255` grades a rep by `proc.returncode == 0`, and **pytest exits 0
when tests skip**. So the frozen threshold G-S5 ("3/3 plan reps pass
`test_bdd_linkage_coherence`") would record as MET on an axis that measured nothing at
all. Correcting the task instrument without saying so would have converted a visible
failure into an invisible one — the exact defect class this estate spent the week
removing.

The freezing document `docs/research/ideas/po-heldout-spec-extension-scope.md` has
therefore been **reopened on the G-S5 axis, visibly**, per its own rule that instrument
revisions "reopen this doc *before* the next freeze, never silently". It records three
options and awaits Rich's ruling. **Until he rules, a skip here means COULD NOT MEASURE
and must never be written down as a pass.**

**2. The tagged-copy selection depended on filename sort order.**
`tagged_feature_text` took `paths[0]`. A tree holding an untagged copy that sorts first
and a *tagged* copy that sorts second was judged on the untagged one — so a dangling
`@task:` tag in the other file was never graded. Measured both ways: the same tree
flipped between "8 passed, 1 skipped" and a caught `dangling_task_tag` purely on
ordering. Now the fixture selects the first copy that actually **contains** a `@task:`
tag and only falls back to `paths[0]` when none does. Proven by mutation: the
dangling-tag tree that previously skipped now fails by name.

**Scope note, stated precisely:** the fixture checks every file *named
`<slug>.feature`* under `features/` — not every file under `features/`. A rewritten copy
saved under a different filename is not caught. That was true before this lane too; it
is recorded here so nobody reads "every copy" as broader than it is.

---

## Added 2026-08-22, afternoon — RICH RULED. The fifth bar now grades the plan's own coverage map.

Everything above stands as the record of how the bar went stale and what the
morning's correction did. This section records what replaced it.

**The ruling.** Of the three options listed above, Rich chose the second — make
the plan writer emit `feature_files:` and `scenarios:` inside the plan's own
feature YAML, and grade that. His words: *"that would be a better long term
option"*.

**What the bar is now.** `test_bdd_linkage_coherence` is gone;
`test_scenario_coverage_map` takes its place. It requires the plan's feature
YAML to carry:

```yaml
feature_files:
  - features/member-directory-search/member-directory-search.feature
scenarios:
  "Searching by name returns matching members":
    verifier: toolchain
    test_ref: test_search_by_name
```

and then grades it. Every assertion is taken from the planning template the
serving seat is actually given (guardkit `installer/core/commands/feature-plan.md`,
pinned by specialist-agent as `feature-plan-methodology`, sha256 `20a3061159…`,
commit `3ad3a366`, 3,017 lines) or from the code that enforces it. Nothing is
invented for the exam; each check names its source in
`harness/spec_gates.py::coverage_map_findings`:

| What is required | Where it comes from |
|---|---|
| `feature_files:` and `scenarios:` are present | template "Required Fields" table; "this command **writes the authoritative map**" |
| `feature_files:` names the pinned specification and no other path | specialist-agent `feature_plan_oracle.py` (an entry naming any other path "is still refused"); forge `declare_feature_files_if_absent`; guardkit `_enforce_routing_law` (a declared file must exist) |
| every key is a scenario title copied **verbatim** | template: keys "MUST be the spec's `Scenario:` titles VERBATIM … never paraphrase, re-case, or tidy it" |
| every scenario in the specification appears in the map | template: a scenario "missing from `scenarios:` **rejects the plan load**"; guardkit `_enforce_routing_law` lists them by name |
| a `@smoke` scenario left out is named separately | the frozen G-S5 wording called the smoke set out by name; it is the set re-proved on every build |
| `verifier:` is one of the eight allowed homes | template's closed vocabulary; guardkit `VERIFIER_HOMES`, imported not copied |
| a `toolchain` home carries `test_ref:` | template ("REQUIRED with toolchain — never omit"); guardkit `ScenarioStamp` |
| a stamp carries no other keys | guardkit `ScenarioStamp` (`extra="forbid"`; allowed keys are verifier, test_ref, test_paths) |
| the plan does not write `routing_law:` | template: "Do NOT emit `routing_law:` — the plan-writer never sets policy" |
| a task's own `verifier:` stamp, when it has one, obeys the same rules | template, "Task frontmatter" |

**One thing the old bar did that this one cannot, said plainly.** The retired
tags named a TASK per scenario, so the exam could ask "does every task named
exist?" and "does every task own a scenario?". **The routing-law map has no task
field at all** — its stamp schema allows exactly `verifier`, `test_ref`,
`test_paths` and rejects anything else — because the routing law replaced
task-ownership with verification-home ownership. Those two questions therefore
have **no successor**, and the exam no longer asks them. What survives on the
task side is the frontmatter `verifier:` stamp, which is graded. This is a real
narrowing and it is recorded here rather than glossed.

**The skip that scored green is closed twice over.**

1. The new bar never skips. A plan with no coverage map FAILS it.
2. `tasks/po-held-008-feature-plan/test/conftest.py` now refuses to let *any*
   skip in this grade exit 0. It prints the skipped checks by name and returns
   exit code **40** — deliberately outside pytest's own range (0 ok / 1 failed /
   2 interrupted / 3 internal / 4 usage / 5 nothing collected) so a reader can
   tell "could not measure" from "measured and failed", while every existing
   `returncode == 0` check in the runners treats it as the failure it is.

Measured, on a plan of exactly the shape today's tool produces (the reference
answer with no spec copy and no coverage map):

| Instrument | Result | Exit code |
|---|---|---|
| this morning's | 8 passed, 1 skipped | **0 — recorded as PASSED** |
| this afternoon's | 8 passed, 1 failed | **1** |

**The reference answer failed the new bar, and that is a real finding, not a
weakened bar.** `solution/` was authored 2026-07-07, five weeks before the
routing law was ruled (2026-08-14). It had no `feature_files:` and no
`scenarios:`, so it failed exactly as any other pre-law plan does. The bar was
NOT relaxed to fit it: the reference was brought up to the current contract by
appending the coverage map (nine scenarios, every title copied from the pinned
input, `toolchain` homes each naming their test). Nothing else about the
reference changed. The same map was appended to all eighteen 008 fixtures so
each still fails only for its own defect.

**The fixture battery grew from 14 broken to 20.** Six new firing demos —
`no-coverage-map`, `paraphrased-scenario-key`, `unknown-verifier-home`,
`bare-toolchain-stamp`, `feature-files-wrong-path`, `routing-law-emitted` —
each built by copying the reference answer and making exactly one change, so
the diff against a passing plan *is* the defect. The three fixtures built for
the retired tag check keep their names and their place and now carry the
equivalent coverage-map defect; each one's `meta.json` says what it demonstrates
now and how that relates to what it demonstrated before.

**Two of the new checks are independently corroborated.** `bare-toolchain-stamp`
and `unknown-verifier-home` also fail `test_guardkit_validate` — guardkit's own
CLI refuses those stamps at load, with no involvement from the exam. The exam
and the production loader agree about what an invalid stamp is.
