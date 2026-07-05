"""Deterministic gates for the po-heldout-idea suite extension (FEAT-EVAL-IDEA).

Contract: docs/research/ideas/po-heldout-idea-extension-scope.md §2 (the pinned
instrument contracts — anchors schema, normalization, granularity, licensing,
scope-mode gates). New module by design: the frozen graders (po_contract.py,
grading.py) stay byte-identical; carried-over axes are reused by import.

stdlib only, like the frozen graders. Every gate consumes the PARSED payload
dict (grading.parse_response output) — never raw response text (§2.6).
All matcher functions return structured findings that NAME the offending
group / matched text / feature id — never a bare bool (§2.4/§2.5).
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

# §2.4: a single statement whose stuffing score (anchor groups matched in the
# statement AND asserted in requirement-bearing units) exceeds this licenses
# nothing. Calibrated pre-freeze against the frontier baseline (§4 of the
# extension scope); after the freeze this constant is immutable.
STUFFING_MAX_ASSERTED_GROUPS = 2

# §2.2: central normalization, applied identically to requirement-bearing
# units, license statements, and constraints_and_dependencies. NFKC folds
# fullwidth/compatibility forms; the table folds the unicode punctuation a
# local model's tokenizer plausibly emits. True homoglyphs are out of the
# threat model (the model under test never sees the anchors).
_CHAR_FOLD = str.maketrans({
    "‐": "-", "‑": "-", "‒": "-", "–": "-",
    "—": "-", "―": "-", "−": "-",
    " ": " ", " ": " ", " ": " ",
    "‘": "'", "’": "'", "“": '"', "”": '"',
})


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold().translate(_CHAR_FOLD)


# --- Anchor instrument -------------------------------------------------------

def load_anchors(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compile_anchors(anchors: dict) -> list[dict]:
    """Validate + compile an anchors file (§2.1). Malformed instrument data is
    an instrument defect: raise, never degrade silently."""
    groups = anchors.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ValueError("anchors: 'groups' must be a non-empty list")
    seen: set[str] = set()
    compiled = []
    for g in groups:
        gid = g.get("id")
        alternates = g.get("alternates")
        if not gid or not isinstance(gid, str):
            raise ValueError(f"anchors: group missing string id: {g!r}")
        if gid in seen:
            raise ValueError(f"anchors: duplicate group id {gid!r}")
        seen.add(gid)
        if not isinstance(alternates, list) or not alternates:
            raise ValueError(f"anchors: group {gid!r} has no alternates")
        compiled.append({
            "id": gid,
            "patterns": [re.compile(p, re.IGNORECASE) for p in alternates],
        })
    return compiled


def _first_match(group: dict, normalized_text: str) -> str | None:
    for rx in group["patterns"]:
        m = rx.search(normalized_text)
        if m:
            return m.group(0)
    return None


# --- Requirement-bearing units (§2.3) ----------------------------------------

def requirement_units(payload: dict) -> list[tuple[str, str]]:
    """Epic unit = name + bounded_context + description; feature unit = title +
    description + bounded_context + joined constraints; priority_rationale its
    own unit. feature_spec_inputs excluded — the frozen flatten-match rule
    already forces identity with epics[].features."""
    units: list[tuple[str, str]] = []
    for ei, epic in enumerate(payload.get("epics") or []):
        if not isinstance(epic, dict):
            continue
        parts = [epic.get(k) for k in ("name", "bounded_context", "description")]
        units.append((
            f"epic:{epic.get('id') or ei}",
            "\n".join(p for p in parts if isinstance(p, str)),
        ))
        for fi, feat in enumerate(epic.get("feature_stubs") or epic.get("features") or []):
            if not isinstance(feat, dict):
                continue
            parts = [feat.get(k) for k in ("title", "intent", "description", "bounded_context")]
            parts.append("\n".join(
                c for c in (feat.get("constraints") or []) if isinstance(c, str)
            ))
            units.append((
                f"feature:{feat.get('feature_id') or fi}",
                "\n".join(p for p in parts if isinstance(p, str) and p),
            ))
    rationale = payload.get("priority_rationale")
    if isinstance(rationale, str) and rationale.strip():
        units.append(("priority_rationale", rationale))
    return units


def _license_statements(payload: dict) -> list[str]:
    """License sources (§2.4): assumptions[].statement and open_questions[]
    entries. impact_if_wrong deliberately excluded — the falsifiable claim
    lives in the statement (calibration watch item, extension scope §4)."""
    texts: list[str] = []
    for a in payload.get("assumptions") or []:
        if isinstance(a, dict) and isinstance(a.get("statement"), str):
            texts.append(a["statement"])
    for q in payload.get("open_questions") or []:
        if isinstance(q, str):
            texts.append(q)
    return texts


# --- Gate: invented requirements (po-held-005-idea) ---------------------------

def find_unlicensed_inventions(
    payload: dict, anchors: dict, stuffing_max: int | None = None
) -> list[dict]:
    """§2.4: an anchor group matching in a requirement-bearing unit must
    co-match (per-GROUP: any alternate) in >=1 assumption statement or open
    question, else it is an anchor-detected unlicensed invention. A statement
    whose stuffing score exceeds the threshold licenses nothing."""
    max_groups = STUFFING_MAX_ASSERTED_GROUPS if stuffing_max is None else stuffing_max
    groups = compile_anchors(anchors)

    asserted: dict[str, list[dict]] = {}
    for group in groups:
        for label, raw in requirement_units(payload):
            matched = _first_match(group, normalize(raw))
            if matched:
                asserted.setdefault(group["id"], []).append(
                    {"unit": label, "matched_text": matched}
                )
    if not asserted:
        return []

    licensed: set[str] = set()
    for statement in _license_statements(payload):
        text = normalize(statement)
        statement_groups = {g["id"] for g in groups if _first_match(g, text)}
        if len(statement_groups & set(asserted)) > max_groups:
            continue  # keyword salad: this statement licenses nothing (§2.4)
        licensed |= statement_groups

    findings = []
    for gid in sorted(set(asserted) - licensed):
        for hit in asserted[gid]:
            findings.append({"group": gid, **hit})
    return findings


# --- Gate: constraint carried (po-held-006-scope) ------------------------------

def check_constraint_carried(payload: dict, anchors: dict) -> list[dict]:
    """§2.5: ALL constraint-anchor groups must match the JOINED
    constraints_and_dependencies text. A dropped group is a finding."""
    groups = compile_anchors(anchors)
    joined = normalize("\n".join(
        e for e in (payload.get("constraints_and_dependencies") or [])
        if isinstance(e, str)
    ))
    return [
        {"group": g["id"], "defect": "constraint_not_carried"}
        for g in groups
        if not _first_match(g, joined)
    ]


# --- Reference roadmap + scope-mode selection gates ----------------------------

def reference_features(reference: dict) -> dict[str, dict]:
    feats: dict[str, dict] = {}
    for epic in reference.get("epics") or []:
        for f in epic.get("features") or []:
            feats[f["feature_id"]] = {
                "title": f.get("title", ""),
                "bounded_context": f.get("bounded_context", ""),
                "depends_on": [d for d in (f.get("depends_on") or []) if isinstance(d, str)],
            }
    return feats


def extract_selection(payload: dict) -> dict:
    """Selection view of a scope-mode response: ids, response-declared deps,
    and per-feature identity fields for the subset gate."""
    selected_ids: list[str] = []
    response_depends_on: dict[str, list[str]] = {}
    response_features: dict[str, dict] = {}
    for epic in payload.get("epics") or []:
        for f in epic.get("features") or []:
            fid = f.get("feature_id")
            if not isinstance(fid, str):
                continue
            selected_ids.append(fid)
            response_depends_on[fid] = [
                d for d in (f.get("depends_on") or []) if isinstance(d, str)
            ]
            response_features[fid] = {
                "title": f.get("title", ""),
                "bounded_context": f.get("bounded_context", ""),
            }
    return {
        "selected_ids": selected_ids,
        "response_depends_on": response_depends_on,
        "response_features": response_features,
    }


def check_selection_subset(selection: dict, reference: dict) -> list[dict]:
    """§2.5 subset: every selected id exists in the reference AND carries the
    reference's title and bounded_context under normalization (content-swap
    under a legitimate id is invention). description deliberately unchecked —
    player_scope.md licenses reduced-scope rewrites (Coach territory)."""
    ref = reference_features(reference)
    findings = []
    for fid in sorted(selection.get("response_features", {})):
        meta = selection["response_features"][fid]
        if fid not in ref:
            findings.append({"feature_id": fid, "defect": "invented_feature"})
            continue
        for field in ("title", "bounded_context"):
            if normalize(meta.get(field, "")) != normalize(ref[fid][field]):
                findings.append({
                    "feature_id": fid,
                    "defect": f"content_swap:{field}",
                    "response_value": meta.get(field, ""),
                    "reference_value": ref[fid][field],
                })
    return findings


def check_dependency_closure(selection: dict, reference: dict) -> list[dict]:
    """§2.5 closure, computed against the REFERENCE graph (TASK-REV-09AB
    red-team B1): for every selected id, every reference-declared direct
    dependency must be selected — applied to all selected features this is
    inductively equivalent to transitive closure. Response depends_on entries
    must additionally resolve to selected ids. An emptied response depends_on
    therefore changes nothing."""
    ref = reference_features(reference)
    selected = set(selection.get("selected_ids") or [])
    findings = []
    for fid in sorted(selected):
        for dep in ref.get(fid, {}).get("depends_on", []):
            if dep not in selected:
                findings.append({
                    "feature_id": fid,
                    "defect": "missing_prerequisite",
                    "prerequisite": dep,
                })
    for fid in sorted(selection.get("response_depends_on") or {}):
        for dep in selection["response_depends_on"][fid]:
            if dep not in selected:
                findings.append({
                    "feature_id": fid,
                    "defect": "dangling_depends_on",
                    "prerequisite": dep,
                })
    return findings


def dependency_free_ids(reference: dict) -> list[str]:
    return sorted(
        fid for fid, meta in reference_features(reference).items()
        if not meta["depends_on"]
    )


def first_chained_pair(reference: dict) -> tuple[str, str] | None:
    """(prerequisite_id, dependent_id) for the first reference-declared edge —
    test helper for closure fixtures."""
    for fid, meta in sorted(reference_features(reference).items()):
        for dep in meta["depends_on"]:
            return (dep, fid)
    return None


def reference_graph_sanity(reference: dict) -> list[str]:
    """Instrument sanity (§2.5): unique ids, resolvable deps, acyclic,
    >=1 dependency-free feature. The checksum pin covers drift; this covers
    initial malformation."""
    issues: list[str] = []
    seen: set[str] = set()
    for epic in reference.get("epics") or []:
        for f in epic.get("features") or []:
            fid = f.get("feature_id")
            if fid in seen:
                issues.append(f"duplicate feature_id {fid!r}")
            seen.add(fid)
    feats = reference_features(reference)
    for fid, meta in sorted(feats.items()):
        for dep in meta["depends_on"]:
            if dep not in feats:
                issues.append(f"{fid}: depends_on {dep!r} does not exist in the reference")
    if not dependency_free_ids(reference):
        issues.append("no dependency-free feature (minimal-selection boundary needs one)")

    state: dict[str, int] = {}  # 0=visiting, 1=done

    def visit(fid: str, stack: list[str]) -> None:
        if state.get(fid) == 1:
            return
        if state.get(fid) == 0:
            issues.append("dependency cycle: " + " -> ".join(stack + [fid]))
            return
        state[fid] = 0
        for dep in feats.get(fid, {}).get("depends_on", []):
            if dep in feats:
                visit(dep, stack + [fid])
        state[fid] = 1

    for fid in sorted(feats):
        visit(fid, [])
    return issues
