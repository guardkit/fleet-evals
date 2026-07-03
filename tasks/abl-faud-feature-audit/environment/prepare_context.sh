#!/usr/bin/env bash
# Generates the pinned guardkit source tarball for the task image build.
# The tarball is NOT committed (fleet-evals is public); regenerate it from any
# guardkit checkout that contains the pin. The sha256 must match CONTEXT.sha256.
set -euo pipefail

PIN=71db6d2681ee874e5fee71d2909e4096a383eba0
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDKIT_REPO="${GUARDKIT_REPO:-$HERE/../../../../guardkit}"

git -C "$GUARDKIT_REPO" archive --format=tar.gz \
    --output "$HERE/guardkit-71db6d268.tar.gz" "$PIN"

echo "generated:"
sha256sum "$HERE/guardkit-71db6d268.tar.gz"
if [[ -f "$HERE/CONTEXT.sha256" ]]; then
    echo "pinned:"
    cat "$HERE/CONTEXT.sha256"
    (cd "$HERE" && sha256sum -c CONTEXT.sha256)
fi
