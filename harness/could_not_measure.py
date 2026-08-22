"""A graded run that could not measure something must not exit 0.

THE DEFECT THIS EXISTS TO CLOSE, in plain words
------------------------------------------------
Every runner in this repo decides whether a graded rep passed by looking at the
exit code of `python3 -m pytest test/ -q` (`harness/run_po_eval.py` grade_rep;
`harness/run_po_spec_eval.py` grade_rep). **pytest exits 0 when a test is
SKIPPED.** So a check that quietly stepped aside — because the thing it wanted to
look at was not in the candidate's output — was written down as a PASS. A bar
that measured nothing scored exactly the same as a bar that measured everything,
and nothing in the receipt showed the difference.

It was found twice: in `po-held-008-feature-plan` on the morning of 2026-08-22,
and in `po-held-007-feature-spec` the same evening. 008 carries its own inline
copy of these two hooks (written first, and left alone deliberately — see the
note at the foot of this file). This module is the shared home so a third exam
never has to reinvent it.

THE FIX
-------
Any skip in a task's grade makes that grade exit non-zero, with its own code, and
prints the skipped checks by name. The code is deliberately outside pytest's own
range (0 ok / 1 failed / 2 interrupted / 3 internal / 4 usage / 5 nothing
collected) so a reader — and a receipt — can tell **"could not measure"** from
**"measured and failed"** at a glance, while every existing `returncode == 0`
check treats it as the failure it is.

This does not stop anyone writing a legitimately conditional check later. It
stops such a check being scored as a pass, which is the part that was wrong.

HOW TO USE IT
-------------
In a task's `test/conftest.py`::

    from harness.could_not_measure import (  # noqa: F401
        EXIT_COULD_NOT_MEASURE,
        pytest_runtest_logreport,
        pytest_sessionfinish,
    )

Importing the two hook functions by name makes them attributes of the conftest
module, which is how pytest discovers hooks. Nothing else is needed.

WHAT THE THREE EXIT CODES MEAN TO A READER OF A GRADE
-----------------------------------------------------
    0   every bar ran, and every bar passed
    1   every bar ran, and at least one failed  — a real result
    40  at least one bar could not be measured  — NOT a result. Never record it
        as a pass, and never record it as a model failure either: find out why
        the bar had nothing to look at first.

NOTE ON THE 008 DUPLICATE. `tasks/po-held-008-feature-plan/test/conftest.py`
carries these hooks inline. Its exact behaviour is cited, with measured
before/after numbers, in the frozen scope document
(`docs/research/ideas/po-heldout-spec-extension-scope.md` §10.2), and it landed
on main hours before this module. Folding it onto this import is a two-line
follow-up and is deliberately left for a lane that owns that file, rather than
edited from the side.
"""
from __future__ import annotations

EXIT_COULD_NOT_MEASURE = 40

_skipped: "dict[str, str]" = {}


def pytest_runtest_logreport(report):
    """Record every skipped check, whichever phase it skipped in."""
    if not report.skipped:
        return
    reason = ""
    longrepr = getattr(report, "longrepr", None)
    if isinstance(longrepr, tuple) and len(longrepr) == 3:
        reason = str(longrepr[2])
    elif longrepr is not None:
        reason = str(longrepr)
    _skipped.setdefault(report.nodeid, reason)


def pytest_sessionfinish(session, exitstatus):
    """A grade that could not measure something must not exit 0."""
    if not _skipped:
        return
    print("\n" + "=" * 72)
    print("COULD NOT MEASURE — this grade skipped checks, so it is NOT a pass:")
    for nodeid, reason in sorted(_skipped.items()):
        print(f"  - {nodeid}\n      {reason}")
    print("A skipped bar measures nothing. Recording it as green is the defect")
    print("this guard exists to prevent (see harness/could_not_measure.py).")
    print("=" * 72)
    if exitstatus == 0:
        session.exitstatus = EXIT_COULD_NOT_MEASURE
