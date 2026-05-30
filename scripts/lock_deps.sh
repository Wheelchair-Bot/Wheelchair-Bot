#!/usr/bin/env bash
# Regenerate the pinned .lock files from the .in sources
# (audit gap G-19).
#
# Usage:  scripts/lock_deps.sh
# Requires: pip-tools >= 7.0 in the active venv.
#
# Note: pi.lock is NOT generated here because RPi.GPIO has no macOS /
# x86_64 wheels. See requirements/README.md for the Docker buildx
# incantation that generates pi.lock on linux/arm64.

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v pip-compile >/dev/null 2>&1; then
    echo "pip-compile not found. Install with:  pip install pip-tools" >&2
    exit 1
fi

mkdir -p requirements

compile () {
    local in_file="$1" out_file="$2"
    echo "compiling $in_file → $out_file"
    pip-compile --quiet --resolver=backtracking --strip-extras \
        --output-file="$out_file" "$in_file"
}

compile requirements/sim.in requirements/sim.lock
compile requirements/dev.in requirements/dev.lock

echo
echo "Done. Commit the .lock files."
echo "For pi.lock, see requirements/README.md (needs linux/arm64)."
