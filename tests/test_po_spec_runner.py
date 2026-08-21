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
