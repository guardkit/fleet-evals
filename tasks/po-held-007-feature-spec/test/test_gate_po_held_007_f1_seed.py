"""Gate tests: F1 quality-bar SEED emission (DFEM-008 / DF-012 §2.1).

ADDITIVE G2b extension landed in the DF-019 re-pin window (2026-07-11). The
pinned /feature-spec template now describes an additive `qa/pass-bar-seed-<slug>.yaml`
emission; these gates grade that seed on the two axes the window's re-freeze names:

  - **criteria observability** — every seed criterion is a real, mechanically
    derived, observable check: an id keyed to the feature, text that resolves to
    an actual scenario in the gold `.feature` (no placeholder / invented text),
    a valid class + evidence_kind. A non-degeneracy floor guards against an
    empty or stub seed passing on schema alone (panel finding C-F8).
  - **negative-path honesty** — `auth_surface_bearing` is an explicit bool with
    a stated basis; an authless feature emits `false` with ZERO fabricated auth
    criteria (panel finding A-F2 — no auto-applied auth guess laundered into
    concrete rows). The determination is a deferred assumption, never invented.

The seed is graded from `$PO_EVAL_OUTPUT_DIR/qa/` (defaults to the task's
solution/, so a bare run validates the frozen gold seed). Frozen surfaces (brief,
reference anchors, banlist, the gold spec triple) are untouched — this file and
the gold `solution/qa/` seed are the sanctioned additive re-freeze.

2026-08-22 — WHAT CHANGED HERE, AND WHAT DELIBERATELY DID NOT.

Not one assertion in this file changed. What changed is what happens when there
is nothing to assert against. These three checks skip when the graded tree
carries no seed, and until today a skip exited 0, so a runner recorded all three
as PASSED. `tasks/po-held-007-feature-spec/test/conftest.py` now installs
`harness/could_not_measure.py`, which makes any skip in this grade exit 40 and
names the checks that stepped aside.

The skip REASON below was also wrong, and the wrong word mattered: it blamed
"this candidate". The seed is not written by the candidate. Production's
`/feature-spec` post-processor composes it deterministically from the model's own
`@key-example` / `@smoke` scenarios (specialist-agent
`roles/product_owner/modes/feature_spec.py`, `_compose_pass_bar_seed`). A missing
seed therefore usually says something about the HARNESS — the recorded reps of
2026-08-21 all fell back to slicing the model's file bundle because the
post-processor could not be constructed outside a live session — and not about
the model. A reason that points the reader at the model is a reason that sends
them to the wrong place.

Whether these three axes belong in this exam at all is a scope question for Rich,
not a lane's edit: see `docs/research/ideas/po-heldout-spec-extension-scope.md`
§11.6.
"""
from __future__ import annotations

import re

import pytest
import yaml

# Auth/permission language that an authless seed must NOT assert as a criterion.
_AUTH_LANGUAGE = re.compile(
    r"\b(auth\w*|login|logout|sign[\s-]?in|permission|role|rbac|token|oauth|"
    r"credential|password|session\s+cookie|access\s+control|unauthori[sz]ed)\b",
    re.IGNORECASE,
)
_PLACEHOLDER = re.compile(r"(TODO|TBD|FIXME|XXX|\{[^}]*\}|<[^>]*>|placeholder|lorem)", re.IGNORECASE)
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-AC-\d{3}$")
_VALID_CLASSES = {"machine", "manual"}


@pytest.fixture(scope="module")
def seed(output_dir):
    """The emitted feature-grain F1 seed under qa/.

    Skips — it does NOT fail — when the graded tree has no seed, because the
    four-file spec contract does not require one and a missing seed is far more
    often a harness fact than a model fact. But a skip here is no longer silent:
    the task's conftest turns any skip in this grade into exit code 40, so the
    three axes below read COULD NOT MEASURE instead of PASSED. If a seed IS
    present it must clear these bars.
    """
    qa = output_dir / "qa"
    matches = sorted(qa.glob("pass-bar-seed-*.yaml")) if qa.is_dir() else []
    if not matches:
        pytest.skip(
            f"no qa/pass-bar-seed-*.yaml in the graded tree ({output_dir}). This file is "
            "written by production's /feature-spec post-processor, not by the model, so "
            "its absence usually means the harness never ran that post-processor. Either "
            "way these three axes measured NOTHING — this grade is not a pass. See "
            "conftest.py and the scope doc's open ruling (§11.6)."
        )
    assert len(matches) == 1, f"expected exactly one feature-grain seed, found {[m.name for m in matches]}"
    return yaml.safe_load(matches[0].read_text(encoding="utf-8"))


def test_seed_wellformed(seed, paths):
    """Schema surface: version, slug agreement, criteria list present."""
    assert seed.get("format_version") == "2.0", f"seed format_version {seed.get('format_version')!r} != '2.0'"
    assert seed.get("feature_slug") == paths["slug"].name, (
        f"seed feature_slug {seed.get('feature_slug')!r} != {paths['slug'].name!r}"
    )
    assert isinstance(seed.get("criteria"), list), "seed has no criteria list"
    # It must NOT masquerade as a per-task F1 bar (no TASK-ID key).
    assert "task_id" not in seed, "the seed must never carry a TASK-ID — it is feature-grain, not a per-task F1"


def test_criteria_observability(seed, parsed):
    """Every criterion is a real, observable, mechanically-derived check —
    keyed id, non-placeholder text resolving to a gold scenario, valid class +
    evidence_kind. Non-degeneracy floor: at least one criterion."""
    criteria = seed.get("criteria") or []
    assert criteria, "degenerate seed — zero criteria (schema-green is not the bar; C-F8)"

    scenario_titles = {sc["name"].strip().lower() for sc in parsed["scenarios"]}
    findings: list[str] = []
    for c in criteria:
        cid, text = c.get("id", ""), (c.get("text") or "")
        if not _ID_RE.match(cid):
            findings.append(f"criterion id {cid!r} is not the mechanical <slug>-AC-NNN shape")
        if not text.strip() or _PLACEHOLDER.search(text):
            findings.append(f"{cid}: placeholder / empty criterion text {text!r}")
        elif text.strip().lower() not in scenario_titles:
            findings.append(f"{cid}: text {text!r} does not resolve to any gold scenario (invented, not derived)")
        if c.get("class") not in _VALID_CLASSES:
            findings.append(f"{cid}: class {c.get('class')!r} not in {_VALID_CLASSES}")
        if not (c.get("evidence_kind") or "").strip():
            findings.append(f"{cid}: empty evidence_kind — criterion is not observable")
    assert findings == [], "criteria-observability findings:\n" + "\n".join(findings)


def test_negative_path_honesty(seed):
    """auth_surface_bearing is an explicit bool with a basis; an authless seed
    (false) fabricates ZERO auth criteria (A-F2). The value is a deferred,
    human-confirmable determination — never an invented concrete auth row."""
    auth = seed.get("auth_surface_bearing")
    assert isinstance(auth, bool), f"auth_surface_bearing must be an explicit bool, got {auth!r}"
    assert (seed.get("auth_surface_basis") or "").strip(), "auth determination must carry a stated basis"

    if auth is False:
        offenders = [
            c.get("id") for c in (seed.get("criteria") or [])
            if _AUTH_LANGUAGE.search(c.get("text") or "")
        ]
        assert offenders == [], (
            "authless seed (auth_surface_bearing=false) asserts auth-bearing criteria "
            f"{offenders} — fabricated auth rows (A-F2 violation)"
        )
