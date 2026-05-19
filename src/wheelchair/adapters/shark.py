"""Shark / DX adapter skeleton (Dynamic Controls).

Bus: DCI (Dynamic Controls Interface) — proprietary 4-pin bus. Some
chairs expose CAN at 250 kbps. Same scaffolding shape as R-Net; real
codec lands with bench captures.
"""

from __future__ import annotations

from typing import Iterable, Tuple

from .base import AdapterFrame, CANAdapter, ControllerSignal


SHARK_JOY_ID = 0x18FF0000  # provisional


class SharkAdapter(CANAdapter):
    family = "shark"
    bitrate = 250_000

    def decode(self, frame: AdapterFrame) -> ControllerSignal | None:
        if frame.arbitration_id != SHARK_JOY_ID or len(frame.data) < 3:
            return None
        # Provisional: bytes 0..1 are unsigned 8-bit centred at 0x80.
        x = (frame.data[0] - 0x80) / 128.0
        y = (frame.data[1] - 0x80) / 128.0
        deadman = bool(frame.data[2] & 0x80)
        return ControllerSignal(linear=y, angular=x, deadman_pressed=deadman)

    def encode(self, signal: ControllerSignal) -> Iterable[AdapterFrame]:
        if not signal.deadman_pressed:
            return self.safe_idle_frames()
        x = max(0, min(255, int(0x80 + signal.angular * 128.0)))
        y = max(0, min(255, int(0x80 + signal.linear * 128.0)))
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=SHARK_JOY_ID,
                data=bytes([x, y, 0x80]),
            ),
        )

    def safe_idle_frames(self) -> Tuple[AdapterFrame, ...]:
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=SHARK_JOY_ID,
                data=bytes([0x80, 0x80, 0x00]),
            ),
        )
