"""Deterministic re-implementation of the product-owner output contract.

Faithful to the Pydantic models pinned 2026-07-03 from specialist-agent source:
  ProductRoadmap/Epic/FeatureSpecInput  src/specialist_agent/roles/product_owner/types.py:80-320
  EpicPlan/EpicStub/FeatureStub         src/specialist_agent/roles/product_owner/phased_extraction.py:107-217
  EnrichmentBatch/FeatureEnrichment     src/specialist_agent/roles/product_owner/phase_b_delta.py:22-144
  SourceCitation                        src/specialist_agent/roles/product_owner/types.py:33-77
  SourceDocument/Assumption             src/specialist_agent/roles/architect/types.py:40-134

Rules that come from the OUTPUT-CONTRACT / serving prompts rather than Pydantic code
are marked "CONTRACT:" — deliberate gate-only tightenings, documented per rule. Where
the gate is knowingly stricter than serving, the comment says so (the pre-registered
divergence list lives in po-heldout-suite-scope.md §3.3).

Two systematic stances, both deliberate: (1) no Pydantic-style lax coercion — a
numeric string where a number belongs fails the gate even where Pydantic would coerce;
(2) presence checks use exact types (isinstance), not truthiness.

Stdlib only. Every check appends a human-readable issue string; a valid document
yields an empty list.
"""

from __future__ import annotations

import re
from datetime import datetime

# --- Enum Literals (types.py:143-161 + :273 MODES + :283-292 estimate_unit; phase_b_delta.py:49-75; architect/types.py:133) ---
MODES = {"idea", "extract", "greenfield", "evolve", "impact", "scope"}
PRIORITY = {"Low", "Normal", "High", "Critical"}
MOSCOW = {"Must (core)", "Must", "Should", "Could", "Won't", "N/A", "?"}
VALUE = {"1 (Lowest)", "2 (Low)", "3 (Medium)", "4 (High)", "5 (Highest)"}
COMPLEXITY = {
    "Very easy (<.5d)",
    "Easy (≈1d)",  # U+2248 ALMOST EQUAL TO, verbatim from types.py:150-161
    "Normal (2-5d)",
    "Complex (5-10d)",
    "Very complex (>10d)",
    "Unknown",
    "N/A",
}
ESTIMATE_UNIT = {"story-points", "t-shirt", "person-days", "complexity-bucket", "ideal-hours"}
CONFIDENCE = {"high", "medium", "low"}

# types.py:171-191 / phase_b_delta.py:83-95 — the exact sentence-splitting regex
_SENTENCE_SPLIT = re.compile(r"[.!?]\s+|[.!?]$")

# phased_extraction.py:624-733 — enrichment completeness field set
ENRICHMENT_METADATA_FIELDS = (
    "priority", "moscow", "value", "role", "complexity", "acceptance_criteria", "field_citations",
)

# CONTRACT (gate-only tightening): OUTPUT-CONTRACT.md:52-54 defines any enrichment
# field on a Phase A stub as an ENRICHMENT_LEAK. At serving this is ADVISORY —
# player_extract_roadmap.md:129 says Pydantic drops unknown fields and the Coach no
# longer penalises it. The gate hard-fails it deliberately: emitting leaked fields is
# the opposite of the serving-shape fluency the fine-tune exists to prove.
STUB_ALLOWED_KEYS = {"feature_id", "title", "intent", "source_citations"}

# phase_b_delta.py:22-39 docstring: FeatureEnrichment deliberately has NO title and NO
# bounded_context — identity comes from the Phase A stub (CONTRACT: emitting them is a leak).
ENRICHMENT_FORBIDDEN_KEYS = {"title", "bounded_context"}

QUOTE_MAX_CHARS = 200  # types.py:71-74 and phased_extraction.py:854
INTENT_MAX_CHARS = 100  # CONTRACT: OUTPUT-CONTRACT.md "one line, <=100 chars" (no code constraint)


