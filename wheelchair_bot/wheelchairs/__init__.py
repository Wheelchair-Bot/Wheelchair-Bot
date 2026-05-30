"""DEPRECATED — re-exports from ``wheelchair.wheelchairs``.

Migrated in Phase 0 consolidation (audit gap G-13). New code MUST
import from ``wheelchair.wheelchairs``. This shim raises a
DeprecationWarning on first import and forwards the legacy names to
the canonical classes:

  wheelchair_bot.wheelchairs.PermobilM3Corpus → wheelchair.wheelchairs.PermobilM3Corpus
  wheelchair_bot.wheelchairs.QuantumQ6Edge    → same
  wheelchair_bot.wheelchairs.InvacareTPG      → InvacareTDXSP2 (renamed)
  wheelchair_bot.wheelchairs.PrideJazzy       → PrideJazzyEliteHD (renamed)

The shim disappears at the end of Phase 0 (deadline in PACKAGE_LAYOUT.md).
"""

from __future__ import annotations

import warnings as _warnings

from wheelchair.wheelchairs import (
    InvacareTDXSP2 as _InvacareTDXSP2,
)
from wheelchair.wheelchairs import (
    PermobilM3Corpus,
    PrideJazzyEliteHD as _PrideJazzyEliteHD,
    QuantumQ6Edge,
    Wheelchair,
)

_warnings.warn(
    "wheelchair_bot.wheelchairs is deprecated; import from "
    "wheelchair.wheelchairs instead. See docs/PACKAGE_LAYOUT.md.",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy aliases kept for backward compat during the deprecation window.
InvacareTPG = _InvacareTDXSP2
PrideJazzy = _PrideJazzyEliteHD

__all__ = [
    "Wheelchair",
    "PermobilM3Corpus",
    "QuantumQ6Edge",
    "InvacareTPG",
    "PrideJazzy",
]
