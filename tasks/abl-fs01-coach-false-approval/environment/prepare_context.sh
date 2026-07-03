#!/usr/bin/env bash
# Generates the pinned fleet-memory source tarball for the task image build.
# The tarball is NOT committed (fleet-evals is public); regenerate it from any
# fleet-memory checkout that contains the pin. The sha256 must match
# CONTEXT.sha256.
set -euo pipefail

PIN=92ef8979865c469cf76c88277fb1f327a4d3954b
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLEET_MEMORY_REPO="${FLEET_MEMORY_REPO:-$HERE/../../../../fleet-memory}"

git -C "$FLEET_MEMORY_REPO" archive --format=tar.gz \
    --output "$HERE/fleet-memory-92ef897.tar.gz" "$PIN"

echo "generated:"
sha256sum "$HERE/fleet-memory-92ef897.tar.gz"
if [[ -f "$HERE/CONTEXT.sha256" ]]; then
    echo "pinned:"
    cat "$HERE/CONTEXT.sha256"
    (cd "$HERE" && sha256sum -c CONTEXT.sha256)
fi
