"""S-4 calibration harness — run the R-b S1+S2+S3 pipeline over the FEAT-DD4F
gold diff (d13d88f..1fcb72c, src surface) on the local seat and capture raw output
+ emitted F14 records. Scoring is done by hand against gold/gold-set.json.

Two measured runs (honesty-to-state, both recorded):
  Run A = the pipeline AS SHIPPED: run_advisory_review defaults (guardkit's own
          _default_seat_call -> qwen36 thinking-ON, max_tokens=4096; diff rendered
          with the built 60000-char cap). Documents what ships today.
  Run B = the fair seat-capability measure: same S1 payload + the same S2 review
          contract (_REVIEW_SYSTEM) + the same S3 emit_review_findings honesty
          transform, but with the seat configured fairly (thinking-OFF via
          chat_template_kwargs, max_tokens=8192) and the diff rendered without
          truncation, fed in 4 subsystem groups that keep cross-file finding
          pairs together.
"""
from __future__ import annotations
import json, sys, time, urllib.request
from pathlib import Path

GUARDKIT = Path("/home/richardwoollcott/Projects/appmilla_github/guardkit")
sys.path.insert(0, str(GUARDKIT))
import os
os.environ["GUARDKIT_QA_REVIEW_SEAT"] = "1"  # force flag ON for the as-shipped run

from guardkit.qa import diff_ingest as di
from guardkit.qa import review_seat as rs
from guardkit.qa.diff_ingest import ReviewPayload

FORGE = Path("/home/richardwoollcott/Projects/appmilla_github/forge")
OUT = Path("/home/richardwoollcott/Projects/appmilla_github/fleet-evals/calibration/code-review-seat")
RAW = OUT / "seat-output"
BASE_URL = "http://localhost:9000/v1"
MODEL = "qwen36-workhorse"

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def slot_note():
    try:
        with urllib.request.urlopen("http://localhost:9000/running", timeout=5) as r:
            running = json.load(r).get("running", [])
    except Exception as e:
        return f"running-probe unreachable ({e}) — proceeding"
    free, reason = rs.check_single_slot(running)
    if not free:
        return rs._await_free_slot(rs._default_running_probe(BASE_URL))
    return reason

# ---- S1: ingest the full merge range, keep only the src reviewable surface ----
full = di.ingest_range(FORGE, "d13d88f", "1fcb72c", context_lines=3)
src_files = tuple(fd for fd in full.files if (fd.path or "").startswith("src/forge/"))
def sub(files):
    return ReviewPayload(subject_kind="merge", ref="d13d88f..1fcb72c",
                         context_lines=full.context_lines, files=tuple(files))
src_payload = sub(src_files)

manifest = {
    "range": "d13d88f..1fcb72c", "subject_kind": "merge",
    "total_files_in_range": len(full.files),
    "src_files_reviewed": len(src_files),
    "src_files": [
        {"path": fd.path, "change_kind": fd.change_kind, "additions": fd.additions,
         "deletions": fd.deletions,
         "rendered_chars": len(rs.render_payload_for_seat(sub([fd]), max_chars=10**9))}
        for fd in src_files
    ],
    "src_total_rendered_chars": len(rs.render_payload_for_seat(src_payload, max_chars=10**9)),
    "scoping_note": ("The gold review reviewed the whole 219-file merge with 5 agents "
                     "that had repo-wide + cross-repo grep. This single-seat run is scoped "
                     "to the src/forge/ reviewable code surface (17 files) — all 16 serious "
                     "gold findings live in these files. Task .md and test files are excluded "
                     "as non-code noise the seat could not use (recorded, not hidden). One gold "
                     "LOW (L09) lives in a test file and is therefore out of the seat's surface."),
}
(OUT / "gold" / "diff-manifest.json").write_text(json.dumps(manifest, indent=2))
log(f"S1: {len(src_files)} src files, {manifest['src_total_rendered_chars']} rendered chars")

# ---- Run A: pipeline AS SHIPPED (default seat_call, 60k cap, thinking-ON, 4096) ----
log("Run A (as-shipped) — single-slot: " + slot_note())
outcome = rs.run_advisory_review(FORGE, src_payload, review_id="dd4f-runA-asshipped",
                                 model=MODEL, base_url=BASE_URL, write=False)
