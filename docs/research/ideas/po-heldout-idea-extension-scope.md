# PO Held-Out Suite — Idea/Scope-Mode Extension (FEAT-EVAL-IDEA)

**Status:** **DRAFT** — pre-registered but NOT yet frozen. Rich freezes by commit **after**
build validation (TASK-EVI-008 hands over) and **before** any grading run. "Pre-registered"
binds the freeze to precede *grading*, not the build: the sanctioned build-time calibration
(§4) happens while this doc is DRAFT. Amendments after grading starts: never.
**Date:** 2026-07-05 (Claude Fable, attended session; parent review TASK-REV-09AB)
**Repo:** fleet-evals · **Feature:** FEAT-0760 · spec `features/idea-mode-held-out-evals/`
**Relationship to the frozen suite:** strictly additive. `po-heldout-suite-scope.md`
(FROZEN 2026-07-03), its §5 thresholds, tasks po-held-001..004, `harness/po_contract.py`,
`harness/grading.py`, and `tests/test_verifier_integrity.py` are never edited. New tasks
carry `suite = "po-heldout-idea"`, which the runner's exact-match filter
(`run_po_eval.py:330`) excludes from the frozen 12-rollout grade by construction.
**Consumer (named):** the **SPL go-live gate G2** (sovereign-planning-loop build plan) —
idea-mode quality gating before the PO agent plans in front of James. This verdict never
gates the po-ft-v1 deploy decision (that is the frozen §5's job) and §5 never gates G2.

---

## 1. Tasks

| Task | Mode | Schema | Suite | Oracle |
|---|---|---|---|---|
| `po-held-005-idea` | idea (thin input, no docs) | ProductRoadmap | po-heldout-idea | authored minimal |
| `po-held-006-scope` | scope (selection from pinned reference roadmap) | ProductRoadmap | po-heldout-idea | authored selection |

K = 3 reps per task, timeout 1800 s, artifact `response.txt`, grading via
`PO_EVAL_OUTPUT_DIR` — frozen-suite conventions verbatim (§3.4 there).

## 2. Instrument contracts (pinned here; TASK-EVI-002/003/004 build against these)

### 2.1 Anchors file schema

`tasks/<task>/test/reference/invention_anchors.json` (005) and
`constraint_anchors.json` (006 — never named `coverage_checklist.json`; that filename is
pinned by a frozen integrity check):

```json
{
  "groups": [
    {
      "id": "platform",
      "note": "which deliberate unknown this group covers",
      "alternates": ["\\bios\\b", "\\bandroid\\b", "native\\s*app", "\\bapp\\s*store\\b"]
    }
  ]
}
```

Rules: 5–8 groups for 005, derived **one per deliberate unknown** in the brief; every
group carries ≥1 short distinctive alternate; regex, matched case-insensitively over
normalized text (§2.2). **Input-disjointness:** no invention-anchor alternate may match
the task's own input texts (brief; for 006 also the reference roadmap and constraint
statement) — enforced by an integrity test. Constraint anchors are exempt from
disjointness against the constraint text (they must match it by design).

### 2.2 Normalization (central, symmetric)

One function, applied identically to requirement-bearing units, license statements, and
`constraints_and_dependencies` before any matching:
`unicodedata.normalize("NFKC", s).casefold()` + mapping unicode hyphens/dashes → `-`,
NBSP/thin spaces → ` `, curly quotes → straight. Residual (true homoglyphs) accepted —
the model under test never sees the anchors; threat model is tokenizer drift, not attack.

### 2.3 Matching granularity

Per structural unit, following the frozen `structural_units()` convention: epic unit =
name + bounded_context + description; feature unit = title + description +
bounded_context + joined constraints; `priority_rationale` its own unit.
`feature_spec_inputs` excluded (the frozen flatten-match rule already forces identity
with `epics[].features`). Epic **name** and **bounded_context** are in scope — an
invented specific in an epic name is still an invented specific.

### 2.4 Invented-requirement gate (005)

An anchor group that matches in any requirement-bearing unit is **licensed** iff it also
matches in ≥1 `assumptions[].statement` or `open_questions[]` entry (per-GROUP: any
alternate licenses the group; never per-alternate). Unlicensed match ⇒ FAIL, and the
finding **names the group, the matched text, and the unit** — the matcher returns
structured findings, never a bare bool.

**Anti-stuffing (ASSUM-009, amended):** a statement's stuffing score counts only anchor
groups that are also asserted in requirement-bearing units; a single statement scoring
**> 2** such groups licenses none of them. The threshold is calibrated in §4 before
freeze (raising to > 3 pre-freeze is legal; after freeze, immutable).

### 2.5 Scope-mode gates (006)

- **Selection-subset:** every response `feature_id` ∈ reference ids, AND the selected
  feature's `title` and `bounded_context` equal the reference's under §2.2 normalization.
  `description` is deliberately free — `player_scope.md` licenses reduced-scope rewrites
  (Coach territory). *Documented gate-stricter-than-serving divergence,* per the frozen
  suite's divergence pattern. Findings name the invented / content-swapped id.
- **Dependency-closure:** computed against the **REFERENCE roadmap's graph**, never the
  response's own `depends_on`: for every selected id, every reference-declared direct
  dependency must be selected (inductively equivalent to transitive closure). Response
  `depends_on` entries must resolve to selected ids (no dangling refs). An emptied
  `depends_on` therefore changes nothing.
- **Constraint-carried:** ALL constraint-anchor groups must match the **joined**
  `constraints_and_dependencies` text. Floor semantics: presence, not fit (§5 residuals).
