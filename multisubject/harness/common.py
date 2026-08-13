"""Shared helpers for the fleet-evals harness.

Lifted-and-generalised from study-tutor ``scripts/eval/`` at HEAD
``27bb0b5b760a393c7470b0aaae30bcdccbe1a843`` with the five pinned changes:

1. every output path is rooted in a ``--run-dir`` (convention:
   ``runs/YYYY-MM-DD-<venue>-<slug>/``), never a hard-coded evidence dir;
2. the two-way ``base``/``finetune`` keys generalise to an n-way
   ``candidates`` list end-to-end (legacy two-way artefacts still load —
   ``base``/``finetune`` are treated as candidate NAMES);
3. rubrics live in ``harness/rubrics/<subject>.md`` selected by each item's
   ``subject`` field (English is the only non-DRAFT rubric today);
4. every stage records itself into the run's ``MANIFEST.json``;
5. runs refuse to start unless the venue has a committed ``PROTOCOL.md``
   (pre-registration enforced by code, not prose).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUBRICS_DIR = Path(__file__).resolve().parent / "rubrics"

# The six judging dimensions — shared by every rubric (see rubrics/_base.md).
DIMS = [
    "socratic_stance", "aqa_alignment", "scaffolding",
    "subject_accuracy", "tone", "reasoning_visibility",
]

#: Multi-turn judging adds a session-level dimension (PROTOCOL v3, Rich's
#: word 2026-08-13): does the tutor DRAW THE STUDENT IN across the dialogue —
#: eliciting attempts, building on the student's own words, sustaining
#: momentum — rather than lecturing? Single-turn judging cannot see this;
#: it is the construct Rich's real-session experience says matters most.
MT_DIMS = DIMS + ["engagement_elicitation"]

_THINK = re.compile(r"<think>.*?</think>", re.S)


def strip_think(text: str) -> str:
    """Return the visible answer — ``content`` minus any ``<think>`` block."""
    return _THINK.sub("", text).strip()


# --------------------------------------------------------------------------
# JSONL / hashing
# --------------------------------------------------------------------------

def read_jsonl(path: str | Path) -> list[dict]:
    rows: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: str | Path, rows: list[dict]) -> None:
    Path(path).write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Change 5 — pre-registration gate
# --------------------------------------------------------------------------

_PROTOCOL_DRAFT = re.compile(r"^\*\*Status:\*\*.*\bDRAFT\b", re.M)


def require_protocol(venue: str | Path) -> Path:
    """Refuse to start a run unless the venue has a REGISTERED PROTOCOL.md.

    Pre-registration is enforced by code: the hypothesis, decision rule,
    seeds, judges and n must be COMMITTED before any response is generated
    (2026-05-18 required fix #6). A protocol whose ``**Status:**`` line says
    DRAFT is a written-but-unregistered protocol — the gate tap (flipping the
    line to REGISTERED, dated) is Rich's act, so DRAFT refuses just like
    absence does. Returns the protocol path.
    """
    venue = Path(venue)
    protocol = venue / "PROTOCOL.md"
    if not protocol.is_file():
        raise SystemExit(
            f"REFUSED: no PROTOCOL.md in venue '{venue}'.\n"
            "Runs must be pre-registered: commit the venue's PROTOCOL.md "
            "(hypothesis, decision rule, seeds, judges, n) BEFORE any "
            "generation. Template: runbooks/templates/PROTOCOL-template.md."
        )
    if _PROTOCOL_DRAFT.search(protocol.read_text(encoding="utf-8")):
        raise SystemExit(
            f"REFUSED: {protocol} has Status DRAFT.\n"
            "A DRAFT protocol is written but not registered — registration "
            "(Status: REGISTERED, dated) is Rich's gate tap, not the "
            "harness's. No run may start until then."
        )
    return protocol


# --------------------------------------------------------------------------
# Change 2 — n-way candidates
# --------------------------------------------------------------------------

def load_candidates(path: str | Path) -> list[dict]:
    """Load a venue candidates.yaml: {candidates: [{name, model, endpoint,
    gguf_sha256?}, ...]}. Names must be unique and never 'tie'."""
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    cands = data.get("candidates") if isinstance(data, dict) else None
    if not isinstance(cands, list) or len(cands) < 2:
        raise SystemExit(f"{path}: needs a 'candidates' list with >= 2 entries")
    names = []
    for c in cands:
        for field in ("name", "model", "endpoint"):
            if not c.get(field):
                raise SystemExit(f"{path}: candidate missing '{field}': {c}")
        if c["name"] == "tie":
            raise SystemExit(f"{path}: 'tie' is a reserved candidate name")
        names.append(c["name"])
    if len(set(names)) != len(names):
        raise SystemExit(f"{path}: duplicate candidate names {names}")
    return cands


def labels_for(n: int) -> list[str]:
    """Blind labels A, B, C, ... for n candidates."""
    if n > 26:
        raise SystemExit(f"{n} candidates is more than 26 blind labels")
    return [chr(ord("A") + i) for i in range(n)]


def normalise_response_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Normalise responses.jsonl rows to the n-way shape.

    New shape:    {..., "responses": {candidate_name: response_dict}}
    Legacy shape: {..., "base": response_dict, "finetune": response_dict}
                  (2026-05-18 artefacts — 'base'/'finetune' become names)
    Returns (rows in new shape, candidate names in stable order).
    """
    out: list[dict] = []
    names: list[str] = []
    for r in rows:
        if "responses" in r:
            resp = r["responses"]
        elif "base" in r and "finetune" in r:
            resp = {"base": r["base"], "finetune": r["finetune"]}
        else:
            raise SystemExit(
                f"row {r.get('id')}: neither 'responses' nor legacy "
                "'base'/'finetune' keys present"
            )
        if not names:
            names = list(resp)
        elif set(names) != set(resp):
            raise SystemExit(
                f"row {r.get('id')}: candidate set {sorted(resp)} != {sorted(names)}"
            )
        meta = {k: v for k, v in r.items()
                if k not in ("responses", "base", "finetune")}
        out.append({**meta, "responses": resp})
    return out, names


def normalise_transcript_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Same as normalise_response_rows, for multiturn transcripts.

    New shape:    {..., "transcripts": {candidate_name: [turns]}}
    Legacy shape: {..., "base_transcript": [...], "finetune_transcript": [...]}
    """
    out: list[dict] = []
    names: list[str] = []
    for r in rows:
        if "transcripts" in r:
            tr = r["transcripts"]
        elif "base_transcript" in r and "finetune_transcript" in r:
            tr = {"base": r["base_transcript"], "finetune": r["finetune_transcript"]}
        else:
            raise SystemExit(
                f"row {r.get('id')}: neither 'transcripts' nor legacy "
                "'*_transcript' keys present"
            )
        if not names:
            names = list(tr)
        elif set(names) != set(tr):
            raise SystemExit(
                f"row {r.get('id')}: candidate set {sorted(tr)} != {sorted(names)}"
            )
        meta = {k: v for k, v in r.items()
                if k not in ("transcripts", "base_transcript", "finetune_transcript")}
        out.append({**meta, "transcripts": tr})
    return out, names


def positions_from_key(key_data: dict) -> dict[str, dict[str, str]]:
    """Return {item_id: {label: candidate_name}} from a blind key.

    New shape:    {"seed", "candidates": [names], "positions": {id: {label: name}}}
    Legacy shape: {"seed", "base_position": {id: "A"|"B"}}
                  (2026-05-18 two-way key — candidates are base/finetune)
    """
    if "positions" in key_data:
        return key_data["positions"]
    if "base_position" in key_data:
        out = {}
        for item_id, base_label in key_data["base_position"].items():
            ft_label = "B" if base_label == "A" else "A"
            out[item_id] = {base_label: "base", ft_label: "finetune"}
        return out
    raise SystemExit("blind key has neither 'positions' nor legacy 'base_position'")


def normalise_judgement_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Normalise resolved judgements to the n-way shape.

    New shape:    {..., "winner": name|"tie", "scores": {name: {dims}}}
    Legacy shape: {..., "winner": "base"|"finetune"|"tie",
                   "base_scores": {...}, "finetune_scores": {...}}
    """
    out: list[dict] = []
    names: list[str] = []
    for r in rows:
        if "scores" in r:
            scores = r["scores"]
        elif "base_scores" in r and "finetune_scores" in r:
            scores = {"base": r["base_scores"], "finetune": r["finetune_scores"]}
        else:
            raise SystemExit(f"judgement {r.get('id')}: no scores found")
        if not names:
            names = list(scores)
        meta = {k: v for k, v in r.items()
                if k not in ("scores", "base_scores", "finetune_scores")}
        out.append({**meta, "scores": scores})
    return out, names


# --------------------------------------------------------------------------
# Change 3 — rubric selection by subject
# --------------------------------------------------------------------------

def load_rubric(subject: str, *, allow_draft: bool = False,
                rubrics_dir: str | Path | None = None) -> str:
    """Load harness/rubrics/<subject>.md.

    DRAFT rubrics (every subject except English today) refuse to drive a
    scored run unless explicitly allowed — a stub rubric silently scoring
    Maths is exactly the 2026-05-18 'English-only rubric' defect again.
    """
    rdir = Path(rubrics_dir) if rubrics_dir else RUBRICS_DIR
    path = rdir / f"{subject}.md"
    if not path.is_file():
        available = sorted(p.stem for p in rdir.glob("*.md") if p.stem != "_base")
        raise SystemExit(
            f"no rubric for subject '{subject}' in {rdir} — available: {available}"
        )
    text = path.read_text(encoding="utf-8")
    if "STATUS: DRAFT" in text and not allow_draft:
        raise SystemExit(
            f"rubric '{subject}' is STATUS: DRAFT — refusing to judge with a "
            "stub rubric. Pass --allow-draft-rubrics only for dry runs."
        )
    return text


# --------------------------------------------------------------------------
# Change 4 — MANIFEST.json per run
# --------------------------------------------------------------------------

def _git_head(repo: Path) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
    except Exception:
        return None


def update_manifest(run_dir: str | Path, stage: str, payload: dict) -> Path:
    """Record a pipeline stage into <run_dir>/MANIFEST.json (merge, not clobber).

    The manifest is the run's reproducibility record: seeds, endpoints,
    model ids, GGUF sha256s, prompt SHAs, judge model, participating repo
    HEADs. Every stage writes its slice; ``repo_heads`` is captured once
    at creation and callers may extend it via payload["repo_heads"].
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "MANIFEST.json"
    now = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    if path.is_file():
        manifest = json.loads(path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema": "fleet-evals/manifest/v1",
            "created_at": now,
            "repo_heads": {"fleet-evals": _git_head(REPO_ROOT)},
        }
    extra_heads = payload.pop("repo_heads", None)
    if extra_heads:
        manifest.setdefault("repo_heads", {}).update(extra_heads)
    manifest.setdefault("stages", {})[stage] = {**payload, "recorded_at": now}
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def run_path(run_dir: str | Path, override: str | None, default_name: str) -> Path:
    """Resolve a stage file: explicit --<file> override wins, else
    <run_dir>/<default_name> (change 1 — everything rooted in the run dir)."""
    if override:
        return Path(override)
    return Path(run_dir) / default_name
