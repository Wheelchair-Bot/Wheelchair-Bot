"""Tests for the post-G-22 KeyboardControl loop.

Confirms it works without the `keyboard` library, without root, and
without a TTY (the old failure modes the audit flagged).
"""

from __future__ import annotations

import io

import pytest

from wheelchair_controller.keyboard_control import KeyboardControl


class FakeController:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def move_forward(self) -> None:
        self.calls.append("forward")

    def move_backward(self) -> None:
        self.calls.append("backward")

    def turn_left(self) -> None:
        self.calls.append("left")

    def turn_right(self) -> None:
        self.calls.append("right")

    def stop(self) -> None:
        self.calls.append("stop")


def _run_with_stdin(stdin: str, monkeypatch: pytest.MonkeyPatch) -> FakeController:
    """Drive the KeyboardControl loop with a scripted stdin and return
    the FakeController call log."""
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    ctl = FakeController()
    kc = KeyboardControl(ctl)
    kc.run()
    return ctl


def test_each_command_dispatches(monkeypatch: pytest.MonkeyPatch) -> None:
    ctl = _run_with_stdin("w\ns\na\nd\n\nq\n", monkeypatch)
    # The final stop comes from the run() finally-clause.
    assert ctl.calls == ["forward", "backward", "left", "right", "stop", "stop"]


def test_quit_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    ctl = _run_with_stdin("quit\n", monkeypatch)
    assert ctl.calls == ["stop"]


def test_unknown_command_does_not_crash(monkeypatch: pytest.MonkeyPatch) -> None:
    ctl = _run_with_stdin("xyzzy\nq\n", monkeypatch)
    assert ctl.calls == ["stop"]


def test_eof_exits_cleanly_with_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    ctl = _run_with_stdin("", monkeypatch)  # immediate EOF
    assert ctl.calls == ["stop"]


def test_no_root_and_no_keyboard_module_required() -> None:
    """The whole point of G-22 — no import-time dependency on `keyboard`."""
    import wheelchair_controller.keyboard_control as kc_module

    src = open(kc_module.__file__).read()
    assert "import keyboard" not in src
    assert "from keyboard" not in src
