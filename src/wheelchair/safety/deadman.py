"""Deadman switch with mandatory stop-callback (audit gap G-03).

The legacy `wheelchair_bot/safety/deadman.py` only sets a flag on expiry;
the motor stop happens on the next loop iteration, creating a race.

This implementation requires a `stop_callback` at construction time and
invokes it synchronously the instant expiry is detected, so the GPIO
goes low in the same call that observes the timeout. Phase 1 hardware
work (issue #21) wires this callback to the PWM-disable GPIO pin via
the e-stop relay so a stuck Python interpreter cannot defer the stop.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class DeadmanSwitch:
    """Operator-presence switch with hard timeout.

    Args:
        timeout_s: maximum gap between `press()` calls before expiry.
        stop_callback: invoked synchronously the moment expiry is detected.
            Phase-1 production wiring uses this to drop the PWM-disable GPIO.
        clock: monotonic-clock function; injected for tests.
    """

    timeout_s: float
    stop_callback: Callable[[], None]
    clock: Callable[[], float] = field(default=time.monotonic)

    def __post_init__(self) -> None:
        if self.timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self._last_press: float | None = None
        self._stopped = False

    def press(self) -> None:
        """Operator confirms presence."""
        self._last_press = self.clock()
        self._stopped = False

    def release(self) -> None:
        """Operator explicitly releases — equivalent to immediate expiry."""
        self._last_press = None
        self._fire_stop()

    def check(self) -> bool:
        """Run periodic expiry check; fires stop callback if expired.

        Returns ``True`` while the deadman is held; ``False`` after expiry.
        """
        if self._last_press is None:
            self._fire_stop()
            return False
        if (self.clock() - self._last_press) >= self.timeout_s:
            self._fire_stop()
            return False
        return True

    @property
    def stopped(self) -> bool:
        return self._stopped

    def _fire_stop(self) -> None:
        if not self._stopped:
            self._stopped = True
            self.stop_callback()
