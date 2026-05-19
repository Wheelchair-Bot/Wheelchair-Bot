"""Software command watchdog.

Closes audit gap G-01: stale commands must drive motors to zero within a
bounded time. The watchdog is a monotonic-clock timer that the control loop
"feeds" each time a fresh command is processed. If it expires, callers MUST
command motors to zero before any further movement is permitted.

Phase 1 will extend this with a hardware watchdog (GPIO line that the kernel
periodically toggles; if the toggle stops, an external monostable opens the
e-stop relay). This module is the software half.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


class WatchdogExpired(RuntimeError):
    """Raised when a caller asks for status after the watchdog expired."""


@dataclass
class CommandWatchdog:
    """Monotonic-clock command watchdog.

    Args:
        timeout_s: maximum allowed gap between successive ``feed()`` calls.
            Default 0.1 s (100 ms) — matches the safety test contract.
        clock: callable returning a monotonic time in seconds. Injected for
            tests; default ``time.monotonic``.
    """

    timeout_s: float = 0.1
    clock: object = time.monotonic

    def __post_init__(self) -> None:
        if self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self._last_feed: float | None = None

    def feed(self) -> None:
        """Mark that a fresh command was just processed."""
        self._last_feed = self.clock()  # type: ignore[operator]

    def is_alive(self) -> bool:
        """True if a recent ``feed()`` keeps the watchdog within timeout."""
        if self._last_feed is None:
            return False
        return (self.clock() - self._last_feed) < self.timeout_s  # type: ignore[operator]

    def time_since_feed(self) -> float | None:
        """Seconds since the most recent feed, or ``None`` if never fed."""
        if self._last_feed is None:
            return None
        return self.clock() - self._last_feed  # type: ignore[operator]

    def assert_alive(self) -> None:
        """Raise ``WatchdogExpired`` if not currently alive."""
        if not self.is_alive():
            raise WatchdogExpired(
                f"command watchdog expired (timeout={self.timeout_s}s, "
                f"since_feed={self.time_since_feed()})"
            )
