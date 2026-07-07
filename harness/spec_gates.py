"""Deterministic gates for the po-heldout-spec suite extension (FEAT-EVAL-SPEC).

Contract sources (both pinned; any divergence is a defect here, not there):
  - specialist-agent/docs/design/contracts/CONTRACT-feature-spec-plan-outputs.md
    (WS1 Session B pin, 2026-07-07) — the three-file /feature-spec contract
    (Part A) and the feature/task/wave YAML + plan-body obligations (Part B).
  - guardkit @ 28587b61: installer/core/commands/feature-spec.md (ce914f7c),
    feature-plan.md (5ad48fcf), lib/bdd_linker.py apply_mapping (tag-insertion
    shape), orchestrator/feature_loader.py (schema oracle, exercised via the
    installed `guardkit feature validate` CLI — never re-implemented here).

New module by design: the frozen graders (po_contract.py, grading.py) and the
frozen idea extension (idea_gates.py) stay byte-identical; the anchor
instrument (compile/normalize/match + anti-stuffing licensing) is reused from
idea_gates by import.

Dependency posture (documented divergence from the frozen suite's stdlib-only
rule): the plan-side artifacts ARE YAML, and guardkit's own oracle parses them
with yaml.safe_load (feature_loader.py) — this module uses the same parser for
parse-parity rather than hand-rolling a YAML subset that could disagree with
the oracle. The `guardkit` CLI (installed, resolves to the pinned checkout) is
invoked as a subprocess for schema+structural validation; a missing CLI is an
instrument error that names the pin, never a silent skip.

Every matcher returns structured findings that NAME the offending scenario /
step / task / file — never a bare bool (house rule, extension scope §2.4).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from harness.idea_gates import (
    STUFFING_MAX_ASSERTED_GROUPS,
    _first_match,
    compile_anchors,
    load_anchors,
    normalize,
)

__all__ = [
    "STUFFING_MAX_ASSERTED_GROUPS",
    "compile_anchors",
    "load_anchors",
    "normalize",
]

STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")
CATEGORY_TAGS = ("@key-example", "@boundary", "@negative", "@edge-case")
SPEC_FILE_SUFFIXES = (".feature", "_assumptions.yaml", "_summary.md")
TASK_TAG_RE = re.compile(r"^\s*@task:(TASK-[A-Za-z0-9._-]+)\s*$")
ASSUM_ANNOTATION_RE = re.compile(
    r"#\s*\[ASSUMPTION:\s*confidence=(\w+)\s*\]"
)
# task_types.py @ 28587b61: canonical values + normalised aliases.
VALID_TASK_TYPES = {
    "scaffolding", "feature", "infrastructure", "integration",
    "documentation", "testing", "refactor", "declarative", "operator_handoff",
}
TASK_TYPE_ALIASES = {
    "implementation": "feature", "bug-fix": "feature", "bug_fix": "feature",
    "enhancement": "feature", "benchmark": "testing",
    "research": "documentation", "config": "declarative", "dto": "declarative",
}


def _yaml():
    """guardkit's own parser (feature_loader.py uses yaml.safe_load); imported
    lazily so the module stays importable for spec-side-only use if PyYAML is
    ever absent — the plan gates then fail loudly with the reason."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - environment defect
        raise RuntimeError(
            "PyYAML is required by the po-heldout-spec plan gates (parse-parity "
            "with guardkit feature_loader.py yaml.safe_load) — pip install pyyaml"
        ) from exc
    return yaml


# --- Spec artifact discovery (Part A directory layout) -------------------------

def find_spec_dir(output_root: Path) -> Path:
    """The answer sheet mirrors the tool's repo view: {root}/features/{slug}/.
    Exactly one slug directory is the contract; zero or many is a finding
    raised by the caller via spec_layout_findings."""
    features = Path(output_root) / "features"
    if not features.is_dir():
        raise FileNotFoundError(f"no features/ directory in answer sheet: {output_root}")
    slugs = sorted(p for p in features.iterdir() if p.is_dir())
    if len(slugs) != 1:
        raise FileNotFoundError(
            f"expected exactly one feature directory under {features}, "
            f"found {[p.name for p in slugs]}"
        )
    return slugs[0]


