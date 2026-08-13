"""Pinned change 2: the blind → resolve → aggregate pipeline is n-way.

Hermetic end-to-end with THREE synthetic candidates: prepare blinds with
labels A/B/C, a synthetic judge answers against the labels, resolve maps
labels back to candidate names, deterministic + aggregate report all three
columns.
"""
from __future__ import annotations

import json

import pytest

from harness.aggregate import main as aggregate_main
from harness.judge.prepare import main as prepare_main
from harness.judge.resolve import main as resolve_main
from harness.score.deterministic import main as deterministic_main
from harness.common import DIMS

CANDIDATES = ["alpha", "beta", "gamma"]
# Opaque per-candidate markers: response TEXT must not contain candidate
# names, so the blind file can be asserted name-free.
MARKER = {"alpha": "M-aa", "beta": "M-bb", "gamma": "M-cc"}


def _mk_responses(run_dir, n_items=4):
    rows = []
    for i in range(n_items):
        responses = {}
        for c in CANDIDATES:
            content = (f"<think>plan {MARKER[c]}</think>Answer {MARKER[c]} to "
                       f"item {i} — what do you notice?")
            responses[c] = {
                "content": content,
                "reasoning_content": "",
                "visible": f"Answer {MARKER[c]} to item {i} — what do you notice?",
                "finish_reason": "stop",
            }
        rows.append({
            "id": f"item-{i:02d}",
            "category": "socratic" if i % 2 == 0 else "tone",
            "subject": "english" if i < 2 else "maths",
            "prompt": f"Student question {i}?",
            "expected_behaviours": ["asks a question"],
            "red_flags": ["hands over the answer"],
            "responses": responses,
        })
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "responses.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows))
    return rows


def _run_prepare(run_dir):
    prepare_main(["--run-dir", str(run_dir), "--seed", "7"])
    key = json.loads((run_dir / "blind_key.json").read_text())
    pairs = [json.loads(l) for l in
             (run_dir / "blind_pairs.jsonl").read_text().splitlines()]
    return key, pairs


def test_prepare_blinds_three_candidates(tmp_path):
    run_dir = tmp_path / "run"
    _mk_responses(run_dir)
    key, pairs = _run_prepare(run_dir)

    assert key["candidates"] == CANDIDATES
    for row in pairs:
        assert set(row["responses"]) == {"A", "B", "C"}
        # No candidate name leaks into the blind file.
        for name in CANDIDATES:
            assert name not in json.dumps(row)
        pos = key["positions"][row["id"]]
        assert sorted(pos.values()) == sorted(CANDIDATES)
        # The blind visible text really is the mapped candidate's text.
        for label, cand in pos.items():
            assert MARKER[cand] in row["responses"][label]["visible"]
        # Inline <think> was surfaced as the judge-facing reasoning channel.
        assert row["responses"]["A"]["reasoning"].startswith("plan ")


def test_resolve_maps_labels_to_candidates_nway(tmp_path):
    run_dir = tmp_path / "run"
    _mk_responses(run_dir)
    key, pairs = _run_prepare(run_dir)

    # Synthetic judge: alpha wins every item except the last, which ties.
    raw = []
    for i, row in enumerate(pairs):
        pos = key["positions"][row["id"]]
        label_of_alpha = next(l for l, c in pos.items() if c == "alpha")
        raw.append({
            "id": row["id"],
            "winner": "tie" if i == len(pairs) - 1 else label_of_alpha,
            **{label: {d: 3 + (ord(label) % 2) for d in DIMS} for label in pos},
            "rationale": f"synthetic verdict {i}",
        })
    (run_dir / "raw_judgements.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in raw))

    resolve_main(["--run-dir", str(run_dir)])
    resolved = [json.loads(l) for l in
                (run_dir / "judgements.jsonl").read_text().splitlines()]

    tally = {}
    for r in resolved:
        tally[r["winner"]] = tally.get(r["winner"], 0) + 1
        assert set(r["scores"]) == set(CANDIDATES)
        # Scores followed the label→candidate mapping.
        pos = key["positions"][r["id"]]
        raw_row = next(x for x in raw if x["id"] == r["id"])
        for label, cand in pos.items():
            assert r["scores"][cand] == raw_row[label]
    assert tally == {"alpha": 3, "tie": 1}


def test_resolve_rejects_missing_dimension(tmp_path):
    run_dir = tmp_path / "run"
    _mk_responses(run_dir, n_items=1)
    key, pairs = _run_prepare(run_dir)
    pos = key["positions"][pairs[0]["id"]]
    broken = {"id": pairs[0]["id"], "winner": "A",
              **{label: {d: 3 for d in DIMS} for label in pos},
              "rationale": ""}
    del broken["B"]["tone"]
    (run_dir / "raw_judgements.jsonl").write_text(json.dumps(broken) + "\n")
    with pytest.raises(SystemExit, match="missing"):
        resolve_main(["--run-dir", str(run_dir)])


def test_deterministic_and_aggregate_nway(tmp_path):
    run_dir = tmp_path / "run"
    _mk_responses(run_dir)
    key, pairs = _run_prepare(run_dir)
    raw = []
    for row in pairs:
        pos = key["positions"][row["id"]]
        raw.append({"id": row["id"], "winner": "A",
                    **{label: {d: 4 for d in DIMS} for label in pos},
                    "rationale": "x"})
    (run_dir / "raw_judgements.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in raw))
    resolve_main(["--run-dir", str(run_dir)])
    deterministic_main(["--run-dir", str(run_dir)])
    aggregate_main(["--run-dir", str(run_dir)])

    det = json.loads((run_dir / "deterministic.json").read_text())
    assert set(det["summary"]) == set(CANDIDATES)
    assert det["summary"]["alpha"]["inline_think_pct"] == 100.0
    assert det["summary"]["alpha"]["leak_total"] == 0

    table = (run_dir / "results-table.md").read_text()
    for c in CANDIDATES:
        assert f"| {c} preferred |" in table
    assert "Δ" not in table          # Δ column only for exactly 2 candidates
    assert "## Win rate by subject" in table   # subject-stamped judgements
    assert "| maths |" in table

    manifest = json.loads((run_dir / "MANIFEST.json").read_text())
    assert manifest["stages"]["judge_prepare"]["seed"] == 7
    for stage in ("judge_prepare", "judge_resolve",
                  "score_deterministic", "aggregate"):
        assert stage in manifest["stages"]
