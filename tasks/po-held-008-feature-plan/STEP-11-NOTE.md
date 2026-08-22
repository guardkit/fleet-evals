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
