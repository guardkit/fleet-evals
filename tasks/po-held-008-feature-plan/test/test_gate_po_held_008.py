"""Gate tests: headless /feature-plan quality from a pinned spec triple.

Axes per the pinned contract (CONTRACT-feature-spec-plan-outputs.md Parts B+D,
guardkit feature-plan.md @ 5ad48fcf on main 28587b61): the deterministic
feature-YAML oracle (`guardkit feature validate`, exit 0); task-markdown
frontmatter discipline (explicit task_type, id/feature_id/wave agreement);
the pinned mode-assignment rule; the Step 8/9 folder contract (README +
IMPLEMENTATION-GUIDE with mandatory Mermaid diagrams); the lint acceptance
criterion; plan/spec coherence via @task linkage WHEN a tagged spec copy is
present; and spec preservation — the plan may TAG the input spec, never
rewrite it.

CORRECTION 2026-08-22. Two axes below used to REQUIRE a tagged copy of the
input spec at `features/<slug>/<slug>.feature`. No tool in the chain writes
that file today, and one of them would refuse the whole plan if the model
tried: the plan writer's output grammar admits exactly four artefact shapes
(`.guardkit/features/{id}.yaml`, `tasks/backlog/{slug}/TASK-*.md`,
`.../IMPLEMENTATION-GUIDE.md`, `.../README.md`) and rejects everything else.
The step that used to write the tagged copy — Step 11, BDD scenario linking —
was retired by ruling on 2026-08-14 and is marked DO NOT RUN in the template.
So both axes now grade the copy IF the graded tree carries one, and say so
plainly if it does not. Full account, with the measurements and dates, in
STEP-11-NOTE.md beside this directory.
"""
import json

import pytest

from harness import spec_gates

MIN_TASKS = 3   # anti-collapse floor (dependency-graph diagram threshold)
MIN_WAVES = 2   # a one-wave plan has no ordering judgment to grade


@pytest.fixture(scope="module")
def validate_result(output_dir):
    return spec_gates.run_guardkit_validate(output_dir)


def test_guardkit_validate(validate_result):
    """Part B.1: the installed guardkit CLI (pinned @ 28587b61) is THE schema +
    structural oracle. Exit 0 or the plan does not ship."""
    assert validate_result["exit_code"] == 0, (
        f"guardkit feature validate {validate_result.get('feature_id')} failed "
        f"(exit {validate_result['exit_code']}):\n"
        + json.dumps({k: validate_result.get(k) for k in
                      ("errors", "schema_errors", "structural_errors", "error_message",
                       "stderr_tail")}, indent=2)
    )


def test_task_frontmatter_discipline(output_dir, feature_yaml):
    """Step 9 frontmatter contract, gate-stricter than validate where the
    template says REQUIRED: explicit valid task_type on every task file, and
    id / feature_id / wave agreeing with the YAML + orchestration."""
    findings = spec_gates.frontmatter_findings(output_dir, feature_yaml)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_mode_assignment(feature_yaml):
    """Contract B.4 pinned default: task-work for complexity >= 4, direct for
    <= 3."""
    findings = spec_gates.mode_assignment_findings(feature_yaml)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_plan_structure_floor(feature_yaml):
    """Anti-collapse: a real plan for this spec decomposes into >= 3 tasks
    over >= 2 waves (the pinned spec has 9 scenarios across 4 categories)."""
    tasks = feature_yaml.get("tasks") or []
    waves = (feature_yaml.get("orchestration") or {}).get("parallel_groups") or []
    assert len(tasks) >= MIN_TASKS, f"only {len(tasks)} tasks — effort-dodging floor is {MIN_TASKS}"
    assert len(waves) >= MIN_WAVES, f"only {len(waves)} wave(s) — floor is {MIN_WAVES}"


def test_readme_and_guide_present(output_dir):
    """Step 8/9 folder contract: tasks/backlog/{slug}/ carries README.md and
    IMPLEMENTATION-GUIDE.md alongside the task files."""
    folder = output_dir / "tasks" / "backlog" / "member-directory-search"
    assert (folder / "README.md").is_file(), f"missing {folder / 'README.md'}"
    assert (folder / "IMPLEMENTATION-GUIDE.md").is_file(), f"missing {folder / 'IMPLEMENTATION-GUIDE.md'}"


