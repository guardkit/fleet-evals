"""Golden-master test: the lifted criterion-referenced scorer reproduces
the published 2026-05-18 length-neutral results table (semantic equality;
column labels are raw candidate names — documented deliberate difference)."""
from __future__ import annotations

from harness.score.criteria import main as criteria_main

from util import FIXTURES, LEGACY_LABELS, make_run_dir, md_tables, table_as_dict


def test_criteria_reproduces_published_table(tmp_path):
    run_dir = make_run_dir(tmp_path, "criteria_judgements.jsonl")
    criteria_main(["--run-dir", str(run_dir)])

    got_tables = md_tables((run_dir / "criteria_results-table.md").read_text())
    pub_tables = md_tables((FIXTURES / "criteria_results-table.md").read_text())
    assert len(got_tables) == len(pub_tables) == 2

    for i in range(2):
        got = table_as_dict(got_tables[i])
        pub = table_as_dict(pub_tables[i], LEGACY_LABELS)
        # Covers behaviours 88.5% vs 62.5%, red flags 0/45 vs 1/45, clean
        # items 9/16 vs 2/16, and every per-item fraction incl. the ⚑1 flag
        # on misconception-01.
        assert got == pub, f"table {i} differs: {got} != {pub}"
