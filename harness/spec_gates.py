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
from difflib import SequenceMatcher
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
# 2026-08-14 (specialist-agent f23a845): the /feature-spec output contract became FOUR files — the
# digest joined the triple and the postprocessor now raises on a missing block. The contract document
# was not corrected until 2026-08-21, which is how this suite came to be frozen against three.
SPEC_FILE_SUFFIXES = (".feature", "_assumptions.yaml", "_summary.md", "_digest.yaml")
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
    """Part A: exactly four files, pinned names, nothing else (no step
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
        "digest": spec_dir / f"{slug}_digest.yaml",
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


# --- The digest (Part A.4, from 2026-08-14) -------------------------------------
#
# These mirror `check_digest_consistency()` in specialist-agent
# (src/specialist_agent/roles/product_owner/modes/feature_spec.py) — production's own checker, which
# is the source of truth. They are re-implemented here rather than imported because GRADING must run
# standalone against an output directory: an exam that needs the production repo on the path is an
# exam that quietly does not run. The oracle in solution/ is validated against the REAL function, so
# a divergence between these rules and production's shows up as a failing oracle.
#
# Deliberately NOT checked, exactly as production does not: whether a sentence accurately DESCRIBES
# its example. Nothing deterministic can, and that is what the human read is for.

DIGEST_KEYS = {"feature", "generated", "scenarios", "assumptions"}

# --- VENDORED VERBATIM from specialist-agent -----------------------------------
# src/specialist_agent/roles/product_owner/modes/feature_spec.py (lines ~881-965).
#
# Copied, not paraphrased, and the reason is a live example: my first pass wrote
# `\b(Given|When|Then|And|But)\b\s` and it rejected two perfectly good oracle sentences —
# "When a member gives up a booking, ..." — because "When" opens ordinary English all the time.
# Production knows that and excludes "When" from the start-anchored set ON PURPOSE, and it re-checks
# every candidate sentence break against an abbreviation list. Those are judgements, not details, and
# a paraphrase loses them. If these ever drift from production, the oracle in solution/ — which is
# validated against the REAL function — starts failing, which is the signal we want.
_STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")
# "When" is missing on purpose: "When the service restarts, the queue is drained." is ordinary
# English, and refusing it would reject good digests.
_STEP_KEYWORDS_AT_START = ("Given", "Then", "And", "But")
_DIGEST_STEP_LINE_RE = re.compile(
    r"\n\s*(?:" + "|".join(_STEP_KEYWORDS) + r")\s"
    r"|\A(?:" + "|".join(_STEP_KEYWORDS_AT_START) + r")\s"
)
_MID_SENTENCE_BREAK_RE = re.compile(r"[.?!]\s")
_DIGEST_ABBREVIATIONS = (
    "e.g.", "i.e.", "etc.", "cf.", "vs.", "approx.", "a.m.", "p.m.", "U.S.", "U.K.", "E.U.",
    "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "St.", "Jr.", "Sr.", "Inc.", "Ltd.", "Co.",
)
_ABBREVIATION_TAIL_RE = re.compile(
    r"(?<![A-Za-z])(?:" + "|".join(re.escape(a) for a in _DIGEST_ABBREVIATIONS) + r")$",
    re.IGNORECASE,
)


def _has_mid_sentence_break(sentence: str) -> bool:
    """True iff `sentence` is more than one sentence — abbreviations excepted."""
    body = sentence[:-1]
    for match in _MID_SENTENCE_BREAK_RE.finditer(body):
        if _ABBREVIATION_TAIL_RE.search(body[: match.start() + 1]):
            continue
        return True
    return False


def digest_findings(digest, feature_text: str, manifest, slug: str) -> list[dict]:
    """Structured findings; empty list means the digest conforms."""
    out: list[dict] = []
    if not isinstance(digest, dict):
        return [{"defect": "digest_shape", "detail": "the digest is not a mapping"}]

    extra = set(digest) - DIGEST_KEYS
    missing = DIGEST_KEYS - set(digest)
    for k in sorted(extra):
        out.append({"defect": "digest_unknown_key", "key": k})
    for k in sorted(missing):
        out.append({"defect": "digest_missing_key", "key": k})
    if digest.get("feature") not in (None, slug):
        out.append({"defect": "digest_slug_mismatch",
                    "detail": f"names {digest.get('feature')!r}, spec files are {slug!r}"})

    spec = parse_feature(feature_text)["scenarios"]
    # this parser names the scenario title `name`; production's _parse_scenarios returns it as the
    # first tuple element. Same value, different key — read it from THIS parser, not from memory.
    spec_titles = [sc["name"] for sc in spec]
    spec_tags = [list(sc.get("tags") or []) for sc in spec]
    entries = digest.get("scenarios") or []
    if not isinstance(entries, list):
        return out + [{"defect": "digest_shape", "detail": "'scenarios' is not a list"}]

    if len(entries) != len(spec_titles):
        out.append({"defect": "digest_scenario_count",
                    "detail": f"digest has {len(entries)}, .feature has {len(spec_titles)}"})

    for i, (entry, title) in enumerate(zip(entries, spec_titles), start=1):
        if not isinstance(entry, dict):
            out.append({"defect": "digest_entry_shape", "index": i}); continue
        if str(entry.get("title") or "").strip() != title:
            out.append({"defect": "digest_title_mismatch", "index": i,
                        "detail": f"{entry.get('title')!r} != {title!r} (order-sensitive)"})
        tags = entry.get("tags")
        if [str(t) for t in (tags or [])] != spec_tags[i - 1]:
            out.append({"defect": "digest_tags_mismatch", "index": i,
                        "detail": f"{tags} != {spec_tags[i - 1]}"})
        sentence = str(entry.get("sentence") or "").strip()
        if not sentence:
            out.append({"defect": "digest_sentence_empty", "index": i}); continue
        if sentence[-1] not in ".?!":
            out.append({"defect": "digest_sentence_unterminated", "index": i})
        if _has_mid_sentence_break(sentence):
            out.append({"defect": "digest_sentence_not_one_sentence", "index": i})
        if _DIGEST_STEP_LINE_RE.search(sentence):
            out.append({"defect": "digest_sentence_has_step_line", "index": i})
        for token in ("Scenario", "Feature:"):
            if token in sentence:
                out.append({"defect": "digest_sentence_uses_spec_word", "index": i, "word": token})

    man_entries = (manifest or {}).get("assumptions") or []
    man_ids = [str(a.get("id")) for a in man_entries if isinstance(a, dict)]
    dig_entries = digest.get("assumptions") or []
    dig_ids = [str(a.get("id")) for a in dig_entries if isinstance(a, dict)]
    for missing_id in [i for i in man_ids if i not in dig_ids]:
        out.append({"defect": "digest_assumption_missing", "id": missing_id})
    for extra_id in [i for i in dig_ids if i not in man_ids]:
        out.append({"defect": "digest_assumption_unknown", "id": extra_id})
    by_id = {str(a.get("id")): a for a in man_entries if isinstance(a, dict)}
    for a in dig_entries:
        if not isinstance(a, dict):
            continue
        src = by_id.get(str(a.get("id")))
        if not src:
            continue
        if str(a.get("text") or "") != str(src.get("assumption") or ""):
            out.append({"defect": "digest_assumption_text_not_verbatim", "id": a.get("id")})
        if str(a.get("basis") or "") != str(src.get("basis") or ""):
            out.append({"defect": "digest_assumption_basis_not_verbatim", "id": a.get("id")})
    return out


def load_digest(path):
    import yaml
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


# ===========================================================================
# THE SCENARIO COVERAGE MAP  (G-S5, re-pointed 2026-08-22 on Rich's ruling)
# ===========================================================================
#
# WHAT THIS REPLACES AND WHY, in plain words.
#
# Until 2026-08-14 a plan said which scenarios it covered by writing tag lines
# (`@task:TASK-XXX-001`) into a copy of the specification. Rich retired that on
# 2026-08-14 and the tool that writes plans today cannot produce such a file at
# all. The check that graded those tags therefore measured nothing, and — worse
# — it SKIPPED, which pytest reports as exit code 0, i.e. as a pass.
#
# The replacement is the mechanism the current planning template already
# specifies: the plan's own feature YAML carries
#
#     feature_files:                       <- which specification file(s) this
#       - features/<slug>/<slug>.feature      plan is answering
#     scenarios:                           <- one entry per scenario in it
#       "<the scenario's title, copied exactly>":
#         verifier: hurl                   <- where that scenario gets proved
#
# Every assertion below is taken from a written source, named inline. Nothing
# here is invented for the exam.
#
# SOURCES (all read 2026-08-22):
#   [T] guardkit installer/core/commands/feature-plan.md — the planning
#       template the serving seat is given, pinned by specialist-agent
#       templates/pins.py as `feature-plan-methodology`
#       (sha256 20a3061159…, pinned_commit 3ad3a366, 3017 lines).
#       Line numbers below are that file's.
#   [L] guardkit guardkit/orchestrator/feature_loader.py — the loader that
#       reads the YAML in production (`Feature`, `_enforce_routing_law`).
#   [V] guardkit guardkit/orchestrator/verifier_stamp.py — `ScenarioStamp`,
#       `VERIFIER_HOMES`, `extract_scenario_titles`.
#   [S] specialist-agent roles/architect/modes/feature_plan_oracle.py — the
#       plan writer's own post-processing (what it strips, what it repairs).
#   [F] forge src/forge/planning/target_terminal_tools.py — what forge does
#       when the plan omits `feature_files:`.
#
# ONE THING THE OLD CHECK DID THAT THIS ONE CANNOT, stated plainly rather than
# quietly dropped: the retired tags named a TASK per scenario, so the exam
# could ask "does every task exist?" and "does every task own a scenario?".
# The routing-law map has no task field at all — `ScenarioStamp` [V] sets
# `extra="forbid"` and allows exactly `verifier`, `test_ref`, `test_paths`.
# The routing law replaced task-ownership with verification-home ownership.
# So the successor questions are "does every scenario have a home?" and "does
# every stamp name a scenario that really exists?", which is what is graded
# below. The task half survives only as the task-frontmatter `verifier:` stamp
# ([T] 479-486), graded by `task_verifier_findings`.

# The closed list of verification homes, and the scenario-title lexer, are
# IMPORTED from guardkit rather than copied, so this gate and the production
# loader can never drift apart. A failed import is an instrument error naming
# the pin — the same posture as the missing-CLI rule above, never a silent skip.
def _guardkit_routing_law():
    """(`VERIFIER_HOMES`, `extract_scenario_titles`) from the installed guardkit."""
    try:
        from guardkit.orchestrator.verifier_stamp import (  # noqa: PLC0415
            VERIFIER_HOMES,
            extract_scenario_titles,
        )
    except ImportError as exc:  # pragma: no cover - environment defect
        raise RuntimeError(
            "guardkit is not importable — the scenario-coverage gate reads its "
            "closed verifier vocabulary and its Gherkin title lexer from "
            "guardkit.orchestrator.verifier_stamp so the exam and the production "
            "feature loader can never disagree. Install the pinned guardkit "
            "checkout (CONTRACT-feature-spec-plan-outputs.md §0)."
        ) from exc
    return VERIFIER_HOMES, extract_scenario_titles


# The stamp's allowed keys, verbatim from ScenarioStamp [V] (extra='forbid';
# parse_scenario_stamp's own message says "Allowed keys: verifier, test_ref,
# test_paths").
STAMP_KEYS = ("verifier", "test_ref", "test_paths")

# A tag line in a .feature file: `@smoke`, `@key-example @smoke`, …
_TAG_LINE_RE = re.compile(r"^\s*@[^\s]")
# Same shape as guardkit's _SCENARIO_LINE_RE [V] — longest keyword first so
# "Scenario Outline" never half-matches, and "Examples:" (an Outline's table
# header) can never match.
_SCENARIO_HEAD_RE = re.compile(
    r"^\s*(?:Scenario Outline|Scenario Template|Scenario|Example)\s*:\s*(?P<title>\S.*?)\s*$"
)


def spec_scenario_tags(spec_text: str) -> dict[str, set[str]]:
    """{scenario title -> the tags on the lines immediately above it}.

    guardkit's own extractor returns titles only; the exam additionally needs to
    know which scenarios the specification marked `@smoke`, because the smoke set
    is the one the Coach re-proves on every build. Titles come from the SAME
    regex shape guardkit uses, so the two agree on what a scenario is.
    """
    tags: dict[str, set[str]] = {}
    pending: set[str] = set()
    for line in spec_text.splitlines():
        head = _SCENARIO_HEAD_RE.match(line)
        if head:
            tags.setdefault(head.group("title"), set()).update(pending)
            pending = set()
            continue
        if _TAG_LINE_RE.match(line):
            pending.update(tok for tok in line.split() if tok.startswith("@"))
            continue
        if line.strip():
            pending = set()
    return tags


def _loose(title: str) -> str:
    """Case- and spacing-insensitive form of a title, used ONLY to pick the
    closest specification title to show beside a rejected key. The PASS/FAIL rule
    is exact equality — [T] 461-465: keys "MUST be the spec's `Scenario:` titles
    VERBATIM … never paraphrase, re-case, or tidy it"."""
    return re.sub(r"[^a-z0-9]+", " ", title.casefold()).strip()


