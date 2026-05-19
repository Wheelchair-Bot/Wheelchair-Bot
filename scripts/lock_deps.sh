#!/usr/bin/env bash
# Regenerate pinned lockfiles from the unpinned requirements*.txt /
# pyproject.toml inputs (audit gap G-19).
#
# Usage:  scripts/lock_deps.sh
# Requires: pip-tools >= 7.0 in the active venv.

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v pip-compile >/dev/null 2>&1; then
    echo "pip-compile not found. Install with:  pip install pip-tools" >&2
    exit 1
fi

echo "Compiling requirements.lock from requirements.txt ..."
pip-compile --quiet --resolver=backtracking --strip-extras \
    --output-file=requirements.lock \
    requirements.txt

echo "Compiling requirements-dev.lock from requirements-dev.txt ..."
pip-compile --quiet --resolver=backtracking --strip-extras \
    --output-file=requirements-dev.lock \
    requirements-dev.txt

echo "Compiling requirements-docker.lock from requirements-docker.txt ..."
pip-compile --quiet --resolver=backtracking --strip-extras \
    --output-file=requirements-docker.lock \
    requirements-docker.txt

echo "Done. Commit the .lock files."
