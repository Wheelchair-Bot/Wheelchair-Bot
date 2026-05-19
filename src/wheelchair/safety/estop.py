"""Emergency-stop coordinator (audit gap G-04 software half).

Aggregates every safety subsystem's `stop_callback` into a single
fan-out: any one of {watchdog expiry, deadman release, tilt trip, LVC
cutoff, overcurrent trip, explicit operator e-stop} engages a latched
stop. Release requires explicit `clear()` after the operator confirms.

The fan-out also pulses the *hardware* e-stop GPIO line, which on a
properly-built Phase-1 board is wired through a latching relay that
drops motor power independent of any software state (issue #22).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List


class EStopReason(Enum):
    OPERATOR = "operator"
    WATCHDOG = "watchdog"
    DEADMAN = "deadman"
    TILT = "tilt"
    LVC = "lvc"
    OVERCURRENT = "overcurrent"
    EXTERNAL = "external"


@dataclass
class EStopEvent:
    reason: EStopReason
    detail: str = ""


@dataclass
class EmergencyStop:
    motor_stop: Callable[[], None]
    hardware_gpio_drop: Callable[[], None] = lambda: None  # noqa: E731
    listeners: List[Callable[[EStopEvent], None]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._engaged: EStopEvent | None = None

    def engage(self, reason: EStopReason, detail: str = "") -> None:
        with self._lock:
            if self._engaged is not None:
                return
            self._engaged = EStopEvent(reason=reason, detail=detail)
        # Outside lock: callbacks must not deadlock.
        try:
            self.motor_stop()
        finally:
            self.hardware_gpio_drop()
            for cb in self.listeners:
                try:
                    cb(self._engaged)
                except Exception:  # noqa: BLE001
                    pass

    def is_engaged(self) -> bool:
        return self._engaged is not None

    @property
    def event(self) -> EStopEvent | None:
        return self._engaged

    def clear(self, operator_confirm: bool = False) -> None:
        """Release the latch. Requires explicit operator confirmation."""
        if not operator_confirm:
            raise PermissionError(
                "E-stop clear requires explicit operator_confirm=True"
            )
        with self._lock:
            self._engaged = None