def spec_layout_findings(output_root: Path) -> list[dict]:
    """Part A: exactly three files, pinned names, nothing else (no step
    definitions, no support files — behavioural rule 'purely additive')."""
    findings: list[dict] = []
    try:
        spec_dir = find_spec_dir(output_root)
    except FileNotFoundError as exc:
        return [{"defect": "layout", "detail": str(exc)}]
    slug = spec_dir.name
    expected = {slug + s for s in SPEC_FILE_SUFFIXES}
    actual = {p.name for p in spec_dir.iterdir()}
    for name in sorted(expected - actual):
        findings.append({"defect": "missing_file", "file": name})
    for name in sorted(actual - expected):
        findings.append({"defect": "unexpected_file", "file": name})
    # Nothing else anywhere under features/ (the tool writes the triple only).
    features = Path(output_root) / "features"
    for p in sorted(features.rglob("*")):
        if p.is_file() and p.parent != spec_dir:
            findings.append({"defect": "unexpected_file", "file": str(p.relative_to(features))})
    return findings


def spec_paths(output_root: Path) -> dict[str, Path]:
    spec_dir = find_spec_dir(output_root)
    slug = spec_dir.name
    return {
        "slug": spec_dir,
        "feature": spec_dir / f"{slug}.feature",
        "assumptions": spec_dir / f"{slug}_assumptions.yaml",
        "summary": spec_dir / f"{slug}_summary.md",
    }


# --- Gherkin mini-parser --------------------------------------------------------
#
# Purpose-built for the gate axes (header block, tags, # Why:, step lines,
# single-physical-line invariant, per-scenario text units) — NOT a general
# Gherkin implementation. The full official-parser check is the serving-side
# backstop (feature_spec_normalize, run by the tool before it returns); this
# parser is the gate-side floor and is deliberately stricter than nothing and
# weaker than the official grammar (accepted residual, scope §5).

def _classify(line: str, in_docstring: bool) -> str:
    s = line.strip()
    if in_docstring:
        return "docstring-open" if s.startswith(('"""', "```")) else "docstring"
    if not s:
        return "blank"
    if s.startswith(('"""', "```")):
        return "docstring-open"
    if s.startswith("#"):
        return "comment"
    if s.startswith("@"):
        return "tag"
    if s.startswith("|"):
        return "table"
    for kw in ("Feature:", "Background:", "Scenario Outline:", "Scenario:",
               "Examples:", "Rule:"):
        if s.startswith(kw):
            return "keyword:" + kw.rstrip(":")
    first = s.split(" ", 1)[0]
    if first in STEP_KEYWORDS:
        return "step"
    return "other"


