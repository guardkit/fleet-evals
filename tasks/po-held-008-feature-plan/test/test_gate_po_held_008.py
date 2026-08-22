"""Gate tests: headless /feature-plan quality from a pinned spec triple.

Axes per the pinned contract (CONTRACT-feature-spec-plan-outputs.md Parts B+D,
guardkit feature-plan.md): the deterministic feature-YAML oracle (`guardkit
feature validate`, exit 0); task-markdown frontmatter discipline (explicit
task_type, id/feature_id/wave agreement); the pinned mode-assignment rule; the
Step 8/9 folder contract (README + IMPLEMENTATION-GUIDE with mandatory Mermaid
diagrams); the lint acceptance criterion; the scenario coverage map; and spec
preservation — a plan may not rewrite the specification it was given.

HISTORY OF THE FIFTH BAR, kept visible rather than tidied away:

* Pinned 2026-07-07 against a step that wrote `@task:` tag lines into a copy of
  the specification. Correct on the day it was written.
* 2026-08-14 Rich retired that step. The tool this exam grades never
  implemented it and its output grammar forbids the file outright.
* 2026-08-22 (morning) the bar was made conditional so it would stop erroring.
  That was worse: with nothing to grade it SKIPPED, and pytest exits 0 on a
  skip, so the bar would have been recorded as PASSED while measuring nothing.
* 2026-08-22 (this change) Rich ruled: require the plan to carry the routing-law
  coverage map in its own YAML, and grade that. `test_bdd_linkage_coherence` is
  replaced by `test_scenario_coverage_map`, which cannot skip. The other half of
  the old axis, `test_spec_preserved_verbatim`, is unchanged and still runs.

Bars one to four (`test_guardkit_validate`, `test_task_frontmatter_discipline`,
`test_mode_assignment`, `test_plan_structure_floor` + `test_readme_and_guide_present`,
`test_mandatory_diagrams`, `test_lint_acceptance_criterion`) are frozen and are
byte-identical to their 2026-07-07 text.

Full account, with the measurements and dates, in STEP-11-NOTE.md.
"""
import json

import pytest

from harness import spec_gates

SLUG = "member-directory-search"
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


def test_scenario_coverage_map(feature_yaml, pinned_input_feature, output_dir):
    """THE FIFTH BAR — does the plan say which scenarios it covers, and is what
    it says true?

    RE-POINTED 2026-08-22 on Rich's ruling. What this bar used to grade, and why
    that stopped working, is in STEP-11-NOTE.md beside this directory; the short
    version is that plans used to mark coverage by writing tag lines into a copy
    of the specification, Rich retired that on 2026-08-14, and the tool that
    writes plans today cannot produce such a file at all. The check that graded
    those tags ended up SKIPPING — and a skipped test exits 0, which every
    runner reads as a pass. A bar that measures nothing must never score green.

    The mechanism graded instead is the one the current planning template
    already specifies for exactly this job: the plan's own feature YAML carries
    `feature_files:` (which specification it is answering) and a `scenarios:`
    map (one entry per scenario, giving the place that scenario will be proved).
    The template says of it, in as many words, that "this command writes the
    authoritative map".

    Graded here, each assertion sourced in `harness/spec_gates.py`
    `coverage_map_findings` at the line that makes it:

      1. the map is present at all — `feature_files:` and `scenarios:`;
      2. `feature_files:` names the specification this exam pinned, not some
         other path;
      3. every key in `scenarios:` is a scenario title copied from that
         specification VERBATIM — a paraphrased key matches nothing, so it
         leaves the scenario unstamped, and a key matching no title at all is
         the plan claiming to cover something nobody asked for;
      4. every scenario in the specification appears in the map — with the
         @smoke ones named separately when they are missing, because that is
         the set re-proved on every build;
      5. every verification home is one of the eight allowed values, and a
         `toolchain` home names the test that proves it;
      6. the plan does not switch the law on — that is a human's decision.

    NEVER SKIPS. An answer with no coverage map FAILS here. That is the whole
    point of the re-pointing: "could not measure" is not a pass.
    """
    findings = spec_gates.coverage_map_findings(
        feature_yaml,
        pinned_input_feature,
        expected_feature_files={f"features/{SLUG}/{SLUG}.feature"},
    )
    findings += spec_gates.task_verifier_findings(output_dir, feature_yaml)
    assert findings == [], (
        "\nthe plan's scenario coverage map does not hold up:\n"
        + "\n".join(json.dumps(f) for f in findings)
    )


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
