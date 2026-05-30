"""Physical wheelchair-controller-bus adapters (audit gap G-10).

One module per controller family. Each implements ``CANAdapter``:

- ``decode(frame_bytes) -> ControllerSignal`` for sniffing the joystick
- ``encode(signal) -> frame_bytes`` for injecting our own commands
- ``replay(file) -> Iterable[(t, frame)]`` for cabana-format captures

Phase 3 lands the encode/decode skeletons + replay framework + per-
family pinout docs. Real protocol bring-up requires bench access to a
chair of each family; the captures live in ``tests/captures/`` (gitignored).
"""

from .base import CANAdapter, ControllerSignal
from .rnet import RNetAdapter
from .shark import SharkAdapter
from .vr2 import VR2Adapter

__all__ = ["CANAdapter", "ControllerSignal", "RNetAdapter", "SharkAdapter", "VR2Adapter"]
