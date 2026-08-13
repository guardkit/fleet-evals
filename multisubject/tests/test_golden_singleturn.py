"""Golden-master tests: the lifted resolve + aggregate + deterministic
stages reproduce the published 2026-05-18 single-turn tables from the
original evidence fixtures.

Semantic equality, not byte equality — the deliberate format differences
are documented in the repo README ("Deliberate format differences vs the
2026-05-18 artefacts"): n-way ``scores``/``positions`` rows instead of
``base_scores``/``finetune_scores``/``base_position``, raw candidate names
as table labels, and a preamble without hard-coded serving claims. The
LEGACY_LABELS map in tests/util.py encodes exactly that label mapping.
"""
from __future__ import annotations

import json

from harness.aggregate import main as aggregate_main
from harness.judge.resolve import main as resolve_main
from harness.score.deterministic import main as deterministic_main

from util import FIXTURES, LEGACY_LABELS, make_run_dir, md_tables, read_jsonl, table_as_dict


def _resolve(tmp_path):
    run_dir = make_run_dir(
        tmp_path, "raw_judgements.jsonl", "blind_key.json", "blind_pairs.jsonl")
    resolve_main(["--run-dir", str(run_dir)])
    return run_dir


def test_resolve_reproduces_published_judgements(tmp_path):
    run_dir = _resolve(tmp_path)
    resolved = {r["id"]: r for r in read_jsonl(run_dir / "judgements.jsonl")}
    published = {r["id"]: r for r in read_jsonl(FIXTURES / "judgements.jsonl")}

    assert set(resolved) == set(published)
    for item_id, pub in published.items():
        got = resolved[item_id]
        assert got["winner"] == pub["winner"], item_id
        assert got["category"] == pub["category"], item_id
        assert got["rationale"] == pub["rationale"], item_id
        # n-way shape carries the same content as the legacy two-way shape:
        assert got["scores"]["base"] == pub["base_scores"], item_id
        assert got["scores"]["finetune"] == pub["finetune_scores"], item_id
        assert got["positions"][pub["base_position"]] == "base", item_id

    # Published head-to-head: base 15 / finetune 1 / tie 0.
    tally = {"base": 0, "finetune": 0, "tie": 0}
    for r in resolved.values():
        tally[r["winner"]] += 1
    assert tally == {"base": 15, "finetune": 1, "tie": 0}


def test_deterministic_reproduces_published_json(tmp_path):
    run_dir = make_run_dir(tmp_path, "responses.jsonl")
    deterministic_main(["--run-dir", str(run_dir)])
    got = json.loads((run_dir / "deterministic.json").read_text())
    published = json.loads((FIXTURES / "deterministic.json").read_text())
    # Exact reproduction — the legacy two-way file IS the n-way shape with
    # candidates named base/finetune.
    assert got == published


def test_aggregate_reproduces_published_results_table(tmp_path):
    run_dir = _resolve(tmp_path)
    (run_dir / "deterministic.json").write_bytes(
        (FIXTURES / "deterministic.json").read_bytes())
    aggregate_main(["--run-dir", str(run_dir)])

    got_tables = md_tables((run_dir / "results-table.md").read_text())
    pub_tables = md_tables((FIXTURES / "results-table.md").read_text())
    assert len(got_tables) == len(pub_tables) == 4

    for i in range(4):
        got = table_as_dict(got_tables[i])
        pub = table_as_dict(pub_tables[i], LEGACY_LABELS)
        # Same rows, same columns (after label mapping), same cell values —
        # covers head-to-head counts/shares (15/94%, 1/6%, 0/0%), the six
        # dimension means + Δ, per-category wins, and deterministic checks.
        assert got == pub, f"table {i} differs: {got} != {pub}"
