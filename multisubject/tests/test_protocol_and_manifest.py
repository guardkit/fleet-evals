"""Pinned changes 4 + 5: MANIFEST.json per run, and pre-registration
enforced by code — runs refuse to start when the venue has no PROTOCOL.md.

All hermetic: the positive-path generation tests use an EMPTY golden set /
scenario file, so the full pipeline runs (gate → candidates → output →
manifest) with zero HTTP calls.
"""
from __future__ import annotations

import json

import pytest

from harness.common import require_protocol, update_manifest
from harness.generate.run_ab_eval import main as run_ab_main
from harness.generate.run_multiturn_eval import main as run_mt_main


def _venue(tmp_path, with_protocol: bool):
    venue = tmp_path / "venue"
    venue.mkdir()
    if with_protocol:
        (venue / "PROTOCOL.md").write_text("# PROTOCOL: test venue\n")
    (venue / "candidates.yaml").write_text(
        "candidates:\n"
        "  - {name: base, model: m-base, endpoint: 'http://localhost:9'}\n"
        "  - {name: finetune, model: m-ft, endpoint: 'http://localhost:9'}\n"
    )
    (tmp_path / "empty.jsonl").write_text("")
    (tmp_path / "prompt.txt").write_text("You are a tutor.")
    return venue


def _args(tmp_path, venue, data_flag):
    return [
        "--venue", str(venue),
        data_flag, str(tmp_path / "empty.jsonl"),
        "--system-prompt", str(tmp_path / "prompt.txt"),
        "--run-dir", str(tmp_path / "run"),
    ]


@pytest.mark.parametrize("main,data_flag", [
    (run_ab_main, "--golden"), (run_mt_main, "--scenarios")])
def test_run_refuses_without_protocol(tmp_path, main, data_flag):
    venue = _venue(tmp_path, with_protocol=False)
    with pytest.raises(SystemExit) as exc:
        main(_args(tmp_path, venue, data_flag))
    assert "PROTOCOL.md" in str(exc.value)
    assert not (tmp_path / "run").exists()  # nothing started


def test_run_starts_with_protocol_and_writes_manifest(tmp_path):
    venue = _venue(tmp_path, with_protocol=True)
    run_ab_main(_args(tmp_path, venue, "--golden"))

    run_dir = tmp_path / "run"
    assert (run_dir / "responses.jsonl").exists()
    manifest = json.loads((run_dir / "MANIFEST.json").read_text())
    assert manifest["schema"] == "fleet-evals/manifest/v1"
    assert "fleet-evals" in manifest["repo_heads"]
    gen = manifest["stages"]["generate"]
    assert gen["n_items"] == 0
    assert [c["name"] for c in gen["candidates"]] == ["base", "finetune"]
    assert gen["system_prompt_sha256"]
    assert gen["protocol_sha256"]
    assert gen["temperature"] == 0.0


def test_multiturn_run_starts_with_protocol(tmp_path):
    venue = _venue(tmp_path, with_protocol=True)
    run_mt_main(_args(tmp_path, venue, "--scenarios"))
    manifest = json.loads((tmp_path / "run" / "MANIFEST.json").read_text())
    assert manifest["stages"]["generate_multiturn"]["n_scenarios"] == 0


def test_require_protocol_returns_path(tmp_path):
    venue = _venue(tmp_path, with_protocol=True)
    assert require_protocol(venue).name == "PROTOCOL.md"


def test_run_refuses_draft_protocol(tmp_path):
    """A DRAFT protocol (written, awaiting Rich's gate tap) refuses like
    absence — the real multisubject PROTOCOL.md ships as DRAFT."""
    venue = _venue(tmp_path, with_protocol=True)
    (venue / "PROTOCOL.md").write_text(
        "# PROTOCOL: test venue\n\n"
        "**Status:** DRAFT — PENDING RICH'S GATE TAP\n"
    )
    with pytest.raises(SystemExit) as exc:
        run_ab_main(_args(tmp_path, venue, "--golden"))
    assert "DRAFT" in str(exc.value)
    assert not (tmp_path / "run").exists()


def test_registered_protocol_passes_gate(tmp_path):
    venue = _venue(tmp_path, with_protocol=True)
    (venue / "PROTOCOL.md").write_text(
        "# PROTOCOL: test venue\n\n"
        "**Status:** REGISTERED (gate tap 2026-01-01)\n"
        "A draft rubric may be mentioned in prose without tripping the gate.\n"
    )
    assert require_protocol(venue).name == "PROTOCOL.md"


def test_shipped_venue_protocol_states():
    """Protocol states as of Rich's 2026-08-07 gate tap: multisubject is
    REGISTERED (runs permitted), bakeoff is still DRAFT (runs refused)."""
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    # Registered venue: require_protocol admits it without raising.
    require_protocol(repo / "venues" / "study-tutor-multisubject")
    protocol = (
        repo / "venues" / "study-tutor-multisubject" / "PROTOCOL.md"
    ).read_text()
    assert "REGISTERED" in protocol and "2026-08-07" in protocol
    # Untapped venue: still refused.
    with pytest.raises(SystemExit) as exc:
        require_protocol(repo / "venues" / "study-tutor-bakeoff")
    assert "DRAFT" in str(exc.value)


def test_update_manifest_merges_stages(tmp_path):
    run_dir = tmp_path / "run"
    update_manifest(run_dir, "generate", {"seed": 1})
    update_manifest(run_dir, "judge_prepare", {"seed": 2,
                                               "repo_heads": {"other": "abc"}})
    manifest = json.loads((run_dir / "MANIFEST.json").read_text())
    assert manifest["stages"]["generate"]["seed"] == 1
    assert manifest["stages"]["judge_prepare"]["seed"] == 2
    assert manifest["repo_heads"]["other"] == "abc"
    assert "fleet-evals" in manifest["repo_heads"]
    assert "recorded_at" in manifest["stages"]["generate"]
