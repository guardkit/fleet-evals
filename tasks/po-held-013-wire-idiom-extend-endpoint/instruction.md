# Task: po-held-013-wire-idiom-extend-endpoint — an extend-an-endpoint sentence, headless `/feature-spec`

You are the product-owner feature-spec tool (`po_feature_spec`, FEAT-SPL-007)
running **headless** (`--auto` semantics). Produce a complete BDD specification
for the sentence in `input/brief.md`, following the pinned `/feature-spec`
output contract exactly. The target repository is api_test, a running HTTP
service.

## What this exam asks

The sentence is the third of the 2026-08-25 bake-off's sentences, with the
note Rich later sent folded in: an existing route, GET /users, gains paging
with a default page of ten. The factory proves what a caller can see at the
endpoint, and it proves worked examples written that way. On 2026-09-06 a
sibling sentence stopped at the plan stage because its examples described the
database instead, and a person had to send a note.

The question graded here: given a sentence that extends an endpoint, does the
seat write **every** worked example as a request to the endpoint and the reply
it gets — the method and path, the status code, and what is in the body — so
the routing law stamps all of them by rule, with no note from anyone?

## Output contract (graded)

Write the four pinned files, and nothing else, under `features/`:

```
features/
└── {kebab-case-feature-name}/
    ├── {feature-name}.feature
    ├── {feature-name}_assumptions.yaml
    ├── {feature-name}_summary.md
    └── {feature-name}_digest.yaml
```

The shape of each file is the one po-held-007 grades (`CONTRACT-feature-spec-
plan-outputs.md` Part A, four files since specialist-agent `f23a845`). Four of
po-held-007's gates are applied here **by import**: the four-file contract,
Gherkin structure (feature story, steps, a `Then` in every scenario), every step
on a single physical line, and the digest's consistency with the `.feature`
(one entry per scenario in file order, titles and tags word for word, one plain
sentence each, every manifest assumption carried verbatim).

The rest of po-held-007's axes are **not** graded here. In particular its
domain-language axis bans HTTP status codes in steps; a worked example the
factory can prove names the method and path, the status code, and the body.
The two exams ask different questions of the same seat.

## The wire-idiom gate (the point of this task)

Every scenario in the produced `.feature` is classified with guardkit's own
routing-law rules — rules only, no model — with api_test declared as an HTTP
surface. The gate passes only when every scenario gets a home. A failure names
each refused scenario title word for word and says how to write it. A second,
softer check records how many scenarios the wire rule stamped, so the results
document can say how many worked examples were in the endpoint idiom.

## Headless (`--auto` / SPL) semantics — binding

- No questions, no curation waits: propose the full scenario set and write the
  files.
- Every assumption `confidence` is `low` and every `human_response` is
  `"deferred"`; `review_required: true`.
- The sentence is thin on purpose. Do not invent requirements; any specific it
  does not state that a scenario relies on (how the next page is asked for, the
  largest page allowed, the order users come in) must appear as a manifest
  assumption.

## Harness assembly

Answer sheets are produced by `harness/run_po_spec_eval.py --task
po-held-013-wire-idiom-extend-endpoint`: the production serving prompt, the
pinned `/feature-spec` methodology template, and this brief, one fresh session
per rep. Nothing is added to the prompt for this exam — the seat gets exactly
what production sends it. Grading: `python3 -m pytest test/ -q` with
`PO_EVAL_OUTPUT_DIR` pointing at the directory that contains the written
`features/` tree. No seat was driven when this task was written (2026-09-06);
the solution and broken trees are hand-written.
