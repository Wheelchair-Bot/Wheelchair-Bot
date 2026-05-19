"""Wheelchair base type.

Adds frozen dataclasses for ``MotorConfig`` and ``WheelchairSpec`` so
models can be defined declaratively. The runtime ``Wheelchair`` class
keeps the legacy mutable velocity-state API for backward compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class MotorConfig:
    """Per-chair motor parameters.

    Phase 1 (`wheelchair.safety.OvercurrentMonitor`) uses ``max_continuous_a``
    and ``max_peak_a`` to set per-chair trip thresholds.
    """

    drive_type: str  # "mid_wheel_drive" | "rear_wheel_drive" | "front_wheel_drive"
    motor_count: int
    motor_type: str  # "brushless_dc" | "brushed_dc"
    max_voltage_v: float
    max_continuous_a: float
    max_peak_a: float

    def __post_init__(self) -> None:
        if self.max_peak_a < self.max_continuous_a:
            raise ValueError("max_peak_a must be >= max_continuous_a")


@dataclass(frozen=True)
class WheelchairSpec:
    """Declarative spec for a wheelchair model."""

    name: str
    max_speed_mps: float
    wheel_base_m: float
    wheel_diameter_m: float
    motor: MotorConfig
    aliases: Tuple[str, ...] = field(default_factory=tuple)


class Wheelchair:
    """Runtime wheelchair instance.

    Holds the immutable spec and the mutable velocity state. Concrete
    model classes (Permobil M3, Quantum Q6, …) are thin subclasses
    that bind a single `WheelchairSpec`.
    """

    spec: WheelchairSpec

    def __init__(self) -> None:
        if not hasattr(self, "spec"):
            raise TypeError(
                f"{type(self).__name__} must define a class-level WheelchairSpec"
            )
        self._linear: float = 0.0
        self._angular: float = 0.0

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def max_speed(self) -> float:
        return self.spec.max_speed_mps

    @property
    def wheel_base(self) -> float:
        return self.spec.wheel_base_m

    @property
    def wheel_diameter(self) -> float:
        return self.spec.wheel_diameter_m

    def get_motor_config(self) -> dict:
        m = self.spec.motor
        return {
            "type": m.drive_type,
            "motor_count": m.motor_count,
            "motor_type": m.motor_type,
            "max_voltage": m.max_voltage_v,
            "max_current": m.max_continuous_a,
            "max_peak_current": m.max_peak_a,
        }

    def set_velocity(self, linear: float, angular: float) -> None:
        self._linear = max(-1.0, min(1.0, linear))
        self._angular = max(-1.0, min(1.0, angular))

    def get_velocity(self) -> Tuple[float, float]:
        return self._linear, self._angular

    def stop(self) -> None:
        self._linear = 0.0
        self._angular = 0.0

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "max_speed": self.max_speed,
            "wheel_base": self.wheel_base,
            "wheel_diameter": self.wheel_diameter,
        }
