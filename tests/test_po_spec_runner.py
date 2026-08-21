"""Integrity tests for harness/run_po_spec_eval.py (the po-held-007 tree runner).

These guard the two properties the runner exists to provide, and they are written to RUN — not to
pass. 2026-08-21, from a sibling lane's finding: two fixes shipped tests that proved an instrument
was wired in, and neither test executed under the repository's own command (one missed the
collection pattern, one skipped itself at file level on a missing optional import). Both would have
been green forever while proving nothing. So:

  * this file matches the suite's `test_*.py` collection pattern and lives in `tests/`;
  * it imports nothing optional and skips nothing at module level;
  * its fixtures are inline, so it never silently degrades when an external corpus is absent.

Verify membership, not just outcome:  python3 -m pytest tests/test_po_spec_runner.py --collect-only -q
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "harness" / "run_po_spec_eval.py"


def _load():
    spec = importlib.util.spec_from_file_location("run_po_spec_eval", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# A representative emission in the contract the serving prompt pins and the trace corpus shows.
BUNDLE = """<think>Deciding the scenarios and the unknowns.</think>

=== FILE: features/kiln-firing-slot-booking/kiln-firing-slot-booking.feature ===
```gherkin
Feature: Kiln firing slot booking
  Scenario: A member books a free slot
    Given a free slot
    When the member books it
    Then the slot is theirs
```
=== END FILE ===
=== FILE: features/kiln-firing-slot-booking/kiln-firing-slot-booking_assumptions.yaml ===
assumptions:
  - id: A1
    statement: A slot covers exactly one firing.
=== END FILE ===
=== FILE: features/kiln-firing-slot-booking/kiln-firing-slot-booking_summary.md ===
# Summary
Members book and cancel kiln firing slots.
=== END FILE ===
"""


def test_runner_file_exists_and_loads():
    assert RUNNER.is_file(), f"missing {RUNNER}"
    assert _load() is not None


def test_slicer_recovers_the_three_file_triple():
    """The graded artifact is a TREE; the slicer must recover all three files of the triple."""
    m = _load()
    files = m.slice_file_bundle(m.strip_think(BUNDLE))
    names = sorted(Path(p).name for p in files)
    assert len(files) == 3, f"expected the three-file triple, got {names}"
    assert any(n.endswith(".feature") for n in names), names
    assert any(n.endswith("_assumptions.yaml") for n in names), names
    assert any(n.endswith("_summary.md") for n in names), names


def test_slicer_strips_fences_and_end_markers():
    """Content must be the file's own text — no ``` fences, no `=== END FILE ===` residue."""
    m = _load()
    files = m.slice_file_bundle(m.strip_think(BUNDLE))
    feature = next(v for k, v in files.items() if k.endswith(".feature"))
    assert "```" not in feature, "code fence leaked into the written file"
    assert "END FILE" not in feature, "end marker leaked into the written file"
    assert feature.startswith("Feature:"), feature[:40]


def test_think_block_is_not_written_into_the_tree():
    m = _load()
    files = m.slice_file_bundle(m.strip_think(BUNDLE))
    assert not any("<think>" in v for v in files.values())


def test_write_tree_refuses_path_traversal(tmp_path):
    """A model-authored path must never escape the rep directory."""
    m = _load()
    written = m.write_tree(tmp_path, {"../escaped.feature": "x", "features/a/b.feature": "y"})
    assert written == ["features/a/b.feature"], written
    assert not (tmp_path.parent / "escaped.feature").exists()


def test_config_records_how_the_tree_was_produced():
    """`tree_source` must be reported, so a receipt can never hide the mechanism."""
    m = _load()
    _, source = m.tree_from_output(BUNDLE)
    assert source, "tree_source must never be empty"
    assert "postprocess_feature_spec" in source or "bundle_slicer" in source, source


def test_prompts_root_identity_stamps_the_tree_it_read():
    """A grade must carry evidence of WHICH tree supplied the prompts (branch switches are silent)."""
    m = _load()
    ident = m.prompts_root_identity(REPO_ROOT)  # this repo is a git tree; any git tree will do
    assert set(ident) == {"path", "head", "branch", "dirty"}, ident
    assert ident["head"], "HEAD must be recorded"


# --- the 2026-08-21 assembly correction ------------------------------------------------------
# assemble() used to send {system: player_feature_spec.md, user: brief}. Production's
# build_feature_spec_input() sends LABELLED SECTIONS with the pinned methodology template in the user
# turn, and 007's instruction.md says answer sheets come from that harness. These tests fail against
# the old shortcut, which is the point — a fix whose test passes either way proves nothing.

def _fake_roots(tmp_path):
    m = _load()
    prompts = tmp_path / "specialist-agent" / Path(m.SERVING_PROMPT).parent
    prompts.mkdir(parents=True)
    (tmp_path / "specialist-agent" / m.SERVING_PROMPT).write_text(
        "SYSTEM: emit the four files as === FILE: blocks.", encoding="utf-8")
    tpl = tmp_path / "guardkit" / Path(m.METHODOLOGY_TEMPLATE).parent
    tpl.mkdir(parents=True)
    (tmp_path / "guardkit" / m.METHODOLOGY_TEMPLATE).write_text(
        "TEMPLATE-SENTINEL: the /feature-spec methodology.", encoding="utf-8")
    task = tmp_path / "task"
    (task / "input").mkdir(parents=True)
    (task / "input" / "brief.md").write_text("BRIEF-SENTINEL: book a kiln slot.", encoding="utf-8")
    return m, task, tmp_path / "specialist-agent", tmp_path / "guardkit"


def test_assemble_puts_the_methodology_template_in_the_user_turn(tmp_path):
    """The system prompt says the request CARRIES the template — so the request must carry it."""
    m, task, prompts, tpl = _fake_roots(tmp_path)
    asm = m.assemble(task, prompts, tpl)
    assert "TEMPLATE-SENTINEL" in asm["user"], "the pinned methodology template is missing"
    assert "BRIEF-SENTINEL" in asm["user"], "the brief is missing"


def test_assemble_uses_productions_labelled_sections(tmp_path):
    """build_feature_spec_input() emits these exact section headers, in this order."""
    m, task, prompts, tpl = _fake_roots(tmp_path)
    user = m.assemble(task, prompts, tpl)["user"]
    i_t = user.find("## Methodology template")
    i_a = user.find("## Approved input")
    i_s = user.find("## Stack")
    assert -1 not in (i_t, i_a, i_s), f"missing section header(s): {(i_t, i_a, i_s)}"
    assert i_t < i_a < i_s, "sections are out of production's order"
    assert user.rstrip().endswith("generic"), "stack must be the last section, and 'generic' for 007"


def test_assemble_refuses_when_the_template_is_absent(tmp_path):
    """Silently grading without the template is the defect this fix exists to remove."""
    m, task, prompts, tpl = _fake_roots(tmp_path)
    (tpl / m.METHODOLOGY_TEMPLATE).unlink()
    try:
        m.assemble(task, prompts, tpl)
    except FileNotFoundError as e:
        assert "template" in str(e).lower()
    else:
        raise AssertionError("assemble() must refuse, not quietly send a request production never sends")


def test_template_root_identity_stamps_the_tree(tmp_path):
    m = _load()
    ident = m.template_root_identity(REPO_ROOT)
    assert set(ident) == {"path", "head", "branch", "dirty"}, ident
