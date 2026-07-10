# Provenance — gc-held-002-mbpp pinned subset

- **Source:** MBPP — Mostly Basic Python Problems (Austin et al., 2021,
  "Program Synthesis with Large Language Models"), `google-research/google-research`,
  `mbpp/mbpp.jsonl`, retrieved 2026-07-10 from https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl @ upstream commit `f82046ba5aabbbb427dbfd38a254d26bff08b533`.
- **Licence:** CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
  Attribution: Google Research, MBPP dataset. This subset is redistributed under the
  same licence with changes noted below.
- **Changes:** 25-row subset per the pinned selection rule (manifest.json); rows
  re-serialized to this repo's canonical row.json form (field subset recorded in the
  manifest — `challenge_test_list` not carried); the benchmark's reference asserts are
  shown to the model in the prompt (the standard MBPP convention, ASSUM-009) and
  executed grader-side.
- **Contamination residual (pre-registered):** these rows are public data present in
  base-model pretraining; the suite reports RELATIVE regression only, never absolute
  capability.
