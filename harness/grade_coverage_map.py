#!/usr/bin/env python3
"""Grade captured planning runs against the scenario-coverage bar, off-line.

WHY THIS EXISTS. The po-held-008 exam grades one pinned specification. A real
planning run answers whatever specification it was handed, so the exam's own
pytest gate cannot be pointed at one. This script applies the SAME function the
exam's fifth bar calls — `spec_gates.coverage_map_findings` — to a captured
request/reply pair, using that run's own specification as the truth. Same
instrument, different input: if the two ever disagree, the instrument is wrong.

INPUT. A pair of files as produced by the architect planning drives:
  <name>.payload.json   the request. payload.args.spec_feature is the
                        specification the plan was given.
  <name>.reply.json     the answer. payload.result.role_output.artifacts holds
                        the files the tool emitted, keyed by repo-relative path.

It never contacts a model, a server or the GPU. It reads two JSON files.

Usage:
  python3 harness/grade_coverage_map.py <dir-of-drives> [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from harness import spec_gates  # noqa: E402


def grade_pair(payload_path: Path, reply_path: Path) -> dict:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    reply = json.loads(reply_path.read_text(encoding="utf-8"))

    spec_text = (payload.get("payload", {}).get("args", {}) or {}).get("spec_feature") or ""
    artifacts = (
        ((reply.get("payload", {}).get("result", {}) or {}).get("role_output", {}) or {})
        .get("artifacts") or {}
    )
    yaml_names = [n for n in artifacts if n.startswith(".guardkit/features/") and n.endswith(".yaml")]

    row: dict = {
        "run": payload_path.name.replace(".payload.json", ""),
        "spec_scenarios": len(dict.fromkeys(
            spec_gates._guardkit_routing_law()[1](spec_text))) if spec_text else 0,
    }
    if not spec_text:
        row.update(verdict="CANNOT GRADE", reason="the request carries no specification")
        return row
    if len(yaml_names) != 1:
        row.update(verdict="CANNOT GRADE",
                   reason=f"expected exactly one feature YAML artefact, found {yaml_names}")
        return row

    import yaml as _yaml
    data = _yaml.safe_load(artifacts[yaml_names[0]])
    if not isinstance(data, dict):
        row.update(verdict="CANNOT GRADE", reason="the feature YAML is not a mapping")
        return row

    findings = spec_gates.coverage_map_findings(data, spec_text)
    row.update(
        feature_yaml=yaml_names[0],
        declares_feature_files=bool(data.get("feature_files")),
        declares_scenarios=bool(data.get("scenarios")),
        stamped=len(data.get("scenarios") or {}),
        findings=findings,
        defects=sorted({f["defect"] for f in findings}),
        verdict="PASS" if not findings else "FAIL",
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("drives_dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    d = Path(args.drives_dir)
    rows = []
    for payload in sorted(d.glob("*.payload.json")):
        reply = payload.with_name(payload.name.replace(".payload.json", ".reply.json"))
        if not reply.is_file():
            continue
        rows.append(grade_pair(payload, reply))

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    print(f"{'run':<18} {'scen':>4} {'stamped':>7}  {'verdict':<8} defects")
    print("-" * 100)
    for r in rows:
        print(f"{r['run']:<18} {r.get('spec_scenarios',0):>4} {r.get('stamped',0):>7}  "
              f"{r['verdict']:<8} {', '.join(r.get('defects') or []) or r.get('reason','')}")
    passed = sum(1 for r in rows if r["verdict"] == "PASS")
    print(f"\n{passed}/{len(rows)} captured runs carry a coverage map that holds up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
