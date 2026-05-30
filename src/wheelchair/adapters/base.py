"""Base class for wheelchair-bus adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass
class ControllerSignal:
    """Normalised joystick + button state from the chair's OEM controller."""

    linear: float  # -1..1
    angular: float  # -1..1
    deadman_pressed: bool = False
    emergency_pressed: bool = False
    mode_index: int = 0  # OEM "drive profile"
    horn: bool = False


@dataclass
class AdapterFrame:
    """Raw bytes on the wire with a monotonic timestamp."""

    timestamp_s: float
    arbitration_id: int  # CAN id or bus-specific message id
    data: bytes


class CANAdapter(ABC):
    family: str = "unknown"
    bitrate: int = 0

    @abstractmethod
    def decode(self, frame: AdapterFrame) -> ControllerSignal | None:
        """Return signal if frame carries it; None if uninteresting."""

    @abstractmethod
    def encode(self, signal: ControllerSignal) -> Iterable[AdapterFrame]:
        """Yield zero or more frames that express ``signal`` on the bus."""

    @abstractmethod
    def safe_idle_frames(self) -> Tuple[AdapterFrame, ...]:
        """Frames that hold the chair stationary; used during safety stop."""