def sentence_count(text: str) -> int:
    return len([s for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()])


def _is_str(v) -> bool:
    return isinstance(v, str)


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _require(obj: dict, key: str, path: str, issues: list) -> bool:
    if key not in obj:
        issues.append(f"{path}: missing required field '{key}'")
        return False
    return True


def validate_source_citation(obj, path: str, issues: list, quote_repairable: bool = False) -> None:
    """quote_repairable=True on the Phase B path only: serving truncates >200-char
    quotes in the raw batch BEFORE validation (truncate_overlong_quotes,
    phased_extraction.py:899-966, wired session.py:1132), so an overlong Phase B
    quote is repaired at serving, not rejected — the gate must not reject it either."""
    if not isinstance(obj, dict):
        issues.append(f"{path}: SourceCitation must be an object")
        return
    if _require(obj, "document", path, issues) and not _is_str(obj["document"]):
        issues.append(f"{path}.document: must be a string")
    if _require(obj, "section_path", path, issues):
        sp = obj["section_path"]
        if not _is_str_list(sp):
            issues.append(f"{path}.section_path: must be a list of strings")
        elif len(sp) < 1:  # types.py:75-76
            issues.append(f"{path}.section_path: must have >=1 heading segment")
    ls, le = obj.get("line_start"), obj.get("line_end")
    for k, v in (("line_start", ls), ("line_end", le)):
        if v is not None and not isinstance(v, int):
            issues.append(f"{path}.{k}: must be int or null")
    if isinstance(ls, int) and isinstance(le, int) and le < ls:  # types.py:68-70
        issues.append(f"{path}: line_end must be >= line_start")
    q = obj.get("quote")
    if q is not None:
        if not _is_str(q):
            issues.append(f"{path}.quote: must be string or null")
        elif len(q) > QUOTE_MAX_CHARS and not quote_repairable:  # types.py:71-74
            issues.append(f"{path}.quote: {len(q)} chars > {QUOTE_MAX_CHARS} — cite the snippet, not the section")


def validate_field_citations(obj, path: str, issues: list, quote_repairable: bool = False) -> None:
    if not isinstance(obj, dict):
        issues.append(f"{path}: field_citations must be an object")
        return
    for k, v in obj.items():
        if not isinstance(v, list):
            issues.append(f"{path}.{k}: must be a list of SourceCitation")
            continue
        for i, c in enumerate(v):
            validate_source_citation(c, f"{path}.{k}[{i}]", issues, quote_repairable=quote_repairable)


def validate_source_document(obj, path: str, issues: list) -> None:
    # architect/types.py:40-69 — filename and contribution non-empty after strip
    if not isinstance(obj, dict):
        issues.append(f"{path}: SourceDocument must be an object {{filename, contribution}}, not {type(obj).__name__}")
        return
    for key in ("filename", "contribution"):
        if _require(obj, key, path, issues):
            v = obj[key]
            if not _is_str(v) or not v.strip():
                issues.append(f"{path}.{key}: must be a non-empty string")


