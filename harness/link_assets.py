#!/usr/bin/env python3
"""Link the private FinProxy eval assets into this checkout and verify them.

The PO held-out suite's client-derived payloads (corpus copies, April-derived
oracles, fixtures, coverage checklists) are PRIVATE CLIENT DATA and live
outside this repo — in the FinProxy org's `lpa-project-docs` repo under
`eval-assets/po-heldout/`, mirroring this repo's relative layout. This script
symlinks them into place and verifies every file against the committed
`harness/ASSETS.sha256` pin, so the graders and runner work unchanged while
git never sees the content (the linked paths are gitignored).

Usage:
  python3 harness/link_assets.py            # link + verify
  python3 harness/link_assets.py --check    # verify only (no changes)
  PO_EVAL_ASSETS_ROOT=/path/to/assets python3 harness/link_assets.py

A drifted or missing asset is a hard failure: the §5 gate must never grade
against unpinned inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "harness" / "ASSETS.sha256"
DEFAULT_ROOT = (
    REPO_ROOT.parent / "lpa-project-docs" / "eval-assets" / "po-heldout"
)

LINK_TOPS = [
    "tasks/po-held-001-extract-phase-a/input/corpus",
    "tasks/po-held-001-extract-phase-a/solution",
    "tasks/po-held-001-extract-phase-a/test/reference/coverage_checklist.json",
    "tasks/po-held-002-extract-phase-b/input/corpus",
    "tasks/po-held-002-extract-phase-b/input/epic_plan.json",
    "tasks/po-held-002-extract-phase-b/solution",
    "tasks/po-held-003-extract-full/input/corpus",
    "tasks/po-held-003-extract-full/solution",
    "tasks/po-held-003-extract-full/test/reference/coverage_checklist.json",
    "tests/broken_fixtures/po-held-001-extract-phase-a",
    "tests/broken_fixtures/po-held-002-extract-phase-b",
    "tests/broken_fixtures/po-held-003-extract-full",
    "tests/good_fixtures/po-held-001-extract-phase-a",
    "tests/good_fixtures/po-held-002-extract-phase-b",
]


def assets_root() -> Path:
    root = Path(os.environ.get("PO_EVAL_ASSETS_ROOT", DEFAULT_ROOT))
    if not root.is_dir():
        sys.exit(
            f"assets root not found: {root}\n"
            "The PO held-out suite needs the private FinProxy eval assets "
            "(FinProxy org, lpa-project-docs repo, eval-assets/po-heldout/).\n"
            "Clone it next to this repo or set PO_EVAL_ASSETS_ROOT."
        )
    return root


def link(root: Path) -> int:
    made = 0
    for top in LINK_TOPS:
        src = root / top
        dst = REPO_ROOT / top
        if not src.exists():
            sys.exit(f"asset missing from assets repo: {src}")
        if dst.is_symlink():
            if dst.resolve() == src.resolve():
                continue
            dst.unlink()
        elif dst.exists():
            sys.exit(
                f"refusing to replace real path with symlink: {dst}\n"
                "(client content inside the repo working tree? move it to the "
                "assets repo first — it must never be committed here)"
            )
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
        made += 1
    return made


def verify() -> int:
    bad = []
    n = 0
    for line in MANIFEST.read_text().splitlines():
        if not line.strip():
            continue
        sha, rel = line.split(None, 1)
        f = REPO_ROOT / rel
        if not f.is_file():
            bad.append(f"MISSING  {rel}")
            continue
        if hashlib.sha256(f.read_bytes()).hexdigest() != sha:
            bad.append(f"DRIFTED  {rel}")
        n += 1
    if bad:
        sys.exit("asset pin verification FAILED:\n  " + "\n  ".join(bad))
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify only")
    args = ap.parse_args()
    if not args.check:
        made = link(assets_root())
        print(f"linked {made} new path(s) ({len(LINK_TOPS)} total)")
    n = verify()
    print(f"verified {n} files against harness/ASSETS.sha256 — all pinned ✓")


if __name__ == "__main__":
    main()
