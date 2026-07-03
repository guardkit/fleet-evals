"""FEAT-ABL-003: AutoBuild agent adapter for Harbor.

Custom Harbor agent (``harbor run -a adapter.autobuild_agent:AutoBuildAgent``)
that runs ``guardkit autobuild`` inside a task environment container under the
P4 fleet-memory env contract, collects the retrieval log, and leaves reward
production to Harbor's verifier. Per-rollout JSON emission lives in
``adapter.rollout_record``.

Local-only per DF-001: nothing in this package performs cloud tracking.
"""