runA = {"config": {"seat_call": "guardkit _default_seat_call (thinking-ON, max_tokens=4096)",
                   "diff_render_cap_chars": 60000, "note": "the built pipeline defaults, unchanged"},
        "enabled": outcome.enabled, "error": outcome.error, "seat_note": outcome.seat_note,
        "emitted": outcome.emitted,
        "record": outcome.record.model_dump() if outcome.record else None,
        "n_findings": len(outcome.record.findings) if outcome.record else 0}
(RAW / "runA-asshipped-outcome.json").write_text(json.dumps(runA, indent=2, default=str))
log(f"Run A: emitted={outcome.emitted} n_findings={runA['n_findings']} error={outcome.error}")

# ---- Run B: fair seat config, thinking-OFF, grouped, no truncation ----
def fair_seat_call(system_prompt, user_prompt, model):
    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key="not-needed", timeout=900.0)
    resp = client.chat.completions.create(
        model=model, temperature=0.0, max_tokens=8192,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}])
    return resp.choices[0].message.content or ""

def build_msgs_full(payload):
    diff_text = rs.render_payload_for_seat(payload, max_chars=400000)  # no truncation
    user = (f"## Review subject\n\nkind: {payload.subject_kind} · ref: {payload.ref}\n\n"
            "## Diff under review (review ONLY these changes)\n\n" + diff_text)
    return rs._REVIEW_SYSTEM, user

GROUPS = {
    "G1-boot-wiring": ["src/forge/cli/serve.py", "src/forge/cli/_serve_planning.py",
                       "src/forge/planning/planner.py", "src/forge/planning/states.py"],
    "G2-checkpoint-escalation": ["src/forge/planning/checkpoint.py",
                                 "src/forge/planning/escalation.py",
                                 "src/forge/planning/gate_adapters.py"],
    "G3-store-migration": ["src/forge/planning/run_store.py",
                           "src/forge/lifecycle/migrations.py",
                           "src/forge/lifecycle/schema_v3.sql"],
    "G4-wire-handoff-config": ["src/forge/adapters/nats/planning_consumer.py",
                               "src/forge/planning/handoff.py",
                               "src/forge/config/models.py", "src/forge/config/__init__.py",
                               "src/forge/planning/__init__.py", "src/forge/planning/audit.py",
                               "src/forge/planning/frontier.py"],
}
by_path = {fd.path: fd for fd in src_files}
runB_union = []
runB_meta = {}
for gname, paths in GROUPS.items():
    files = [by_path[p] for p in paths if p in by_path]
    gp = sub(files)
    chars = len(rs.render_payload_for_seat(gp, max_chars=10**9))
    log(f"Run B {gname}: {len(files)} files, {chars} chars — single-slot: {slot_note()}")
    system, user = build_msgs_full(gp)
    t0 = time.time()
    try:
        raw = fair_seat_call(system, user, MODEL)
    except Exception as e:
        raw = ""
        log(f"  seat error: {type(e).__name__}: {e}")
    dt = time.time() - t0
    (RAW / f"runB-{gname}-raw.txt").write_text(raw)
    rec = None; err = None
    try:
        rec = rs.emit_review_findings(gp, raw, review_id=f"dd4f-runB-{gname}")
    except rs.ReviewSeatError as e:
        err = str(e)
    if rec:
        (RAW / f"runB-{gname}-f14.json").write_text(json.dumps(rec.model_dump(), indent=2, default=str))
        for f in rec.findings:
            d = f.model_dump(); d["_group"] = gname; runB_union.append(d)
    runB_meta[gname] = {"files": paths, "chars": chars, "seconds": round(dt, 1),
                        "raw_len": len(raw), "parse_error": err,
                        "n_findings": len(rec.findings) if rec else 0}
    log(f"  {gname}: {dt:.0f}s raw_len={len(raw)} n_findings={runB_meta[gname]['n_findings']} err={err}")

(RAW / "runB-union.json").write_text(json.dumps(runB_union, indent=2, default=str))
(RAW / "runB-meta.json").write_text(json.dumps(runB_meta, indent=2))
log(f"Run B DONE: union {len(runB_union)} findings across {len(GROUPS)} groups")
log("HARNESS COMPLETE")
