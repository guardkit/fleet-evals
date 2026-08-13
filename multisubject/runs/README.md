# runs/ — immutable run evidence

One directory per executed run: `runs/YYYY-MM-DD-<venue>-<slug>/`.

Rules:

- **Immutable once complete.** A run directory is evidence — never edit its
  artefacts after the fact; a corrected run is a NEW run directory.
- **Every run carries a `MANIFEST.json`** (written incrementally by every
  harness stage): seeds, endpoints, model ids, GGUF sha256s, prompt SHAs,
  judge model, participating repo HEADs. No manifest, no receipt.
- **Runs are committed.** Evidence lives in git, like study-tutor's
  `docs/runbooks/evidence/` tradition.

No runs exist yet — the first scored run is a later, attended step (three
operator blockers are open; see the repo README).
