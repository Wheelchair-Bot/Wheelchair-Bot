"""Low-voltage cutoff (audit gap G-06).

For a nominal 24 V lead-acid / Li-ion wheelchair pack:
- Warn at 23.5 V
- Cut at 22.5 V (sustained 1 s to debounce regen spikes)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class LVCState(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CUTOFF = "cutoff"


@dataclass
class LowVoltageCutoff:
    warn_v: float = 23.5
    cutoff_v: float = 22.5
    debounce_s: float = 1.0
    stop_callback: Callable[[], None] = lambda: None  # noqa: E731
    clock: Callable[[], float] = field(default=time.monotonic)

    def __post_init__(self) -> None:
        if self.cutoff_v >= self.warn_v:
            raise ValueError("cutoff_v must be below warn_v")
        self._under_since: float | None = None
        self._state: LVCState = LVCState.NORMAL

    def update(self, voltage_v: float) -> LVCState:
        if self._state == LVCState.CUTOFF:
            return self._state
        if voltage_v <= self.cutoff_v:
            now = self.clock()
            if self._under_since is None:
                self._under_since = now
                self._state = LVCState.WARNING  # in debounce window
            elif (now - self._under_since) >= self.debounce_s:
                self._state = LVCState.CUTOFF
                self.stop_callback()
            else:
                self._state = LVCState.WARNING
        elif voltage_v <= self.warn_v:
            self._under_since = None
            self._state = LVCState.WARNING
        else:
            self._under_since = None
            self._state = LVCState.NORMAL
        return self._state

    @property
    def state(self) -> LVCState:
        return self._state
