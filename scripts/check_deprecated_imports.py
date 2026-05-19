#!/usr/bin/env python3
"""Fail CI if production code imports a deprecated package.

Enforces the contract in docs/PACKAGE_LAYOUT.md.

Today (Phase 0) this script *warns* but does not fail; it will start failing
on the deadlines listed in PACKAGE_LAYOUT.md. The warning behaviour gives
existing code a grace window while consolidation lands.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEPRECATED_PACKAGES = {
    # name: (replacement, fail_after_phase)
    "wheelchair_controller": ("wheelchair.drives.hardware.l298n", "phase-1"),
    "wheelchair_bot": ("wheelchair.*", "phase-0"),
}

EXCLUDED_DIRS = {".git", "node_modules", "dist", "build", "tests", "src/tests"}


def is_test_file(path: Path) -> bool:
    parts = set(path.parts)
    if "tests" in parts or path.name.startswith("test_"):
        return True
    return False


def find_offending_imports(root: Path) -> list[tuple[Path, int, str]]:
    offences: list[tuple[Path, int, str]] = []
    for py in root.rglob("*.py"):
        rel = py.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if is_test_file(rel):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.Import):
                for n in node.names:
                    mod = n.name.split(".")[0]
                    if mod in DEPRECATED_PACKAGES:
                        offences.append((rel, node.lineno, n.name))
            elif isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module.split(".")[0]
                if mod in DEPRECATED_PACKAGES:
                    offences.append((rel, node.lineno, node.module))
    return offences


def main() -> int:
    offences = find_offending_imports(REPO_ROOT)
    if not offences:
        print("No deprecated imports found.")
        return 0
    print("Deprecated-import warnings (will fail CI at their phase deadlines):")
    for path, line, name in offences:
        replacement, phase = DEPRECATED_PACKAGES[name.split(".")[0]]
        print(f"  {path}:{line}  {name}  →  {replacement}  (fail after {phase})")
    # Phase 0: warn only.
    return 0


if __name__ == "__main__":
    sys.exit(main())
