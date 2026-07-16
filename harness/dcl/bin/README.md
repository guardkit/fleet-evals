# harness/dcl/bin — the ONE vendored DCL checker home (dcl-heldout suite)

The deterministic, offline, LLM-free DCL validity checker the `dcl-heldout`
suite grades with — the DCL **compiler itself**, shipped as a WebAssembly
playground build (`dcl.wasm` + `wasm_exec.js`) driven by a ~90-line Node harness
(`dcl-check.mjs`). `node` on PATH is the only runtime dependency.

## Source

Vendored **byte-identical** from `spike/dcl-authoring/bin/` (the DCL SPIKE S1
staging), which vendored it from upstream
**`github.com/russelleast/Capability-Language` @ `4f9fbe56`** (Apache-2.0). The
spike dir is a frozen historical record — this is the promoted, suite-owned copy
so tasks never reach into `spike/`. Full provenance (upstream paths, the WASM
`globalThis.fs` gotcha, the aarch64 arch story) is in `PROVENANCE.md`; the
integrity pins for the four vendored blobs are in `SHA256SUMS`.

## Use

```sh
node dcl-check.mjs <path-to-file.dcl>   # JSON envelope; exit 0 ok / 1 errors / 2 usage
sha256sum -c SHA256SUMS                  # integrity of the vendored blobs
```

Callers go through `harness/dcl_gates.py` (`run_checker` / `compile_findings` /
`structural_findings` / `declaration_findings`), not this script directly.
