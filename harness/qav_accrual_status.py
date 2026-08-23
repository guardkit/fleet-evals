"""QAV shadow accrual — how far toward the decision bar, and is it still moving? (2026-08-23)

WHY THIS EXISTS. The graduation bar is "≥25 shadow-judged builds, zero adjudicated false-blocks"
(qav-shadow-mode-design-2026-07-25.md §71-72). Nothing reported progress against it, so on 2026-08-23
the honest answer to "are we close?" was unknown — and two wrong answers were given before this script
existed, both from counting the wrong files:

  * `.guardkit/worktrees/**` receipts are DELETED when a feature's worktree is cleaned after merge, so
    counting them undercounts and skews July-heavy. That subset said 22 turns / ~5 builds / 68% agree.
  * The durable copies are exported by forge's receipts-landing lane to
    $FORGE_RECEIPTS_DIR/<build_id>/ (default ~/forge-state/receipts). Those say 33 turns / 7 builds /
    93% agree, running to 19 August.

READ THE EXPORTED RECEIPTS. They are the record; the worktree copies are transient.

Also note `python glob('**')` does NOT descend hidden directories, so it silently returns ZERO under
`.guardkit`. This walks with os.walk for that reason — a scan that finds nothing looks identical to a
store that holds nothing, which is the failure this whole lane keeps meeting.
"""
from __future__ import annotations
import argparse, collections, json, os, re
from pathlib import Path

BAR_BUILDS = 25
DEFAULT_RECEIPTS = os.environ.get("FORGE_RECEIPTS_DIR", "~/forge-state/receipts")


def collect(root: Path) -> list[dict]:
    rows, seen = [], set()
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not (fn.startswith("qav_shadow_turn_") and fn.endswith(".json")):
                continue
            p = Path(dirpath) / fn
            try:
                d = json.loads(p.read_text())
            except Exception:
                continue
            key = (d.get("task_id"), d.get("turn"), d.get("ts"))
            if key in seen:
                continue
            seen.add(key)
            m = re.search(rf"{re.escape(str(root))}/([^/]+)/", str(p))
            sh = d.get("shadow") or {}
            rows.append({
                "build": m.group(1) if m else "?",
                "ts": (d.get("ts") or "")[:10],
                "coach": d.get("coach_decision"),
                "qav": sh.get("verdict"),
                "agree": d.get("agree"),
                "findings": len(sh.get("findings") or []),
                "status": d.get("status"),
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipts", default=DEFAULT_RECEIPTS)
    a = ap.parse_args()
    root = Path(os.path.expanduser(a.receipts)).resolve()
    if not root.is_dir():
        print(f"  ABORT: receipts dir not found: {root}")
        return 2
    rows = collect(root)
    if not rows:
        # An empty scan is a RESULT, not a silence — say so loudly.
        print(f"  NO shadow receipts under {root} — accrual is 0/{BAR_BUILDS}, or the export lane is broken.")
        return 1

    builds = sorted({r["build"] for r in rows})
    graded = [r for r in rows if r["agree"] is not None]
    agree = sum(1 for r in graded if r["agree"])
    no_verdict = [r for r in rows if r["qav"] is None]
    blocks = [r for r in rows if r["coach"] == "approve" and r["qav"] == "reject"]

    print(f"  QAV SHADOW ACCRUAL — {root}")
    print(f"    builds judged     : {len(builds)}/{BAR_BUILDS}"
          f"   {'BAR MET' if len(builds) >= BAR_BUILDS else f'({BAR_BUILDS - len(builds)} to go)'}")
    print(f"    turns             : {len(rows)}   ({min(r['ts'] for r in rows)} .. {max(r['ts'] for r in rows)})")
    if graded:
        print(f"    agreement         : {agree}/{len(graded)} = {100*agree/len(graded):.0f}%")
    print(f"    turns w/ finding  : {sum(1 for r in rows if r['findings'])}/{len(rows)}")
    print(f"    NO verdict        : {len(no_verdict)}/{len(rows)}"
          f"{'  <-- shadow produced nothing on these' if no_verdict else ''}")
    print(f"    independent blocks: {len(blocks)}   (coach approved, QAV rejected)")
    if not blocks:
        # The bar's safety criterion is "zero adjudicated false-blocks". Zero blocks of ANY kind
        # satisfies it vacuously — say that plainly rather than let it read as a pass.
        print("      NOTE: zero blocks of any kind, so 'zero false-blocks' is satisfied VACUOUSLY —")
        print("      it is not evidence QAV blocks correctly, only that it has never blocked.")
    print("\n    coach x QAV:")
    for (c, q), n in sorted(collections.Counter((r["coach"], r["qav"]) for r in rows).items(), key=lambda x: -x[1]):
        print(f"      coach={str(c):<9} qav={str(q):<9} n={n}")
    print("\n    builds:")
    for b in builds:
        print(f"      {b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
