"""Panda CAN bridge wrapper.

The panda is the hardware that sits between Linux and the chair's CAN
bus. Linux talks to it over USB (red panda / panda tres) or PCIe
(comma four, when its SDK ships).

We use panda's *safety modes* — the panda firmware refuses to forward
sendcan frames unless its safety mode is in ALLOUTPUT, and it can be
configured to drop all output if heartbeats stop. This is the hardware
foundation that the Phase 1 software watchdog (CommandWatchdog) is
meant to align with.

Like cereal, the actual `panda` Python package is not bundled. When
absent, this module exposes a fake that records traffic for tests.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SafetyMode(IntEnum):
    NOOUTPUT = 0
    SILENT = 1
    ALLOUTPUT = 17


@dataclass
class FakePanda:
    """Stand-in for the real panda when the package isn't installed."""

    safety_mode: SafetyMode = SafetyMode.NOOUTPUT
    sent: List[Tuple[int, int, bytes, int]] = field(default_factory=list)
    received: List[Tuple[int, int, bytes, int]] = field(default_factory=list)
    heartbeats: int = 0

    def set_safety_mode(self, mode: SafetyMode) -> None:
        self.safety_mode = mode

    def can_send(self, addr: int, dat: bytes, bus: int = 0, timeout: int = 0) -> None:
        if self.safety_mode is not SafetyMode.ALLOUTPUT:
            raise PermissionError("panda safety mode blocks sendcan")
        self.sent.append((addr, len(dat), dat, bus))

    def can_recv(self) -> List[Tuple[int, int, bytes, int]]:
        out = list(self.received)
        self.received.clear()
        return out

    def send_heartbeat(self) -> None:
        self.heartbeats += 1


@dataclass
class PandaBridge:
    """High-level wrapper used by drives.comma_panda."""

    panda: object  # FakePanda in tests, real Panda on device

    def enable_output(self) -> None:
        self.panda.set_safety_mode(SafetyMode.ALLOUTPUT)

    def disable_output(self) -> None:
        self.panda.set_safety_mode(SafetyMode.NOOUTPUT)

    def send(self, addr: int, data: bytes, bus: int = 0) -> None:
        try:
            self.panda.can_send(addr, data, bus=bus)
        except PermissionError:
            logger.warning("panda refused send addr=0x%x — safety mode is gating", addr)
            raise

    def recv(self) -> List[Tuple[int, int, bytes, int]]:
        return list(self.panda.can_recv())

    def heartbeat(self) -> None:
        self.panda.send_heartbeat()
