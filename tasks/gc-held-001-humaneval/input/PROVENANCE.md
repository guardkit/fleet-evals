# Provenance — gc-held-001-humaneval pinned subset

- **Source:** HumanEval (`openai/human-eval`, `data/HumanEval.jsonl.gz`), retrieved 2026-07-10
  from https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz @ upstream commit `463c980b59e818ace59f6f9803cd92c749ceae61`.
- **Licence:** MIT. Copyright (c) 2021 OpenAI.
  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to the following
  conditions: The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS",
  WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
  OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
- **Changes:** 25-row subset per the pinned selection rule (manifest.json); rows
  re-serialized to this repo's canonical row.json form (field subset recorded in the
  manifest); reference tests held grader-side.
- **Contamination residual (pre-registered):** these rows are public data present in
  base-model pretraining; the suite reports RELATIVE regression only, never absolute
  capability.