def parse_feature(text: str) -> dict:
    """Parse a .feature file into header comments, feature block, scenarios,
    and structural findings. Scenarios carry: name, keyword, tags (own block),
    leading comments, steps (raw lines), unit_text (name + steps + table cells
    + docstring content — comments and tags excluded, so an assumption
    annotation can never assert its own anchor), and wrapped-continuation
    findings (the single-physical-line invariant, Part A)."""
    lines = text.splitlines()
    findings: list[dict] = []
    header_comments: list[str] = []
    feature: dict = {"name": None, "tags": [], "description": []}
    scenarios: list[dict] = []
    background: dict | None = None

    current: dict | None = None  # scenario or background being filled
    pending_tags: list[str] = []
    pending_comments: list[str] = []
    seen_feature = False
    in_docstring = False
    docstring_delim = ""
    steps_started = False
    in_examples = False

    for i, line in enumerate(lines, start=1):
        kind = _classify(line, in_docstring)

        if kind == "docstring-open":
            s = line.strip()
            if not in_docstring:
                in_docstring, docstring_delim = True, s[:3]
            elif s.startswith(docstring_delim):
                in_docstring = False
            if current is not None:
                current["unit_lines"].append("")
            continue
        if kind == "docstring":
            if current is not None:
                current["unit_lines"].append(line.strip())
            continue

        if kind == "comment":
            # Attribute both ways: to the NEXT scenario (the `# Why:` /
            # annotation-above-tags placement) and to the ENCLOSING scenario
            # (the annotation-above-the-affected-step placement) — the pinned
            # template shows both shapes and both gates only ask "does this
            # scenario's block carry the comment".
            if not seen_feature:
                header_comments.append(line.strip())
            else:
                pending_comments.append(line.strip())
                if current is not None and "body_comments" in current:
                    current["body_comments"].append(line.strip())
            continue
        if kind == "blank":
            continue
        if kind == "tag":
            tags = [t for t in line.split() if t.startswith("@")]
            junk = [t for t in line.split() if not t.startswith("@")]
            if junk:
                findings.append({"defect": "malformed_tag_line", "line": i, "text": line.strip()})
            pending_tags.extend(tags)
            continue

        if kind == "keyword:Feature":
            if seen_feature:
                findings.append({"defect": "multiple_feature_blocks", "line": i})
            seen_feature = True
            feature["name"] = line.split(":", 1)[1].strip()
            feature["tags"] = pending_tags
            pending_tags, pending_comments = [], []
            current, steps_started, in_examples = None, False, False
            continue
        if kind == "keyword:Background":
            background = {"steps": [], "unit_lines": [], "line": i}
            current, steps_started, in_examples = background, False, False
            pending_tags, pending_comments = [], []
            continue
        if kind in ("keyword:Scenario", "keyword:Scenario Outline"):
            current = {
                "keyword": kind.split(":", 1)[1],
                "name": line.split(":", 1)[1].strip(),
                "tags": pending_tags,
                "comments": pending_comments,
                "body_comments": [],
                "steps": [],
                "unit_lines": [line.split(":", 1)[1].strip()],
                "line": i,
            }
            scenarios.append(current)
            pending_tags, pending_comments = [], []
            steps_started, in_examples = False, False
            continue
        if kind == "keyword:Examples":
            in_examples = True
            continue
        if kind == "keyword:Rule":
            findings.append({"defect": "rule_block_not_in_contract", "line": i})
            continue

        if kind == "step":
            if current is None:
                findings.append({"defect": "step_outside_scenario", "line": i, "text": line.strip()})
            else:
                current["steps"].append(line.strip())
                current["unit_lines"].append(line.strip())
                steps_started = True
            continue
        if kind == "table":
            if current is not None:
                current["unit_lines"].append(line.strip())
            continue

        # kind == "other": free text. Legal as Feature/Scenario description
        # (before any step); after a step it is a wrapped step continuation —
        # exactly what feature_spec_normalize exists to reject (Part A).
        if not seen_feature:
            findings.append({"defect": "text_before_feature", "line": i, "text": line.strip()})
        elif current is None:
            feature["description"].append(line.strip())
        elif steps_started or in_examples:
            findings.append({
                "defect": "wrapped_step_continuation",
                "line": i,
                "text": line.strip(),
                "scenario": current.get("name", "(background)"),
            })
        else:
            current["unit_lines"].append(line.strip())

    if not seen_feature:
        findings.append({"defect": "no_feature_block"})
    if in_docstring:
        findings.append({"defect": "unterminated_docstring"})

    for sc in scenarios:
        sc["unit_text"] = "\n".join(sc["unit_lines"])
    if background is not None:
        background["unit_text"] = "\n".join(background["unit_lines"])

    return {
        "header_comments": header_comments,
        "feature": feature,
        "background": background,
        "scenarios": scenarios,
        "findings": findings,
    }


def wrapped_step_findings(parsed: dict) -> list[dict]:
    return [f for f in parsed["findings"] if f["defect"] == "wrapped_step_continuation"]


def header_block(parsed: dict) -> dict[str, str]:
    """The five pinned header comment fields (Part A.1), keyed lowercase."""
    fields: dict[str, str] = {}
    for c in parsed["header_comments"]:
        body = c.lstrip("#").strip()
        if body.startswith("Generated by"):
            fields["generated_by"] = body
        else:
            for key in ("Feature", "Stack", "Assumptions", "Generated"):
                if body.startswith(key + ":"):
                    fields[key.lower()] = body.split(":", 1)[1].strip()
    return fields


def scenario_task_tags(parsed: dict) -> dict[str, list[str]]:
    """scenario name -> [@task ids] (Step 11 linkage view)."""
    out: dict[str, list[str]] = {}
    for sc in parsed["scenarios"]:
        ids = [t.split(":", 1)[1] for t in sc["tags"] if t.startswith("@task:")]
        out[sc["name"]] = ids
    return out


# --- Domain-language banlist (Part A structural rules) --------------------------

