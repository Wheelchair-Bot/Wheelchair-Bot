"""Tilt / rollover cutoff (audit gap G-05).

Reads IMU accel data and engages a stop if the chair tilts past
`limit_deg` for `debounce_s` continuous seconds. Configurable per
wheelchair model in Phase 1.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TiltMonitor:
    """Pitch/roll cutoff with debounce.

    Args:
        limit_deg: max allowed tilt magnitude (combined pitch + roll).
        debounce_s: must sustain ``limit_deg`` for this long before tripping.
        stop_callback: invoked once on trip.
        clock: monotonic-clock function.
    """

    limit_deg: float = 25.0
    debounce_s: float = 0.2
    stop_callback: Callable[[], None] = lambda: None  # noqa: E731
    clock: Callable[[], float] = field(default=time.monotonic)

    def __post_init__(self) -> None:
        self._over_since: float | None = None
        self._tripped = False

    def update(self, accel_x: float, accel_y: float, accel_z: float) -> bool:
        """Feed a fresh accel sample (m/s² or g-units — only ratios matter).

        Returns ``True`` if currently tripped.
        """
        if self._tripped:
            return True
        tilt = self._tilt_from_accel(accel_x, accel_y, accel_z)
        if tilt >= self.limit_deg:
            now = self.clock()
            if self._over_since is None:
                self._over_since = now
            elif (now - self._over_since) >= self.debounce_s:
                self._tripped = True
                self.stop_callback()
        else:
            self._over_since = None
        return self._tripped

    @staticmethod
    def _tilt_from_accel(ax: float, ay: float, az: float) -> float:
        """Angle (deg) between gravity vector and the chair's z-axis."""
        magnitude = math.sqrt(ax * ax + ay * ay + az * az)
        if magnitude == 0:
            return 0.0
        cos_t = max(-1.0, min(1.0, az / magnitude))
        return math.degrees(math.acos(cos_t))

    @property
    def tripped(self) -> bool:
        return self._tripped

    def reset(self) -> None:
        self._over_since = None
        self._tripped = False
