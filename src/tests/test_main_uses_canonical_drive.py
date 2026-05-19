"""Tests for the post-G-09 main.py.

Confirms that main.py:
- imports the canonical L298NDrive (not the legacy MotorDriver directly)
- constructs WheelchairController via L298NDrive.motor_driver
- still works in --mock mode end-to-end
"""

from __future__ import annotations

import ast
import importlib
import io
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MAIN_PY = REPO_ROOT / "main.py"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                mods.add(n.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_main_imports_canonical_drive() -> None:
    mods = _imported_modules(MAIN_PY)
    assert "wheelchair.drives.hardware.l298n" in mods


def test_main_does_not_import_motor_driver_directly() -> None:
    """G-09: hardware drive must go through L298NDrive, not raw MotorDriver."""
    mods = _imported_modules(MAIN_PY)
    assert "wheelchair_controller.motor_driver" not in mods


def test_l298n_exposes_motor_driver_property() -> None:
    from wheelchair.drives.hardware.l298n import L298NDrive

    drive = L298NDrive(use_mock=True)
    assert drive.motor_driver is drive._md
    # Property should be usable as a MotorDriver-typed handle.
    assert hasattr(drive.motor_driver, "set_motor_speed")
    assert hasattr(drive.motor_driver, "stop")


def test_main_smoke_runs_under_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """End-to-end smoke: invoke main() with --mock and an empty stdin."""
    import importlib.util

    monkeypatch.setattr("sys.argv", ["main.py", "--mock"])
    monkeypatch.setattr("sys.stdin", io.StringIO(""))  # immediate EOF on input()
    spec = importlib.util.spec_from_file_location("wcbot_main_smoke", MAIN_PY)
    assert spec and spec.loader
    main_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_mod)
    rc = main_mod.main()
    assert rc == 0
