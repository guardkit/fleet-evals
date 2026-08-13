# Prompt provenance — study-tutor-multisubject venue

The eight subject system prompts in this directory are BYTE-VERBATIM copies out
of the study-tutor repo (`~/Projects/appmilla_github/study-tutor`) at HEAD
`5d2d849e55bbe69c047c965bae1b48c553ea8370` (extracted 2026-08-07). They exist as
files here because a scored run must pin a sha256 per prompt — you cannot pin a
SHA to a bash heredoc buried in a runbook (Lane 1 design pin, prerequisite (e)).

**These files are frozen evidence inputs.** Any change to a tutor prompt happens
in study-tutor first; this directory is then re-extracted and this manifest's
hashes are updated in the same commit. A hash mismatch between a file here and
this manifest voids any run that used it.

## Sources

- **Seven subject prompts** — the heredoc BODIES (content between
  `cat > "$SUBJECTS_DIR/<subject>.txt" <<'PROMPT'` and the closing `PROMPT`
  delimiter, exclusive; no added headers) in
  `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` (§5.1 "Create
  subject system prompts"). These are the exact texts the Open WebUI presets
  serve (preset table at :646–654 of the same runbook).
- **english.txt** — `roles/tutor/prompts/player.md` minus its leading one-line
  HTML comment (the comment is repo metadata, not part of the served prompt).
  player.md is itself a verbatim copy of the GB10's
  `/opt/llama-swap/models/gemma4-tutor/system-prompt.txt` (2026-05-05); that
  file no longer exists on this host, so the repo copy is the canonical text
  and THIS extraction is the pinnable artefact (scored-run blocker 2).

## Per-file manifest

| File | Source path (in study-tutor @ `5d2d849e`) | Line range | sha256 |
|---|---|---|---|
| `maths.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 521–533 | `9f4b13a36e991213754fe520de06e81c220d961df560650b2aa98b2a5fa31008` |
| `french.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 538–549 | `6915cf95cdad409c63705fd1f2f9df8df3648dc3626d68c9f53868c22bf063a9` |
| `spanish.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 554–565 | `869607e56957c0c7c3333312d74dd461e56b3ea0f70f199caa570a09bc44cc19` |
| `history.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 570–582 | `00225d8c7c4a9fbc650aa0bcf7012c85f9b22b4ecee00edaf9bfe444b59d57d5` |
| `biology.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 587–598 | `92eef9445ec117340ffeac10eeff48f8bc7a2b10e8ddc1fac1ee1418eb5a1036` |
| `chemistry.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 603–614 | `1756332cad14b8d75500b94303f2d824105fe5e92aef9b05e8270555f5633be7` |
| `physics.txt` | `docs/research/ideas/RUNBOOK-open-webui-tutor-access.md` | 619–631 | `995ac61905f50b65ebf97f56d2167d46a35269c06237184e52098f4324f45429` |
| `english.txt` | `roles/tutor/prompts/player.md` (minus line 1, the HTML comment) | 2–14 | `998a6f1ac3d7601b75f8b4dbb82ac05bd3c8b2f87c167f78a466f3715e832104` |

Verify at any time:

```bash
cd venues/study-tutor-multisubject/prompts && sha256sum -c <(awk -F'|' \
  '{gsub(/[` ]/,"",$2); gsub(/[` ]/,"",$5)} $5 ~ /^[0-9a-f]{64}$/ {print $5"  "$2}' \
  PROMPTS-PROVENANCE.md)
```

## Open WebUI preset binding (for probe re-runs)

| preset_id | Prompt file | Note |
|---|---|---|
| `gcse-maths` | `maths.txt` | |
| `gcse-french` | `french.txt` | |
| `gcse-spanish` | `spanish.txt` | |
| `gcse-history` | `history.txt` | |
| `gcse-biology` | `biology.txt` | |
| `gcse-chemistry` | `chemistry.txt` | Preset exists and is correct — the 2026-05-era EVIDENCE ran both Chemistry probes under `gcse-biology` (see `../probes-17/probes.jsonl` C1/C2 annotations). |
| `gcse-physics` | `physics.txt` | Preset + prompt exist but the 17-probe protocol has NO physics probes — physics coverage is an open gap. |
| (English fine-tune preset) | `english.txt` | Served as the model's system prompt, not via a subject heredoc. |