def _closest_title(key: str, titles: list[str]) -> tuple[str | None, float]:
    """The specification title most similar to `key`, and how similar.

    DELIBERATELY NOT A VERDICT. An earlier draft of this gate tried to sort
    rejected keys into "a paraphrase of a real scenario" and "a scenario the plan
    invented", and reported them as two different defects. That distinction is not
    mechanically decidable and the attempt was dropped: "Searching by EMPLOYER
    returns matching members" and "A query shorter than the minimum ALLOWED length
    is refused" are the same edit distance from a real title, and one is an
    invented scenario while the other is a mis-copied one. Only a person reading
    the two titles can tell. So the gate reports ONE defect — the key is not a
    title in the specification — and hands the reader the nearest title and the
    similarity so the answer is obvious at a glance.
    """
    best, score = None, 0.0
    loose_key = _loose(key)
    for title in titles:
        ratio = SequenceMatcher(None, loose_key, _loose(title)).ratio()
        if ratio > score:
            best, score = title, ratio
    return best, round(score, 3)


def coverage_map_findings(
    feature_yaml: dict,
    spec_text: str,
    *,
    expected_feature_files: set[str] | None = None,
) -> list[dict]:
    """Does the plan say which scenarios it covers, and is what it says true?

    Returns findings that NAME the offending scenario or key (house rule,
    extension scope §2.4). An empty list is the only pass.

    `expected_feature_files` — when the exam knows exactly which specification
    file the plan was handed (it does; the input is pinned), the declared paths
    must be that file. Omit it to grade a plan whose specification lives
    somewhere the caller cannot pin, which is the case when grading captured
    production runs for other features.
    """
    homes, extract_titles = _guardkit_routing_law()
    findings: list[dict] = []

    # --- 1. The map must be there at all. ---------------------------------
    # [T] 319: `feature_files` "Repo-relative Gherkin .feature paths naming this
    # feature's approved-scenario universe. Required when the law is enforced."
    # [T] 320: `scenarios` "Per-scenario verifier map".
    # [T] 421: "/feature-spec proposes the routing in its summary; THIS COMMAND
    # writes the authoritative map into the feature YAML."
    # Both keys are optional in the schema [L] and become mandatory only under
    # the enforcement flag — which the plan writer is forbidden to set ([T] 470-474).
    # RICH'S RULING, 2026-08-22: for this exam they are REQUIRED. A plan that
    # does not say which scenarios it covers has not been graded on coverage,
    # and "not graded" must never again be recorded as "passed".
    files = feature_yaml.get("feature_files")
    if not files:
        findings.append({
            "defect": "no_feature_files",
            "detail": "the plan's feature YAML declares no `feature_files:` — "
                      "nothing names the specification this plan answers",
        })
    elif not isinstance(files, list):
        findings.append({"defect": "feature_files_not_a_list", "value": repr(files)[:120]})
        files = []
    else:
        for entry in files:
            if not isinstance(entry, str) or not entry.strip():
                findings.append({"defect": "feature_files_entry_malformed", "entry": repr(entry)[:120]})
    if not isinstance(files, list):
        files = []

    # [S] 2447-2455: the plan writer may declare
    # `feature_files: [features/<slug>/<slug>.feature]` and "a feature_files:
    # entry naming any OTHER path is still refused"; [F] 1746-1811: forge fills
    # the key with the spec .feature IT committed at that path, and refuses a
    # plan whose declaration contradicts it; [L] 1250-1259: every declared file
    # must exist under the repo root.
    if expected_feature_files is not None and files:
        declared = {str(e).strip().lstrip("./") for e in files if isinstance(e, str)}
        for entry in sorted(declared - expected_feature_files):
            findings.append({
                "defect": "feature_files_wrong_path", "entry": entry,
                "expected_one_of": sorted(expected_feature_files),
            })
        if not (declared & expected_feature_files):
            findings.append({
                "defect": "feature_files_missing_the_pinned_spec",
                "expected_one_of": sorted(expected_feature_files),
                "declared": sorted(declared),
            })

    scenarios = feature_yaml.get("scenarios")
    if not scenarios:
        findings.append({
            "defect": "no_scenarios_map",
            "detail": "the plan's feature YAML declares no `scenarios:` map — "
                      "no scenario has been given a verification home",
        })
        scenarios = {}
    elif not isinstance(scenarios, dict):
        findings.append({"defect": "scenarios_not_a_mapping", "value": type(scenarios).__name__})
        scenarios = {}

    # --- 2. The keys must be the specification's own titles, exactly. -----
    # [T] 461-465: "`scenarios:` keys MUST be the spec's `Scenario:` titles
    # VERBATIM — copy the title text from the .feature file character for
    # character; never paraphrase, re-case, or tidy it. Under the law a key that
    # does not equal a title in feature_files matches nothing, so a paraphrased
    # key is an UNSTAMPED scenario."
    # [L] 1284-1293 logs the mirror case as a stale stamp.
    spec_titles = list(dict.fromkeys(extract_titles(spec_text)))
    title_set = set(spec_titles)
    for key in scenarios:
        if not isinstance(key, str) or not key.strip():
            findings.append({"defect": "scenario_key_not_a_title", "key": repr(key)[:120]})
            continue
        if key in title_set:
            continue
        nearest, similarity = _closest_title(key, spec_titles)
        findings.append({
            "defect": "scenario_title_not_in_the_specification",
            "key": key,
            "nearest_title_in_the_spec": nearest,
            "similarity": similarity,
            "detail": "this key is not a scenario title in the declared specification. "
                      "Either the plan copied a real title inexactly — in which case that "
                      "scenario now has no verification home, because under the routing "
                      "law a key that is not equal to a title matches nothing — or the "
                      "plan is claiming to cover a scenario nobody asked for. Compare it "
                      "with the nearest title above to see which.",
        })

    # --- 3. Every scenario in the specification must have a home. ---------
    # [T] 474-477: "Under the flag, a scenario found in feature_files but missing
    # from scenarios: REJECTS THE PLAN LOAD, naming the unstamped titles."
    # [L] 1270-1282 is that rejection.
    tags = spec_scenario_tags(spec_text)
    for title in spec_titles:
        if title in scenarios:
            continue
        findings.append({"defect": "scenario_unstamped", "scenario": title})
        # Named separately, not because it can fire alone (it cannot — an
        # unstamped smoke scenario is always an unstamped scenario) but because
        # the frozen G-S5 wording called the smoke set out by name: it is the
        # set the Coach re-proves on every build, so losing one is worth saying
        # in its own sentence rather than leaving a reader to notice the tag.
        if "@smoke" in tags.get(title, set()):
            findings.append({"defect": "smoke_scenario_unstamped", "scenario": title})

    # --- 4. Each stamp must be well formed. -------------------------------
    # [T] 417-420 closed vocabulary + "An unknown value is a loud plan-load ERROR
    # — there is no fallback home"; [V] ScenarioStamp._verifier_in_closed_vocabulary.
    # [T] 432-437 and 457-458: toolchain "REQUIRES test_ref: naming that test —
    # a toolchain stamp WITHOUT test_ref is REJECTED"; [V]
    # ScenarioStamp._toolchain_carries_its_named_test.
    # [V] ScenarioStamp extra="forbid" — "Allowed keys: verifier, test_ref, test_paths."
    for key, stamp in scenarios.items():
        if isinstance(stamp, str):          # the documented bare-string shorthand [V]
            stamp = {"verifier": stamp}
        if not isinstance(stamp, dict):
            findings.append({"defect": "stamp_malformed", "scenario": key,
                             "value": repr(stamp)[:120]})
            continue
        for extra in sorted(k for k in stamp if k not in STAMP_KEYS):
            findings.append({"defect": "stamp_unknown_key", "scenario": key, "key": extra,
                             "allowed": list(STAMP_KEYS)})
        verifier = stamp.get("verifier")
        if verifier is None:
            findings.append({"defect": "stamp_has_no_verifier", "scenario": key})
            continue
        if verifier not in homes:
            findings.append({"defect": "verifier_not_in_closed_list", "scenario": key,
                             "verifier": verifier, "allowed": sorted(homes)})
            continue
        test_ref = stamp.get("test_ref")
        if verifier == "toolchain" and not (isinstance(test_ref, str) and test_ref.strip()):
            findings.append({
                "defect": "toolchain_stamp_without_test_ref", "scenario": key,
                "detail": "`verifier: toolchain` means 'this NAMED test proves the "
                          "scenario' and requires `test_ref:`; a bare toolchain stamp "
                          "is refused at plan load",
            })

    # --- 5. The plan must not set policy. ---------------------------------
    # [T] 470-474: "routing_law: is REPO/HUMAN POLICY, not a plan-writer field …
    # Do NOT emit routing_law: in the feature YAML — the plan-writer never sets
    # policy; write feature_files: and scenarios: only, and let the repo flag
    # decide." [S] strip_model_emitted_routing_law removes it in production, for
    # the same reason. The exam grades what the model wrote, before that repair.
    if "routing_law" in feature_yaml:
        findings.append({
            "defect": "routing_law_emitted_by_the_plan",
            "value": str(feature_yaml.get("routing_law")),
            "detail": "turning the law on is a human/repo decision; the plan writer "
                      "declares coverage, never policy",
        })

    return findings