def find_banned_language(parsed: dict, banlist: dict) -> list[dict]:
    """Implementation language in scenario STEPS (the pinned scope: status
    codes, SQL, file paths, JSON bodies, named infrastructure — template
    §Domain Language). Comments, docstrings and Examples cells are exempt by
    design; the banlist file is the transparent instrument (anchors schema)."""
    groups = compile_anchors(banlist)
    findings = []
    for sc in parsed["scenarios"]:
        for step in sc["steps"]:
            text = normalize(step)
            for g in groups:
                matched = _first_match(g, text)
                if matched:
                    findings.append({
                        "group": g["id"],
                        "scenario": sc["name"],
                        "step": step,
                        "matched_text": matched,
                    })
    return findings


def implementation_comment_findings(text: str) -> list[dict]:
    """`# Implementation:` comments are banned anywhere in the file
    (behavioural rule: never reference implementation files)."""
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        if re.match(r"\s*#\s*Implementation\s*:", line):
            out.append({"defect": "implementation_comment", "line": i, "text": line.strip()})
    return out


# --- Assumptions manifest (Part A.2) --------------------------------------------

MANIFEST_ENTRY_FIELDS = ("id", "scenario", "assumption", "confidence", "basis", "human_response")
CONFIDENCE_VALUES = {"high", "medium", "low"}


def load_assumptions_manifest(path: Path) -> dict:
    data = _yaml().safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("assumptions manifest is not a YAML mapping")
    return data


def manifest_schema_findings(manifest: dict, scenario_names: set[str]) -> list[dict]:
    """Every field required on every entry; ids ASSUM-NNN sequential from 001;
    scenario titles must resolve against the .feature (referential integrity);
    human_response ∈ {confirmed, deferred, overridden: {value}}."""
    findings: list[dict] = []
    for key, kind in (("feature", str), ("generated", str), ("stack", str),
                      ("review_required", bool)):
        if not isinstance(manifest.get(key), kind):
            findings.append({"defect": "top_level_field", "field": key,
                             "value": repr(manifest.get(key))})
    entries = manifest.get("assumptions")
    if not isinstance(entries, list):
        return findings + [{"defect": "assumptions_not_a_list"}]
    for n, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            findings.append({"defect": "entry_not_a_mapping", "index": n})
            continue
        eid = entry.get("id")
        for field in MANIFEST_ENTRY_FIELDS:
            v = entry.get(field)
            if not isinstance(v, str) or not v.strip():
                findings.append({"defect": "entry_field", "id": eid or f"#{n}", "field": field})
        if isinstance(eid, str) and eid != f"ASSUM-{n:03d}":
            findings.append({"defect": "id_not_sequential", "id": eid,
                             "expected": f"ASSUM-{n:03d}"})
        conf = entry.get("confidence")
        if isinstance(conf, str) and conf not in CONFIDENCE_VALUES:
            findings.append({"defect": "confidence_enum", "id": eid, "value": conf})
        hr = entry.get("human_response")
        if isinstance(hr, str) and hr not in ("confirmed", "deferred") \
                and not hr.startswith("overridden: "):
            findings.append({"defect": "human_response_enum", "id": eid, "value": hr})
        sc = entry.get("scenario")
        if isinstance(sc, str) and sc.strip() and sc not in scenario_names:
            findings.append({"defect": "scenario_not_in_feature", "id": eid, "scenario": sc})
    return findings


def annotation_findings(parsed: dict, manifest: dict) -> list[dict]:
    """Part A: 'Assumption annotations are included as comments above the
    affected scenario step.' Every manifest entry's scenario block must carry
    ≥1 `# [ASSUMPTION: confidence=...]` annotation with a valid confidence."""
    findings: list[dict] = []
    per_scenario: dict[str, list[str]] = {}
    for sc in parsed["scenarios"]:
        per_scenario[sc["name"]] = [
            m.group(1)
            for c in sc["comments"] + sc.get("body_comments", [])
            for m in [ASSUM_ANNOTATION_RE.search(c)] if m
        ]
    for sc in parsed["scenarios"]:
        for c in sc["comments"] + sc.get("body_comments", []):
            m = ASSUM_ANNOTATION_RE.search(c)
            if m and m.group(1) not in CONFIDENCE_VALUES:
                findings.append({"defect": "annotation_confidence_enum",
                                 "scenario": sc["name"], "value": m.group(1)})
    for entry in manifest.get("assumptions") or []:
        if not isinstance(entry, dict):
            continue
        sc = entry.get("scenario")
        if isinstance(sc, str) and sc in per_scenario and not per_scenario[sc]:
            findings.append({"defect": "annotation_missing", "id": entry.get("id"),
                             "scenario": sc})
    return findings


# --- Summary coherence (Part A.3) ------------------------------------------------

