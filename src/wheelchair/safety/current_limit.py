"""Per-motor over-current monitor (audit gap G-02).

The real trip MUST live on a dedicated MCU (e.g. ATtiny / RP2040)
reading the INA226 at >=1 kHz; Linux is not fit for hard real-time
overcurrent protection.

This module is the higher-level supervisor that:
- consumes the MCU's already-trip-protected current readings,
- logs / telemeters them,
- engages a soft stop if a trip event arrives.

Phase 1 hardware work (issue #20) builds the MCU board; this code is
the software contract it talks to.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class MotorCurrent:
    left_a: float
    right_a: float
    timestamp_s: float


@dataclass
class OvercurrentMonitor:
    max_continuous_a: float
    max_peak_a: float
    peak_window_s: float = 0.1
    stop_callback: Callable[[], None] = lambda: None  # noqa: E731
    clock: Callable[[], float] = field(default=time.monotonic)

    def __post_init__(self) -> None:
        if self.max_peak_a < self.max_continuous_a:
            raise ValueError("peak limit must be >= continuous limit")
        self._tripped = False
        self._peak_since: float | None = None

    def update(self, sample: MotorCurrent) -> bool:
        if self._tripped:
            return True
        i = max(abs(sample.left_a), abs(sample.right_a))
        if i > self.max_peak_a:
            self._trip()
        elif i > self.max_continuous_a:
            now = sample.timestamp_s
            if self._peak_since is None:
                self._peak_since = now
            elif (now - self._peak_since) >= self.peak_window_s:
                self._trip()
        else:
            self._peak_since = None
        return self._tripped

    def _trip(self) -> None:
        self._tripped = True
        self.stop_callback()

    @property
    def tripped(self) -> bool:
        return self._tripped
