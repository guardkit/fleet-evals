"""Grading utilities for the PO held-out suite: serving-shape extraction,
citation grounding, and coverage-vs-reference matching.

The extraction cascade is faithful to the serving parse flow pinned 2026-07-03:
  think-block strip     specialist-agent orchestrator/think_block.py:49-153
  _extract_json cascade specialist-agent roles/product_owner/handler.py:535-609
(The gate is stricter than the runtime on one point, by design: the runtime
tolerates a *missing* think block at parse time and lets the Coach fail it;
the gate requires exactly one well-formed think block — Decision A 2026-07-02
makes `<think>` + one fenced JSON the fine-tune's serving shape.)

Stdlib only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)  # handler.py:568 (byte-identical)


class ShapeError(Exception):
    """Raised when raw output does not have the serving shape."""


def _think_spans_outside_fences(raw: str) -> list[tuple[int, int, str]]:
    """(pos, end, tag) for every <think>/</think> tag outside ``` fences —
    the same fence-awareness as think_block.py:49-153 (literal think tags inside
    fenced JSON/examples are content, not protocol)."""
    spans = []
    in_fence = False
    i = 0
    while i < len(raw):
        if raw.startswith("```", i):
            in_fence = not in_fence
            i += 3
            continue
        if not in_fence:
            for tag in ("</think>", "<think>"):
                if raw.startswith(tag, i):
                    spans.append((i, i + len(tag), tag))
                    i += len(tag)
                    break
            else:
                i += 1
            continue
        i += 1
    return spans


def split_think_block(raw: str) -> tuple[str, str]:
    """Return (think_content, remainder). Requires exactly one well-formed,
    lowercase, top-level <think>...</think> block (Decision A serving shape),
    counted fence-aware — literal think tags inside the JSON payload are content
    (think_block.py:120-132). Raises ShapeError otherwise."""
    tags = _think_spans_outside_fences(raw)
    opens = [t for t in tags if t[2] == "<think>"]
    closes = [t for t in tags if t[2] == "</think>"]
    if not opens:
        raise ShapeError("no <think> block found — serving shape requires one")
    if len(opens) > 1 or len(closes) > 1:
        raise ShapeError(
            f"expected exactly one top-level think block, found {len(opens)} opens / {len(closes)} closes"
        )
    if not closes:
        # think_block.py returns the original on unterminated <think>;
        # for the gate an unterminated block is a shape failure outright.
        raise ShapeError("unterminated <think> tag")
    (o_start, o_end, _), (c_start, c_end, _) = opens[0], closes[0]
    if c_start < o_start:
        raise ShapeError("</think> appears before <think>")
    think = raw[o_end:c_start]
    remainder = raw[:o_start] + raw[c_end:]
    return think, remainder


def extract_json_payload(text: str) -> dict:
    """The _extract_json cascade (handler.py:557-604): whole-text json.loads,
    then FIRST ``` fence, then leading-object raw_decode (trailing text tolerated).
    Runtime-faithful, including the no-fallback-after-broken-fence behaviour —
    a fence whose content does not parse is a shape failure at serving too."""
    stripped = text.strip()
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    m = FENCE_RE.search(text)
    if m:
        candidate = m.group(1).strip()
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError as e:
            raise ShapeError(f"first fenced payload is not valid JSON: {e}") from e
        if not isinstance(obj, dict):
            raise ShapeError("fenced payload is not a JSON object")
        return obj
    if stripped.startswith("{"):
        try:
            obj, _end = json.JSONDecoder().raw_decode(stripped)
        except json.JSONDecodeError as e:
            raise ShapeError(f"leading JSON object does not parse: {e}") from e
        if isinstance(obj, dict):
            return obj
    raise ShapeError("no valid JSON object found in output")


def parse_response(raw: str) -> dict:
    """Serving shape: exactly one think block, then exactly one JSON object."""
    _think, remainder = split_think_block(raw)
    return extract_json_payload(remainder)