def test_mandatory_diagrams(output_dir, feature_yaml):
    """Part B.5: data-flow Mermaid diagram ALWAYS; task-dependency graph when
    >= 3 tasks. (Integration-contract diagram is complexity-conditional and
    input-dependent — Coach territory, not gated here.)"""
    guide = (output_dir / "tasks" / "backlog" / "member-directory-search"
             / "IMPLEMENTATION-GUIDE.md").read_text(encoding="utf-8")
    blocks = spec_gates.mermaid_blocks(guide)
    assert blocks, "IMPLEMENTATION-GUIDE.md has no ```mermaid blocks"
    assert any(b.lstrip().startswith("flowchart") for b in blocks), (
        "mandatory data-flow diagram (flowchart) missing from IMPLEMENTATION-GUIDE.md"
    )
    if len(feature_yaml.get("tasks") or []) >= 3:
        assert any(b.lstrip().startswith("graph TD") for b in blocks), (
            "task-dependency graph (graph TD) required for >= 3 tasks"
        )


def test_lint_acceptance_criterion(output_dir, feature_yaml):
    """Step 9: every implementation (feature/refactor) task carries the
    stack-agnostic lint/format acceptance criterion."""
    missing = []
    for task in feature_yaml.get("tasks") or []:
        tid = str(task.get("id"))
        if spec_gates.effective_task_type(output_dir, feature_yaml, tid) not in ("feature", "refactor"):
            continue
        body = (output_dir / str(task.get("file_path"))).read_text(encoding="utf-8")
        if "lint" not in body.lower():
            missing.append(tid)
    assert missing == [], f"implementation tasks without the lint acceptance criterion: {missing}"


def test_bdd_linkage_coherence(parsed, feature_yaml, output_dir):
    """Plan/spec coherence: every @task tag resolves to a plan task; every
    @smoke scenario is linked; every feature-type task owns at least one
    scenario.

    Graded WHEN the tree carries a spec copy with at least one @task tag.
    Skipped otherwise, and that is not leniency — it is the contract:

    * No spec copy at all is what the plan tool produces. Its four artefact
      shapes cannot contain a `.feature` file (STEP-11-NOTE.md).
    * A copy with NO @task tags is what a real forge worktree looks like: the
      spec stage commits the untagged `.feature`, and Step 11 — the step that
      would tag it — is retired DO NOT RUN since 2026-08-14. Failing an
      untagged copy would fail a plan for obeying the ruling.

    Consequence worth stating out loud: for any sheet the current tool
    produces, this axis is not graded at all. Nothing in the four artefact
    shapes carries a scenario-to-task mapping. If plan/spec coherence is to
    have teeth again, something must first produce the mapping — see the
    closing section of STEP-11-NOTE.md.
    """
    if parsed is None:
        pytest.skip(
            "no copy of the spec .feature in the graded tree — the plan tool "
            "cannot emit one (retired Step 11; see STEP-11-NOTE.md)"
        )
    tagged = any(t.startswith("@task:") for sc in parsed["scenarios"] for t in sc["tags"])
    if not tagged:
        pytest.skip(
            "spec copy present but carries no @task tags — tagging is retired "
            "DO NOT RUN since 2026-08-14 (see STEP-11-NOTE.md)"
        )
    findings = spec_gates.linkage_findings(parsed, feature_yaml, output_dir)
    assert findings == [], "\n" + "\n".join(json.dumps(f) for f in findings)


def test_spec_preserved_verbatim(output_dir, tagged_feature_paths, pinned_input_feature):
    """Spec preservation: the plan may INSERT standalone `@task:<ID>` lines
    into the spec, never rewrite a line of it. Stripping exactly those lines
    from any copy in the tree must reproduce the pinned input byte-for-byte.

    CORRECTION 2026-08-22: this now grades EVERY copy of the spec in the tree
    rather than only the one canonical path, and a tree with NO copy passes
    rather than erroring. Both halves are strictly more faithful to the
    assertion the test is named for — "the plan did not rewrite the spec" is
    true of a plan that emits no copy, and a rewritten copy at a non-canonical
    path used to slip through. The requirement to PRODUCE a copy is what was
    dropped, and only that; see STEP-11-NOTE.md.
    """
    offenders = []
    for path in tagged_feature_paths:
        stripped = spec_gates.strip_task_tag_lines(path.read_text(encoding="utf-8"))
        if stripped != pinned_input_feature:
            offenders.append(str(path.relative_to(output_dir)))
    assert offenders == [], (
        "these .feature copies are not the pinned input plus @task tag lines — "
        f"the plan modified the spec (only tag insertion is allowed): {offenders}"
    )