SUMMARY_HEADER_RE = {
    "stack": re.compile(r"^\*\*Stack\*\*:\s*(.+)$", re.MULTILINE),
    "generated": re.compile(r"^\*\*Generated\*\*:\s*(.+)$", re.MULTILINE),
    "scenarios": re.compile(
        r"^\*\*Scenarios\*\*:\s*(\d+)\s+total\s*\((\d+)\s+smoke,\s*(\d+)\s+regression\)",
        re.MULTILINE),
    "assumptions": re.compile(
        r"^\*\*Assumptions\*\*:\s*(\d+)\s+total\s*\((\d+)\s+high\s*/\s*(\d+)\s+medium\s*/\s*(\d+)\s+low",
        re.MULTILINE),
    "review_required": re.compile(r"^\*\*Review required\*\*:\s*(Yes|No)", re.MULTILINE),
}
CATEGORY_TABLE_ROWS = {
    "@key-example": re.compile(r"\|\s*Key examples \(@key-example\)\s*\|\s*(\d+)\s*\|"),
    "@boundary": re.compile(r"\|\s*Boundary conditions \(@boundary\)\s*\|\s*(\d+)\s*\|"),
    "@negative": re.compile(r"\|\s*Negative cases \(@negative\)\s*\|\s*(\d+)\s*\|"),
    "@edge-case": re.compile(r"\|\s*Edge cases \(@edge-case\)\s*\|\s*(\d+)\s*\|"),
}


def parse_summary(text: str) -> dict:
    out: dict = {"category_counts": {}}
    for key, rx in SUMMARY_HEADER_RE.items():
        m = rx.search(text)
        out[key] = m.groups() if m and len(m.groups()) > 1 else (m.group(1) if m else None)
    for tag, rx in CATEGORY_TABLE_ROWS.items():
        m = rx.search(text)
        out["category_counts"][tag] = int(m.group(1)) if m else None
    return out


def tag_count(parsed: dict, tag: str) -> int:
    return sum(1 for sc in parsed["scenarios"] if tag in sc["tags"])


def is_full_iso_timestamp(value: str) -> bool:
    """Part C deviation 1 is gold-only: NEW output must carry a full ISO 8601
    timestamp (date + time), not a bare date."""
    import datetime
    v = value.strip().replace("Z", "+00:00")
    if "T" not in v and " " not in v:
        return False
    try:
        datetime.datetime.fromisoformat(v)
    except ValueError:
        return False
    return True


# --- Invented-requirement gate (spec-side, mirrors idea_gates §2.4) ---------------

def spec_requirement_units(parsed: dict) -> list[tuple[str, str]]:
    """Requirement-bearing units of a spec: the Feature block (name + story
    description), the Background, and each scenario (title + steps + tables +
    docstrings). Comments and tags are EXCLUDED so license annotations can
    never assert their own anchor."""
    units: list[tuple[str, str]] = []
    feat = parsed["feature"]
    feat_text = "\n".join([feat.get("name") or ""] + feat.get("description", []))
    if feat_text.strip():
        units.append(("feature", feat_text))
    if parsed.get("background"):
        units.append(("background", parsed["background"]["unit_text"]))
    for sc in parsed["scenarios"]:
        units.append((f"scenario:{sc['name']}", sc["unit_text"]))
    return units


def manifest_license_texts(manifest: dict) -> list[str]:
    """License source = the manifest's `assumption` statements (the canonical
    record of every inferred value, Part A.2). Inline annotations are
    presentation of the same rows; `basis` deliberately excluded — the
    falsifiable claim lives in the assumption text (G-I precedent)."""
    return [
        e["assumption"]
        for e in (manifest.get("assumptions") or [])
        if isinstance(e, dict) and isinstance(e.get("assumption"), str)
    ]