def load_response(output_dir: Path) -> str:
    p = Path(output_dir) / "response.txt"
    if not p.exists():
        raise FileNotFoundError(f"candidate artifact not found: {p}")
    return p.read_text(encoding="utf-8")


# --- Grounding -------------------------------------------------------------

def load_corpus_manifest(corpus_dir: Path) -> set[str]:
    """Filenames pinned by input/corpus/MANIFEST.sha256."""
    manifest = Path(corpus_dir) / "MANIFEST.sha256"
    names = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            names.add(line.split(maxsplit=1)[1].lstrip("*"))
    return names


def collect_cited_documents(obj) -> set[str]:
    """Every document name the output claims came from the corpus:
    cited_docs and source_documents entries are contractually corpus filenames, so
    EVERY string entry is collected (no extension heuristic — a fabricated name
    without '.md' is still a fabrication); source_citations[].document and
    field_citations[*][].document and {filename, contribution} objects likewise.
    suggested_context_files may legitimately name repo/code paths, so only its
    markdown-named entries are held to the manifest."""
    cited: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for key in ("cited_docs", "source_documents"):
                v = node.get(key)
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str) and item.strip():
                            cited.add(item)
                        elif isinstance(item, dict) and isinstance(item.get("filename"), str):
                            cited.add(item["filename"])
            scf = node.get("suggested_context_files")
            if isinstance(scf, list):
                for item in scf:
                    if isinstance(item, str) and item.endswith(".md"):
                        cited.add(item)
            doc = node.get("document")
            if isinstance(doc, str):
                cited.add(doc)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(obj)
    return cited


def fabricated_references(obj, corpus_names: set[str]) -> list[str]:
    return sorted(collect_cited_documents(obj) - corpus_names)


# --- Coverage-vs-reference --------------------------------------------------

def load_checklist(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def structural_units(obj) -> list[str]:
    """One text unit per epic (name + bounded_context + description) and one per
    feature/stub (title + intent/description + bounded_context). feature_spec_inputs
    is excluded — it mirrors the epic features and would double-count them."""
    units: list[str] = []
    for epic in obj.get("epics") or []:
        if not isinstance(epic, dict):
            continue
        epic_parts = [epic.get(k) for k in ("name", "bounded_context", "description")]
        units.append("\n".join(p for p in epic_parts if isinstance(p, str)))
        for feat in epic.get("feature_stubs") or epic.get("features") or []:
            if not isinstance(feat, dict):
                continue
            feat_parts = [feat.get(k) for k in ("title", "intent", "description", "bounded_context")]
            units.append("\n".join(p for p in feat_parts if isinstance(p, str)))
    return units


def coverage_report(obj, checklist: dict) -> dict:
    """Per-area: which anchor patterns matched, and in how many distinct structural
    units. An area is covered when >= `min_distinct_anchors` (default 2) distinct
    patterns match AND the matches span >= 2 distinct epics/features — a single
    keyword-stuffed field cannot cover an area, let alone all of them."""
    units = structural_units(obj)
    report = {}
    for area in checklist["areas"]:
        matched = []
        matching_units = set()
        for pattern in area["anchors_any"]:
            rx = re.compile(pattern, re.IGNORECASE)
            hit_units = {i for i, u in enumerate(units) if rx.search(u)}
            if hit_units:
                matched.append(pattern)
                matching_units |= hit_units
        needed = area.get("min_distinct_anchors", 2)
        report[area["id"]] = {
            "required": area["required"],
            "matched_anchors": matched,
            "matching_units": len(matching_units),
            "covered": len(matched) >= needed and len(matching_units) >= 2,
        }
    return report


def uncovered_required(report: dict) -> list[str]:
    return sorted(a for a, r in report.items() if r["required"] and not r["covered"])


def structure_counts(obj) -> tuple[int, int]:
    """(epic_count, feature_count) for EpicPlan (stubs) or ProductRoadmap (features)."""
    epics = obj.get("epics") or []
    features = 0
    for e in epics:
        if isinstance(e, dict):
            features += len(e.get("feature_stubs") or e.get("features") or [])
    return len(epics), features
