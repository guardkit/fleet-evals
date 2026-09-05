# Task: po-held-009-spec-revise-drop-example — a spec sent back with a note

You are the product-owner feature-spec tool (`po_feature_spec`, FEAT-SPL-007)
running **headless** (`--auto` semantics), and this is the **second** time you
have been asked for this specification.

The first draft was **not accepted**. It is in `input/prior/`, complete — all
four pinned files. The person who read it sent one note back:

> drop example 3, seven exactly is the rule

Produce the revised specification: the same four files, in the same layout,
with that note resolved.

## What "resolved" means here, and it is the whole task

- **Do what the note asks.** Worked example 3 of the list — the one that says a
  member who has borrowed more than seven tools still sees *at least* seven of
  them — goes. Rewording it is not dropping it. Neither is keeping the idea and
  saying it another way: nothing in the revised list may still claim that seven
  is a floor rather than the number.
- **Change nothing else.** The other five worked examples come across word for
  word, in the order they were in. A revise that also improves a sentence
  nobody asked about cannot be approved by reading the difference, and reading
  the difference is how it gets approved.
- **Keep the files honest with each other.** The `.feature` loses the matching
  scenario, the digest loses the matching entry, the summary's counts follow,
  and no assumption in the manifest is left pointing at a scenario that no
  longer exists.

## Output contract (graded)

The four pinned files, and nothing else, under `features/{kebab-feature-name}/`
— `.feature`, `_assumptions.yaml`, `_summary.md`, `_digest.yaml` — exactly the
contract po-held-007 grades (`CONTRACT-feature-spec-plan-outputs.md` Part A,
four files since specialist-agent `f23a845`). Same slug as the prior spec: this
is a revision of that specification, not a new one.

## Harness assembly

`harness/run_po_spec_eval.py --task po-held-009-spec-revise-drop-example`
sends the serving prompt, the pinned `/feature-spec` methodology template, the
four files of `input/prior/`, and the note — in the shape the forge uses when a
draft is superseded ("The prior submission was NOT accepted. Resolve this
feedback: …"). The note itself is held in `task.toml` under `[revise]`; that
table is the single source of truth for both the prompt and the grade.

Grading: `python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
directory that contains the written `features/` tree.
