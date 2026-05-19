"""Wheelchair model specifications.

Migrated from the legacy ``wheelchair_bot.wheelchairs`` package as part
of the Phase 0 consolidation (audit gap G-13). The legacy module now
re-exports from here with a DeprecationWarning.

Adds ``max_continuous_a`` and ``max_peak_a`` fields per model so the
Phase 1 OvercurrentMonitor has per-chair thresholds to enforce.
"""

from .base import MotorConfig, Wheelchair, WheelchairSpec
from .models import (
    InvacareTDXSP2,
    PermobilM3Corpus,
    PrideJazzyEliteHD,
    QuantumQ6Edge,
    REGISTRY,
)

__all__ = [
    "Wheelchair",
    "WheelchairSpec",
    "MotorConfig",
    "PermobilM3Corpus",
    "QuantumQ6Edge",
    "InvacareTDXSP2",
    "PrideJazzyEliteHD",
    "REGISTRY",
]
