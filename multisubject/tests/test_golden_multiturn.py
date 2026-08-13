"""Golden-master tests: the lifted multi-turn resolve stage reproduces the
published 2026-05-18 multi-turn judgements and results table from the
original evidence fixtures (semantic equality; label mapping documented in
tests/util.py)."""
from __future__ import annotations

from harness.judge.multiturn_resolve import main as multiturn_resolve_main

from util import FIXTURES, LEGACY_LABELS, make_run_dir, md_tables, read_jsonl, table_as_dict


def _resolve(tmp_path):
    run_dir = make_run_dir(
        tmp_path, "multiturn_raw_judgements.jsonl", "multiturn_key.json")
    multiturn_resolve_main(["--run-dir", str(run_dir), "--legacy-dims"])  # 2026-05-18 fixture predates the v3 seventh dimension
    return run_dir


def test_multiturn_resolve_reproduces_published_judgements(tmp_path):
    run_dir = _resolve(tmp_path)
    resolved = {r["id"]: r for r in
                read_jsonl(run_dir / "multiturn_judgements.jsonl")}
    published = {r["id"]: r for r in
                 read_jsonl(FIXTURES / "multiturn_judgements.jsonl")}

    assert set(resolved) == set(published)
    for sc_id, pub in published.items():
        got = resolved[sc_id]
        assert got["winner"] == pub["winner"], sc_id
        assert got["rationale"] == pub["rationale"], sc_id
        assert got["scores"]["base"] == pub["base_scores"], sc_id
        assert got["scores"]["finetune"] == pub["finetune_scores"], sc_id

    # Published: base 2 / tie 1 / finetune 0.
    tally = {"base": 0, "finetune": 0, "tie": 0}
    for r in resolved.values():
        tally[r["winner"]] += 1
    assert tally == {"base": 2, "finetune": 0, "tie": 1}


def test_multiturn_resolve_reproduces_published_table(tmp_path):
    run_dir = _resolve(tmp_path)
    got_tables = md_tables((run_dir / "multiturn_results-table.md").read_text())
    pub_tables = md_tables((FIXTURES / "multiturn_results-table.md").read_text())
    assert len(got_tables) == len(pub_tables) == 3

    for i in range(3):
        got = table_as_dict(got_tables[i])
        pub = table_as_dict(pub_tables[i], LEGACY_LABELS)
        # Head-to-head (2/0/1), the six dimension means + Δ, and the three
        # per-scenario verdicts with their verbatim rationales.
        assert got == pub, f"table {i} differs: {got} != {pub}"