def validate_assumption(obj, path: str, issues: list) -> None:
    # architect/types.py:111-134 — all fields required, confidence Literal
    if not isinstance(obj, dict):
        issues.append(f"{path}: Assumption must be an object")
        return
    for key in ("id", "category", "statement", "source", "impact_if_wrong"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    if _require(obj, "confidence", path, issues) and obj["confidence"] not in CONFIDENCE:
        issues.append(f"{path}.confidence: {obj['confidence']!r} not in {sorted(CONFIDENCE)}")


def _validate_enum_or_null(obj: dict, key: str, allowed: set, path: str, issues: list) -> None:
    v = obj.get(key)
    if v is not None and v not in allowed:
        issues.append(f"{path}.{key}: {v!r} is not a valid Literal (allowed: {sorted(allowed)} or null)")


def _validate_enrichment_fields(obj: dict, path: str, issues: list, quote_repairable: bool = False) -> None:
    """Shared optional enrichment fields of FeatureSpecInput (types.py:141-169) and
    FeatureEnrichment (phase_b_delta.py:43-81)."""
    _validate_enum_or_null(obj, "priority", PRIORITY, path, issues)
    _validate_enum_or_null(obj, "moscow", MOSCOW, path, issues)
    _validate_enum_or_null(obj, "value", VALUE, path, issues)
    _validate_enum_or_null(obj, "complexity", COMPLEXITY, path, issues)
    for key in ("acceptance_criteria", "technical_notes", "risks", "open_questions", "links"):
        if key in obj and not _is_str_list(obj[key]):
            issues.append(f"{path}.{key}: must be a list of strings")
    role = obj.get("role")
    if role is not None and not _is_str(role):
        issues.append(f"{path}.role: must be a string or null")
    if "field_citations" in obj:
        validate_field_citations(obj["field_citations"], f"{path}.field_citations", issues,
                                 quote_repairable=quote_repairable)


def validate_feature_spec_input(obj, path: str, issues: list) -> None:
    if not isinstance(obj, dict):
        issues.append(f"{path}: FeatureSpecInput must be an object")
        return
    for key in ("feature_id", "title", "bounded_context"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    if _require(obj, "description", path, issues):
        d = obj["description"]
        if not _is_str(d):
            issues.append(f"{path}.description: must be a string")
        elif sentence_count(d) < 2:  # types.py:171-191
            issues.append(f"{path}.description: must contain >=2 sentences (found {sentence_count(d)})")
    for key in ("source_documents", "constraints", "suggested_context_files", "depends_on"):
        if _require(obj, key, path, issues) and not _is_str_list(obj[key]):
            issues.append(f"{path}.{key}: must be a list of strings")
    t = obj.get("type")
    if t is not None and not _is_str(t):
        issues.append(f"{path}.type: must be a string or null")
    _validate_enrichment_fields(obj, path, issues)


def validate_epic(obj, path: str, issues: list) -> None:
    # types.py:194-236 — NOTE the Epic id field is 'id' (EpicStub uses 'epic_id')
    if not isinstance(obj, dict):
        issues.append(f"{path}: Epic must be an object")
        return
    for key in ("id", "name", "bounded_context", "description"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    if _require(obj, "features", path, issues):
        feats = obj["features"]
        if not isinstance(feats, list) or len(feats) < 1:  # types.py:230-236
            issues.append(f"{path}.features: every epic must have at least 1 feature")
        else:
            for i, f in enumerate(feats):
                validate_feature_spec_input(f, f"{path}.features[{i}]", issues)
    if _require(obj, "source_documents", path, issues) and not _is_str_list(obj["source_documents"]):
        issues.append(f"{path}.source_documents: must be a list of plain filename strings on Epic (types.py:225)")
    if "field_citations" in obj:
        validate_field_citations(obj["field_citations"], f"{path}.field_citations", issues)


def validate_product_roadmap(obj) -> list:
    issues: list = []
    path = "roadmap"
    if not isinstance(obj, dict):
        return [f"{path}: top-level output must be a JSON object"]
    # project_name: CONTRACT — serving injects the caller's value (handler.py:87-88),
    # so at serving a missing project_name never rejects; the gate requires the model
    # to emit it because the training contract (OUTPUT-CONTRACT.md) lists it.
    for key in ("project_name", "priority_rationale"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    if _require(obj, "mode", path, issues) and obj["mode"] not in MODES:
        issues.append(f"{path}.mode: {obj.get('mode')!r} not in {sorted(MODES)}")
    for key in ("constraints_and_dependencies", "open_questions"):
        if _require(obj, key, path, issues) and not _is_str_list(obj[key]):
            issues.append(f"{path}.{key}: must be a list of strings")
    epics = obj.get("epics")
    if _require(obj, "epics", path, issues):
        if not isinstance(epics, list) or len(epics) < 1:  # types.py:294-300
            issues.append(f"{path}.epics: at least 1 epic is required")
        else:
            for i, e in enumerate(epics):
                validate_epic(e, f"{path}.epics[{i}]", issues)
    fsi = obj.get("feature_spec_inputs")
    if _require(obj, "feature_spec_inputs", path, issues):
        if not isinstance(fsi, list):
            issues.append(f"{path}.feature_spec_inputs: must be a list")
        else:
            for i, f in enumerate(fsi):
                validate_feature_spec_input(f, f"{path}.feature_spec_inputs[{i}]", issues)
            # types.py:302-320 — sorted list compare (duplicates matter)
            if isinstance(epics, list):
                epic_ids = sorted(
                    f.get("feature_id", "?")
                    for e in epics if isinstance(e, dict)
                    for f in (e.get("features") or []) if isinstance(f, dict)
                )
                flat_ids = sorted(f.get("feature_id", "?") for f in fsi if isinstance(f, dict))
                if epic_ids != flat_ids:
                    issues.append(
                        f"{path}.feature_spec_inputs: feature_ids must match the flattened epic features "
                        f"(epics: {epic_ids} vs feature_spec_inputs: {flat_ids})"
                    )
                # CONTRACT (gate-only tightening): the Pydantic ProductRoadmap has no
                # uniqueness validator (only EpicPlan/EnrichmentBatch do), but duplicate
                # feature_ids collide in the written feature_spec_inputs/<id>.md artefacts.
                dupes = sorted({x for x in epic_ids if epic_ids.count(x) > 1})
                if dupes:
                    issues.append(f"{path}: duplicate feature_ids across epics: {dupes}")
    cs = obj.get("change_summary")
    if cs is not None and not _is_str(cs):
        issues.append(f"{path}.change_summary: must be a string or null")
    cov = obj.get("coverage_score")
    if cov is not None and not isinstance(cov, (int, float)):
        issues.append(f"{path}.coverage_score: must be a number or null")
    for i, sd in enumerate(obj.get("source_documents") or []):
        validate_source_document(sd, f"{path}.source_documents[{i}]", issues)
    for i, a in enumerate(obj.get("assumptions") or []):
        validate_assumption(a, f"{path}.assumptions[{i}]", issues)
    eu = obj.get("estimate_unit")
    if eu is not None and eu not in ESTIMATE_UNIT:
        issues.append(f"{path}.estimate_unit: {eu!r} not in {sorted(ESTIMATE_UNIT)} or null")
    return issues


def validate_feature_stub(obj, path: str, issues: list) -> None:
    if not isinstance(obj, dict):
        issues.append(f"{path}: FeatureStub must be an object")
        return
    leaks = set(obj.keys()) - STUB_ALLOWED_KEYS
    if leaks:  # CONTRACT: ENRICHMENT_LEAK
        issues.append(f"{path}: ENRICHMENT_LEAK — stub carries forbidden fields {sorted(leaks)}")
    for key in ("feature_id", "title", "intent"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    intent = obj.get("intent")
    if _is_str(intent) and len(intent) > INTENT_MAX_CHARS:  # CONTRACT
        issues.append(f"{path}.intent: {len(intent)} chars > {INTENT_MAX_CHARS} (one-line intent)")
    for i, c in enumerate(obj.get("source_citations") or []):
        validate_source_citation(c, f"{path}.source_citations[{i}]", issues)


def validate_epic_stub(obj, path: str, issues: list) -> None:
    if not isinstance(obj, dict):
        issues.append(f"{path}: EpicStub must be an object")
        return
    for key in ("epic_id", "name", "bounded_context"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    if _require(obj, "cited_docs", path, issues):
        cd = obj["cited_docs"]
        if not _is_str_list(cd):
            issues.append(f"{path}.cited_docs: must be a list of filename strings")
        elif len(cd) == 0:  # CONTRACT: OUTPUT-CONTRACT.md "empty/missing = hard failure"
            issues.append(f"{path}.cited_docs: empty — Phase B cannot scope its read (hard failure)")
    if _require(obj, "feature_stubs", path, issues):
        stubs = obj["feature_stubs"]
        if not isinstance(stubs, list) or len(stubs) < 1:  # phased_extraction.py:146-152
            issues.append(f"{path}.feature_stubs: each epic must have at least 1 feature stub")
        else:
            for i, s in enumerate(stubs):
                validate_feature_stub(s, f"{path}.feature_stubs[{i}]", issues)


def validate_epic_plan(obj) -> list:
    issues: list = []
    path = "epic_plan"
    if not isinstance(obj, dict):
        return [f"{path}: top-level output must be a JSON object"]
    if _require(obj, "project_name", path, issues) and not _is_str(obj["project_name"]):
        issues.append(f"{path}.project_name: must be a string")
    mode = obj.get("mode", "extract")  # default per phased_extraction.py:182
    if mode != "extract":
        issues.append(f"{path}.mode: only 'extract' is allowed (got {mode!r})")
    ts = obj.get("phase_a_completed_at")  # datetime | None, phased_extraction.py:183
    if ts is not None:
        if isinstance(ts, str):
            try:
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                issues.append(f"{path}.phase_a_completed_at: {ts!r} is not an ISO-8601 datetime")
        elif not isinstance(ts, (int, float)):
            issues.append(f"{path}.phase_a_completed_at: must be an ISO-8601 string, epoch number, or null")
    epics = obj.get("epics")
    if _require(obj, "epics", path, issues):
        if not isinstance(epics, list) or len(epics) < 1:  # phased_extraction.py:193-199
            issues.append(f"{path}.epics: EpicPlan requires at least 1 epic")
        else:
            for i, e in enumerate(epics):
                validate_epic_stub(e, f"{path}.epics[{i}]", issues)
            # phased_extraction.py:201-217 — unique feature_ids across all stubs
            ids = [
                s.get("feature_id", "?")
                for e in epics if isinstance(e, dict)
                for s in (e.get("feature_stubs") or []) if isinstance(s, dict)
            ]
            dupes = sorted({x for x in ids if ids.count(x) > 1})
            if dupes:
                issues.append(f"{path}: duplicate feature_ids across epics: {dupes}")
    if "open_questions" in obj and not _is_str_list(obj["open_questions"]):
        issues.append(f"{path}.open_questions: must be a list of strings")
    cov = obj.get("coverage_score")
    if cov is not None and not isinstance(cov, (int, float)):
        issues.append(f"{path}.coverage_score: must be a number or null")
    pr = obj.get("priority_rationale", "")
    if not _is_str(pr):
        issues.append(f"{path}.priority_rationale: must be a string")
    for i, sd in enumerate(obj.get("source_documents") or []):
        validate_source_document(sd, f"{path}.source_documents[{i}]", issues)
    for i, a in enumerate(obj.get("assumptions") or []):
        validate_assumption(a, f"{path}.assumptions[{i}]", issues)
    if "constraints_and_dependencies" in obj and not _is_str_list(obj["constraints_and_dependencies"]):
        issues.append(f"{path}.constraints_and_dependencies: must be a list of strings")
    nfrc = obj.get("nfr_candidates")
    if nfrc is not None and not (isinstance(nfrc, list) and all(isinstance(x, dict) for x in nfrc)):
        issues.append(f"{path}.nfr_candidates: must be a list of objects")
    return issues


def validate_feature_enrichment(obj, path: str, issues: list) -> None:
    if not isinstance(obj, dict):
        issues.append(f"{path}: FeatureEnrichment must be an object")
        return
    leaks = set(obj.keys()) & ENRICHMENT_FORBIDDEN_KEYS
    if leaks:  # CONTRACT (delta contract, TASK-POE-DELTA-002)
        issues.append(f"{path}: IDENTITY_LEAK — enrichment carries {sorted(leaks)}; identity comes from the Phase A stub")
    if _require(obj, "feature_id", path, issues) and not _is_str(obj["feature_id"]):
        issues.append(f"{path}.feature_id: must be a string")
    if _require(obj, "description", path, issues):
        d = obj["description"]
        if not _is_str(d):
            issues.append(f"{path}.description: must be a string")
        elif sentence_count(d) < 2:  # phase_b_delta.py:83-95
            issues.append(f"{path}.description: must contain >=2 sentences (found {sentence_count(d)})")
    if _require(obj, "source_documents", path, issues):
        sd = obj["source_documents"]
        if not _is_str_list(sd):
            issues.append(f"{path}.source_documents: must be a list of filename strings")
        elif len(sd) < 1:  # phase_b_delta.py:97-106 — every enrichment must be grounded
            issues.append(f"{path}.source_documents: must contain at least one entry")
    for key in ("constraints", "suggested_context_files", "depends_on"):
        if key in obj and not _is_str_list(obj[key]):
            issues.append(f"{path}.{key}: must be a list of strings")
    t = obj.get("type", "Dev: Feature")  # non-None default, phase_b_delta.py:47
    if not _is_str(t):
        issues.append(f"{path}.type: must be a string (FeatureEnrichment.type is non-nullable)")
    _validate_enrichment_fields(obj, path, issues, quote_repairable=True)


def validate_enrichment_batch(obj) -> list:
    issues: list = []
    path = "batch"
    if not isinstance(obj, dict):
        return [f"{path}: top-level output must be a JSON object"]
    for key in ("project_name", "epic_id"):
        if _require(obj, key, path, issues) and not _is_str(obj[key]):
            issues.append(f"{path}.{key}: must be a string")
    enr = obj.get("enrichments")
    if _require(obj, "enrichments", path, issues):
        if not isinstance(enr, list) or len(enr) < 1:  # phase_b_delta.py:121-127
            issues.append(f"{path}.enrichments: must be non-empty")
        else:
            for i, e in enumerate(enr):
                validate_feature_enrichment(e, f"{path}.enrichments[{i}]", issues)
            ids = [e.get("feature_id", "?") for e in enr if isinstance(e, dict)]
            dupes = sorted({x for x in ids if ids.count(x) > 1})
            if dupes:  # phase_b_delta.py:129-144
                issues.append(f"{path}: duplicate feature_ids within batch: {dupes}")
    return issues


def enrichment_metadata_count(enrichment: dict) -> int:
    """Populated metadata fields per _is_populated (phased_extraction.py:658-668):
    None, empty string, empty list and empty dict are all treated as absent."""
    n = 0
    for f in ENRICHMENT_METADATA_FIELDS:
        v = enrichment.get(f)
        if v is None:
            continue
        if isinstance(v, (str, list, dict)) and len(v) == 0:
            continue
        n += 1
    return n


def check_batch_against_stub_allowlist(batch: dict, epic_id: str, allowed_feature_ids: set) -> list:
    """Mirror of check_batch_against_epic_stub (phased_extraction.py:540-574) +
    assert_enrichment_completeness (phased_extraction.py:624-733)."""
    issues: list = []
    if batch.get("epic_id") != epic_id:
        issues.append(f"batch.epic_id {batch.get('epic_id')!r} != requested epic {epic_id!r}")
    enrichments = [e for e in (batch.get("enrichments") or []) if isinstance(e, dict)]
    escaped = sorted({e.get("feature_id", "?") for e in enrichments} - allowed_feature_ids)
    if escaped:
        issues.append(f"feature_ids outside the Phase A stub allowlist: {escaped}")
    if enrichments and all(enrichment_metadata_count(e) < 3 for e in enrichments):
        issues.append(
            "enrichment completeness: every enrichment populates fewer than 3 of "
            f"{ENRICHMENT_METADATA_FIELDS} (EnrichmentCompletenessError)"
        )
    return issues
