"""Keyboard control for the legacy main.py entry point.

Closes audit gap G-22 by removing the `keyboard` Python library
dependency. The previous implementation tried to import `keyboard` for
"real-time" key detection — which only works as root, only with a TTY,
and refuses to load in Docker. Both failure modes hit production users.

The right place for real-time low-latency input is the **client**
(Android joystick or web UI), not the Pi reading its own attached
keyboard. The Pi exposes the WebSocket control endpoint
(`wheelchair.app.server` from Phase 2) and the client sends frames.

This module is kept only for the legacy `python main.py` command:
line-buffered ``input()``-based control. It's intentionally simple
and intentionally not real-time; if you need real-time, use the
tele-op WS client.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


class KeyboardControl:
    """Line-buffered keyboard control. No external lib, no root."""

    def __init__(self, controller: Any) -> None:
        self.controller = controller
        self.running = False

    def print_instructions(self) -> None:
        print(
            "\n"
            + "=" * 50
            + "\n"
            "Wheelchair Controller — line-buffered keyboard input\n"
            + "=" * 50
            + "\n"
            "Type a letter and press <Enter>:\n"
            "  w — forward       a — left\n"
            "  s — backward      d — right\n"
            "  (blank) — stop    q — quit\n"
            "\n"
            "For real-time control use the WS tele-op client (web/Android),\n"
            "not this loop.\n"
            + "=" * 50
            + "\n",
            flush=True,
        )

    def run(self) -> None:
        self.print_instructions()
        self.running = True
        try:
            while self.running:
                command = self._read_command()
                if command is None:
                    break
                self._dispatch(command)
        finally:
            self.controller.stop()

    def _read_command(self) -> str | None:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        return line.lower().strip()

    def _dispatch(self, command: str) -> None:
        if command in ("w", "forward"):
            print("forward")
            self.controller.move_forward()
        elif command in ("s", "backward", "back"):
            print("backward")
            self.controller.move_backward()
        elif command in ("a", "left"):
            print("left")
            self.controller.turn_left()
        elif command in ("d", "right"):
            print("right")
            self.controller.turn_right()
        elif command in ("", " ", "stop"):
            print("stop")
            self.controller.stop()
        elif command in ("q", "quit", "exit"):
            print("quit")
            self.running = False
        else:
            print(f"unknown: {command!r} (try: w/s/a/d/<blank>/q)", file=sys.stderr)

    def cleanup(self) -> None:
        self.running = False
        self.controller.stop()
