"""R-Net adapter skeleton (Curtiss-Wright / PG Drives).

Bus: proprietary CAN at 125 kbps. Joystick frames are ~10 ms apart.

This skeleton is the **shape** the real codec will fit into once we
have bench access to a Permobil M3 (the Phase-3 alpha target). Without
captures the byte layout below is illustrative; replace once
``tests/captures/rnet_*.csv`` lands.

A note on safety: writing R-Net frames onto a live chair without
correct CRC and the matching session key WILL trigger the chair's
fault-stop. That is the *desired* failure mode for this scaffolding —
we never silently overwrite OEM commands until the captures and the
hardware e-stop relay are both in place.
"""

from __future__ import annotations

from typing import Iterable, Tuple

from .base import AdapterFrame, CANAdapter, ControllerSignal

# Provisional IDs — replace from real captures.
RNET_JOY_ID = 0x02000000
RNET_HEARTBEAT_ID = 0x14000000
RNET_BITRATE = 125_000


class RNetAdapter(CANAdapter):
    family = "rnet"
    bitrate = RNET_BITRATE

    def decode(self, frame: AdapterFrame) -> ControllerSignal | None:
        if frame.arbitration_id != RNET_JOY_ID or len(frame.data) < 4:
            return None
        # Provisional: first two bytes are signed 8-bit joystick X, Y.
        x = _s8(frame.data[0]) / 128.0
        y = _s8(frame.data[1]) / 128.0
        flags = frame.data[2]
        deadman = bool(flags & 0x01)
        estop = bool(flags & 0x02)
        return ControllerSignal(
            linear=y, angular=x, deadman_pressed=deadman, emergency_pressed=estop
        )

    def encode(self, signal: ControllerSignal) -> Iterable[AdapterFrame]:
        if not signal.deadman_pressed:
            return self.safe_idle_frames()
        x = _to_s8(signal.angular * 128.0)
        y = _to_s8(signal.linear * 128.0)
        flags = 0x01 | (0x02 if signal.emergency_pressed else 0x00)
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=RNET_JOY_ID,
                data=bytes([x & 0xFF, y & 0xFF, flags, 0]),
            ),
        )

    def safe_idle_frames(self) -> Tuple[AdapterFrame, ...]:
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=RNET_JOY_ID,
                data=bytes([0, 0, 0, 0]),
            ),
        )


def _s8(b: int) -> int:
    return b - 256 if b > 127 else b


def _to_s8(x: float) -> int:
    return max(-128, min(127, int(round(x))))