def find_unlicensed_spec_inventions(
    parsed: dict, manifest: dict, anchors: dict, stuffing_max: int | None = None
) -> list[dict]:
    """An anchor group matching in any requirement-bearing spec unit must
    co-match in ≥1 manifest assumption statement (per-GROUP licensing), else it
    is an anchor-detected unlicensed invention. Anti-stuffing verbatim from the
    frozen idea gate: one statement asserting > max body-asserted groups
    licenses none of them."""
    max_groups = STUFFING_MAX_ASSERTED_GROUPS if stuffing_max is None else stuffing_max
    groups = compile_anchors(anchors)

    asserted: dict[str, list[dict]] = {}
    for group in groups:
        for label, raw in spec_requirement_units(parsed):
            matched = _first_match(group, normalize(raw))
            if matched:
                asserted.setdefault(group["id"], []).append(
                    {"unit": label, "matched_text": matched}
                )
    if not asserted:
        return []

    licensed: set[str] = set()
    for statement in manifest_license_texts(manifest):
        text = normalize(statement)
        statement_groups = {g["id"] for g in groups if _first_match(g, text)}
        if len(statement_groups & set(asserted)) > max_groups:
            continue  # keyword salad licenses nothing (idea_gates §2.4)
        licensed |= statement_groups

    findings = []
    for gid in sorted(set(asserted) - licensed):
        for hit in asserted[gid]:
            findings.append({"group": gid, **hit})
    return findings


# --- Plan-side: feature YAML + task files + linkage (Part B) ----------------------

def discover_feature_yaml(output_root: Path) -> Path:
    d = Path(output_root) / ".guardkit" / "features"
    if not d.is_dir():
        raise FileNotFoundError(f"no .guardkit/features/ in answer sheet: {output_root}")
    yamls = sorted(d.glob("*.yaml"))
    if len(yamls) != 1:
        raise FileNotFoundError(
            f"expected exactly one feature YAML under {d}, found {[p.name for p in yamls]}"
        )
    return yamls[0]


def load_feature_yaml(output_root: Path) -> dict:
    path = discover_feature_yaml(output_root)
    data = _yaml().safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: not a YAML mapping")
    data["_path"] = str(path)
    return data


def run_guardkit_validate(output_root: Path) -> dict:
    """The deterministic oracle (contract Part B.1): `guardkit feature validate
    {id} --json` from the answer-sheet root. Exit 0 valid / 1 errors / 2 not
    found. A missing CLI is an instrument defect naming the pin."""
    exe = shutil.which("guardkit")
    if exe is None:
        raise RuntimeError(
            "guardkit CLI not on PATH — the plan-side oracle is the installed "
            "guardkit (~/.agentecflow/bin/guardkit, resolving to the checkout "
            "pinned @ 28587b61 per CONTRACT-feature-spec-plan-outputs.md §0)."
        )
    feature_id = _yaml().safe_load(
        discover_feature_yaml(output_root).read_text(encoding="utf-8")
    ).get("id")
    proc = subprocess.run(
        [exe, "feature", "validate", str(feature_id), "--json"],
        cwd=output_root, capture_output=True, text=True, timeout=120,
    )
    payload: dict = {}
    m = re.search(r"\{.*\}", proc.stdout, re.DOTALL)
    if m:
        try:
            payload = json.loads(m.group(0))
        except json.JSONDecodeError:
            payload = {}
    payload.setdefault("feature_id", feature_id)
    payload["exit_code"] = proc.returncode
    payload["stderr_tail"] = proc.stderr[-1500:]
    return payload


def parse_frontmatter(md_path: Path) -> dict:
    text = Path(md_path).read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{md_path}: no YAML frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError(f"{md_path}: unterminated frontmatter")
    data = _yaml().safe_load(text[3:end])
    if not isinstance(data, dict):
        raise ValueError(f"{md_path}: frontmatter is not a mapping")
    return data


def wave_of(feature_yaml: dict, task_id: str) -> int | None:
    """1-indexed wave containing task_id per orchestration.parallel_groups."""
    groups = (feature_yaml.get("orchestration") or {}).get("parallel_groups") or []
    for n, wave in enumerate(groups, start=1):
        if isinstance(wave, list) and task_id in wave:
            return n
    return None


