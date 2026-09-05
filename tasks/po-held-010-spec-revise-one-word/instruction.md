# Task: po-held-010-spec-revise-one-word — a note that changes one word

You are the product-owner feature-spec tool (`po_feature_spec`, FEAT-SPL-007)
running **headless** (`--auto` semantics), and this is the **second** time you
have been asked for this specification.

The first draft was **not accepted**. It is in `input/prior/`, complete — all
four pinned files. The person who read it sent one note back:

> the list should read newest first, not oldest first

Produce the revised specification: the same four files, in the same layout,
with that note resolved.

## What "resolved" means here, and it is the whole task

- **Change the one sentence the note is about.** Worked example 2 is the
  ordering example. It must now say the newest loan comes first, and it must no
  longer say the oldest does — in the digest sentence, and in the scenario and
  its steps behind that sentence.
- **Change nothing else.** All five other worked examples come across word for
  word, in the order they were in, and the list still has six of them. This is
  the harder half of the revise path: a note to drop something can be honoured
  by deleting a line, but here the whole list comes back and exactly one
  sentence in it may differ.
- **Keep the files honest with each other.** The digest entry and the scenario
  it compresses must still agree — same title, same tags, same order.

## Output contract (graded)

The four pinned files, and nothing else, under `features/{kebab-feature-name}/`
— `.feature`, `_assumptions.yaml`, `_summary.md`, `_digest.yaml` — exactly the
contract po-held-007 grades (`CONTRACT-feature-spec-plan-outputs.md` Part A,
four files since specialist-agent `f23a845`). Same slug as the prior spec.

## Harness assembly

`harness/run_po_spec_eval.py --task po-held-010-spec-revise-one-word` sends the
serving prompt, the pinned `/feature-spec` methodology template, the four files
of `input/prior/`, and the note — in the shape the forge uses when a draft is
superseded ("The prior submission was NOT accepted. Resolve this feedback: …").
The note itself is held in `task.toml` under `[revise]`; that table is the
single source of truth for both the prompt and the grade.

Grading: `python3 -m pytest test/ -q` with `PO_EVAL_OUTPUT_DIR` pointing at the
directory that contains the written `features/` tree.
