"""Repo-root pytest configuration (additive; no frozen file is affected).

The `tasks/abl-*` ablation tasks' tests/ are CONTAINER verifiers: they assert
against `/app` inside each task's Harbor environment (see the task.toml
[environment] tables and docs/runbooks/FEAT-ABL-002-spike.md), so they can
only run in-container — host-side collection is a category error. Worse, all
three share the basename `test_outputs.py`, which breaks a combined
`pytest tests/ tasks/` run outright ("import file mismatch") before a single
test executes.

Ignore them at root-level collection so the frozen suite's documented
build-end invocation (`pytest tests/ tasks/`, po-heldout-suite-scope.md §5.1)
collects only host-runnable gates. The in-container invocation each abl task
pins is untouched — inside the environment, pytest runs from the task root
and never sees this file.
"""

collect_ignore_glob = ["tasks/abl-*"]