def frontmatter_findings(output_root: Path, feature_yaml: dict) -> list[dict]:
    """Gate-stricter-than-validate axes (documented divergence): task_type must
    be EXPLICIT (template Step 9: 'REQUIRED!'; validate tolerates absence by
    defaulting to feature), id/feature_id/wave must agree with the YAML."""
    findings: list[dict] = []
    fid = feature_yaml.get("id")
    for task in feature_yaml.get("tasks") or []:
        tid = task.get("id")
        fp = Path(output_root) / str(task.get("file_path", ""))
        if not fp.is_file():
            findings.append({"task": tid, "defect": "task_file_missing", "file_path": str(fp)})
            continue
        try:
            fm = parse_frontmatter(fp)
        except ValueError as exc:
            findings.append({"task": tid, "defect": "frontmatter_unparseable", "detail": str(exc)})
            continue
        if fm.get("id") != tid:
            findings.append({"task": tid, "defect": "frontmatter_id_mismatch",
                             "frontmatter_id": fm.get("id")})
        raw_type = fm.get("task_type")
        if raw_type is None:
            findings.append({"task": tid, "defect": "task_type_missing"})
        elif TASK_TYPE_ALIASES.get(str(raw_type), str(raw_type)) not in VALID_TASK_TYPES:
            findings.append({"task": tid, "defect": "task_type_invalid", "value": raw_type})
        if fm.get("feature_id") != fid:
            findings.append({"task": tid, "defect": "feature_id_mismatch",
                             "frontmatter_feature_id": fm.get("feature_id")})
        expected_wave = wave_of(feature_yaml, str(tid))
        if fm.get("wave") != expected_wave:
            findings.append({"task": tid, "defect": "wave_mismatch",
                             "frontmatter_wave": fm.get("wave"), "orchestration_wave": expected_wave})
    return findings


def effective_task_type(output_root: Path, feature_yaml: dict, task_id: str) -> str | None:
    for task in feature_yaml.get("tasks") or []:
        if task.get("id") == task_id:
            fp = Path(output_root) / str(task.get("file_path", ""))
            if fp.is_file():
                try:
                    raw = parse_frontmatter(fp).get("task_type")
                except ValueError:
                    return None
                if raw is not None:
                    return TASK_TYPE_ALIASES.get(str(raw), str(raw))
            return "feature"  # feature_loader default when absent
    return None


def mode_assignment_findings(feature_yaml: dict) -> list[dict]:
    """Contract B.4 pinned assignment: task-work for complexity ≥ 4, direct for
    ≤ 3 (gate enforces the pinned generator default — documented divergence:
    the schema alone also allows 'manual')."""
    findings = []
    for task in feature_yaml.get("tasks") or []:
        complexity = task.get("complexity", 5)
        mode = task.get("implementation_mode", "task-work")
        expected = "task-work" if complexity >= 4 else "direct"
        if mode != expected:
            findings.append({"task": task.get("id"), "defect": "mode_assignment",
                             "complexity": complexity, "mode": mode, "expected": expected})
    return findings


def strip_task_tag_lines(feature_text: str) -> str:
    """Inverse of bdd_linker.apply_mapping's insertion (pinned shape: a new
    line `<indent>@task:<TASK-ID>` inserted verbatim; existing lines never
    rewritten). Removing exactly those lines must reproduce the pinned input
    spec byte-for-byte — the spec-preservation gate."""
    kept = [ln for ln in feature_text.splitlines(keepends=True) if not TASK_TAG_RE.match(ln)]
    return "".join(kept)


def linkage_findings(parsed: dict, feature_yaml: dict, output_root: Path) -> list[dict]:
    """Plan/spec coherence floor (Step 11 output): every @task tag resolves to
    a plan task; ≥1 scenario linked; every @smoke scenario linked (the Coach's
    every-build oracle set must trace to owning tasks); every feature-type task
    owns ≥1 scenario (a feature task no scenario motivates is plan-invented
    work — selection discipline, not quality)."""
    findings: list[dict] = []
    task_ids = {t.get("id") for t in feature_yaml.get("tasks") or []}
    tag_map = scenario_task_tags(parsed)

    linked_tasks: set[str] = set()
    any_linked = False
    for scenario, ids in tag_map.items():
        for tid in ids:
            any_linked = True
            if tid not in task_ids:
                findings.append({"defect": "dangling_task_tag", "scenario": scenario, "task": tid})
            linked_tasks.add(tid)
    if not any_linked:
        findings.append({"defect": "no_scenarios_linked"})
    for sc in parsed["scenarios"]:
        if "@smoke" in sc["tags"] and not tag_map.get(sc["name"]):
            findings.append({"defect": "smoke_scenario_unlinked", "scenario": sc["name"]})
    for tid in sorted(task_ids):
        if effective_task_type(output_root, feature_yaml, str(tid)) == "feature" \
                and tid not in linked_tasks:
            findings.append({"defect": "feature_task_owns_no_scenario", "task": tid})
    return findings


def mermaid_blocks(guide_text: str) -> list[str]:
    return re.findall(r"```mermaid\s*\n(.*?)```", guide_text, re.DOTALL)