- **Reference roadmap:** authored, dependency-chained (≥1 dependency-free feature,
  acyclic, unique FEAT-PO-### ids), pinned by `input/REFERENCE.sha256`; id/title/bc
  preservation mandated verbatim in `instruction.md` so the id-style habit of the
  fine-tune cannot produce systematic false failures.

### 2.6 Payload-only invariant

All new gates consume the **parsed payload dict** (post think-strip, pinned cascade via
`grading.parse_response`) — never raw response text. The think-draft-decoy good fixture
carries anchor terms inside its think block specifically to own this invariant.

### 2.7 Fixture-floor convention

Per new task, a **pinned floor list** of fixture names asserted as a superset check in
`tests/test_idea_verifier_integrity.py` — the battery may grow, never shrink below the
registered floor (ablation §6c, made mechanical; the frozen `≥1 fixture` check is weaker
and unchanged). Additionally, **every anchor group must own both** a firing broken
fixture and a licensed good fixture (assertion + natural-language license) — a group
demonstrated only in the firing direction is a topic ban, not a licensing check.

## 3. Pre-registered verdict (Rich amends then freezes; freeze precedes grading)

**Validity gate (verbatim from frozen §5):** all 6 rollouts (2 tasks × K=3) produced by
the pinned config with per-rep records; aborted/missing reps re-run, never skipped — an
incomplete run is **INVALID, not a failure**. A po-heldout-idea run must never reuse a
frozen run's `--out` directory (`run_summary.json` merges by task/rep key).

**Idea-mode go-live (SPL G2) requires all of:**

- **G-I1 — Serving shape & schema: 6/6 reps.** Every rep parses (one fence-aware think
  block; first JSON object via the pinned runtime cascade), asserts its task's pinned
  mode, and passes the full frozen ProductRoadmap battery.
- **G-I2 — Zero ANCHOR-DETECTED unlicensed inventions and zero fabricated citations
  across all reps.** This is a **detection floor**, not a completeness claim: it binds
  exactly what the authored checklists detect (§2.4). Detection beyond the checklist is
  Coach territory (§5).
- **G-I3 — Assumption discipline: 3/3 idea-task reps** carry ≥3 assumptions, each with
  the complete falsifiable shape (non-empty statement and impact_if_wrong, confidence ∈
  {high, medium, low}). No upper bound — conservative-on-assumptions is acceptable.
- **G-I4 — Scope selection gates: 3/3 scope-task reps** pass selection-subset (with
  title/bc pinning), dependency-closure vs the reference graph, and the
  constraint-carried floor. G-I4 claims selection *discipline*, not selection *quality*
  (whether the cut truly fits 6 weeks is Coach/judgment territory).

**If not met:** NO-GO for the SPL exemplar on this model; the failing axis is named in
the RESULTS doc; re-grade only after a model or task-instrument revision (instrument
revisions reopen this doc *before* the next freeze, never silently). Golden-set/Coach
results never rescue a failed G-I gate, and vice versa.

## 4. Build-time calibration (sanctioned while DRAFT; results recorded here)

| Item | Method | Result (filled by TASK-EVI-005) |
|---|---|---|
| ASSUM-009 anti-stuffing threshold | Run invention gate over the 005 frontier sheet + natural compound-assumption shapes; if >2 trips the frontier baseline, raise to >3 | *(pending)* |
| Constraint-anchor paraphrase tolerance | Run constraint gate over the 006 frontier sheet; extend alternates if faithful paraphrase misses | *(pending)* |
| License-source width (statement only vs +impact_if_wrong) | Watch item: if the frontier baseline names a specific only in impact_if_wrong, widen pre-freeze | *(pending)* |

## 5. Accepted residuals — Coach territory, recorded so G-I2/G-I4 are never overread

Synonym/paraphrase evasion outside the authored checklist · licensing via an
opposite-polarity assumption (regex cannot see polarity; the gate's claim is
"surfaced, not silently asserted") · confident requirements dressed in assumption shape
(falsifiable-shape forces the form; posture quality is the Coach's axis) ·
keyword-only constraint echo masking a non-fitting selection (the gate is a
dropped-constraint floor) · true unicode homoglyphs (outside the threat model).
No negation heuristics, ever — transparent JSON checklists with no hidden logic
(frozen-suite design basis).

## 6. Baselines (filled by TASK-EVI-008 from measurement, not estimation)

| Measurement | Value |
|---|---|
| Verifier integrity, total (frozen 33 as strict green subset) | *(pending)* |
| Frozen tasks' gate results identical pre/post extension (node-id diff) | *(pending)* |
| Frozen dry-run assembly SHAs identical pre/post `--suite` change (12/12) | *(pending)* |
| New-suite dry-run assembly proven (6/6) | *(pending)* |
| Frontier sheet, po-held-005-idea: per-axis | *(pending)* |
| Frontier sheet, po-held-006-scope: per-axis | *(pending)* |
| Deliberately-stubbed sheet FAILS (owning gates named) | *(pending)* |
| Fixture floor lists (registered names) | *(pending)* |
| 38-scenario traceability map | *(pending — recorded in §8)* |

## 7. RESULTS template (stub)

`RESULTS-po-heldout-idea-<date>.md`: model id + quant + template + per-rep config records;
per-task × per-rep table with per-axis verdicts; §3 verdict applied verbatim; freeze
commit referenced; INVALID reps listed with re-run evidence.

## 8. Traceability map

*(filled by TASK-EVI-008: each of the 38 spec scenarios → owning test or fixture)*

## 9. Freeze procedure

TASK-EVI-008 fills §4/§6/§8 → this doc is handed to Rich → Rich amends §3 if needed and
**freezes by commit** (house convention: freeze = the commit that flips this Status line).
The frozen thresholds ride with the RESULTS doc. The frozen suite's own doc is untouched
throughout.