def task_verifier_findings(output_root: Path, feature_yaml: dict) -> list[dict]:
    """The task-frontmatter half of the routing law.

    [T] 479-486: "a task MAY carry `verifier:` beside `task_type:` (same closed
    vocabulary, same loud validation at task load). For `verifier: toolchain`,
    `test_ref: <test token>` is REQUIRED — a bare toolchain is refused at task
    load." MAY, so absence is not a finding; a PRESENT stamp is checked, exactly
    as `validate_task_verifier` [V] checks it in production.
    """
    homes, _ = _guardkit_routing_law()
    findings: list[dict] = []
    for task in feature_yaml.get("tasks") or []:
        tid = str(task.get("id"))
        fp = Path(output_root) / str(task.get("file_path", ""))
        if not fp.is_file():
            continue                      # owned by test_task_frontmatter_discipline
        try:
            fm = parse_frontmatter(fp)
        except ValueError:
            continue                      # owned by test_task_frontmatter_discipline
        verifier = fm.get("verifier")
        if verifier is None:
            continue
        if verifier not in homes:
            findings.append({"task": tid, "defect": "task_verifier_not_in_closed_list",
                             "verifier": verifier, "allowed": sorted(homes)})
            continue
        test_ref = fm.get("test_ref")
        if verifier == "toolchain" and not (isinstance(test_ref, str) and test_ref.strip()):
            findings.append({"task": tid, "defect": "task_toolchain_stamp_without_test_ref"})
    return findings
