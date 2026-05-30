"""Canonical wheelchair model registry.

Tier-1 (Phase 3 alpha): Permobil M3, Quantum Q6, Invacare TDX, Pride Jazzy.
Add new models here, register in REGISTRY, then write tests.
"""

from __future__ import annotations

from typing import Dict

from .base import MotorConfig, Wheelchair, WheelchairSpec


_PERMOBIL_M3_SPEC = WheelchairSpec(
    name="Permobil M3 Corpus",
    max_speed_mps=2.2,
    wheel_base_m=0.45,
    wheel_diameter_m=0.35,
    motor=MotorConfig(
        drive_type="mid_wheel_drive",
        motor_count=2,
        motor_type="brushless_dc",
        max_voltage_v=24.0,
        max_continuous_a=30.0,
        max_peak_a=50.0,
    ),
    aliases=("permobil_m3", "m3_corpus"),
)

_QUANTUM_Q6_SPEC = WheelchairSpec(
    name="Quantum Q6 Edge",
    max_speed_mps=2.68,
    wheel_base_m=0.42,
    wheel_diameter_m=0.33,
    motor=MotorConfig(
        drive_type="mid_wheel_drive",
        motor_count=2,
        motor_type="brushed_dc",
        max_voltage_v=24.0,
        max_continuous_a=28.0,
        max_peak_a=45.0,
    ),
    aliases=("quantum_q6", "q6_edge"),
)

_INVACARE_TDX_SPEC = WheelchairSpec(
    name="Invacare TDX SP2",
    max_speed_mps=2.24,
    wheel_base_m=0.50,
    wheel_diameter_m=0.36,
    motor=MotorConfig(
        drive_type="rear_wheel_drive",
        motor_count=2,
        motor_type="brushed_dc",
        max_voltage_v=24.0,
        max_continuous_a=25.0,
        max_peak_a=40.0,
    ),
    aliases=("invacare_tdx", "tdx_sp2"),
)

_PRIDE_JAZZY_SPEC = WheelchairSpec(
    name="Pride Jazzy Elite HD",
    max_speed_mps=1.79,
    wheel_base_m=0.48,
    wheel_diameter_m=0.30,
    motor=MotorConfig(
        drive_type="front_wheel_drive",
        motor_count=2,
        motor_type="brushed_dc",
        max_voltage_v=24.0,
        max_continuous_a=22.0,
        max_peak_a=35.0,
    ),
    aliases=("pride_jazzy", "jazzy_elite"),
)


class PermobilM3Corpus(Wheelchair):
    spec = _PERMOBIL_M3_SPEC


class QuantumQ6Edge(Wheelchair):
    spec = _QUANTUM_Q6_SPEC


class InvacareTDXSP2(Wheelchair):
    spec = _INVACARE_TDX_SPEC


class PrideJazzyEliteHD(Wheelchair):
    spec = _PRIDE_JAZZY_SPEC


REGISTRY: Dict[str, type[Wheelchair]] = {}
for cls in (PermobilM3Corpus, QuantumQ6Edge, InvacareTDXSP2, PrideJazzyEliteHD):
    REGISTRY[cls.spec.name] = cls
    for alias in cls.spec.aliases:
        REGISTRY[alias] = cls
