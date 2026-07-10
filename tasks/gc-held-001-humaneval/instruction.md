# gc-held-001-humaneval — instruction (the operative prompt contract)

One rep = one fresh generation per pinned row against the served checkpoint
(llama-swap, toolless chat completion). K = 3 reps. No tools, no grammar.

## Prompt (pinned; hash-recorded per rep — ASSUM-009)

- **System** (`gc_rows.PINNED_SYSTEM_PROMPT`):
  > You are a careful Python programmer. Solve the task exactly as specified. Output ONE
  > fenced Python code block containing a complete, self-contained solution. No prose
  > outside the code block.
- **User** (`gc_rows.user_prompt`, HumanEval form): the row's signature+docstring prompt
  inside a ```python fence, followed by:
  > Output the complete function definition (including the signature shown) in a single
  > ```python code block. Do not include tests or example usage.

## Sampling (serving-faithful — ASSUM-006)

The candidate seat's deployed posture where one exists; base-model baselines at
temperature 0.1 / top_p 0.9, max_tokens 2048.

## Output contract (extraction — pinned in `gc_gates.extract_program`)

First fenced code block wins (trailing prose tolerated); a bare response that parses as
Python is accepted; anything else is a row FAIL with an extraction reason — never an
INVALID run. `finish_reason == "length"` is a row FAIL recorded as `truncated-generation`,
distinct from execution failure.

## Grading

`PO_EVAL_OUTPUT_DIR=<rep-dir> python3 -m pytest test/ -q` — every verdict comes from the
row's reference assertions EXECUTED in the gc sandbox (`harness/gc_sandbox.py`; isolation
unavailable ⇒ refuse loud, grading blocked). The rep passes its regression floor iff
solved ≥ same-family baseline − 2 rows (G-G2, PROPOSED until freeze).
