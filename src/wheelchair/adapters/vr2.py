"""VR2 / Pilot+ adapter skeleton (PG Drives)."""

from __future__ import annotations

from typing import Iterable, Tuple

from .base import AdapterFrame, CANAdapter, ControllerSignal


VR2_JOY_ID = 0x0CFF1000  # provisional


class VR2Adapter(CANAdapter):
    family = "vr2"
    bitrate = 125_000

    def decode(self, frame: AdapterFrame) -> ControllerSignal | None:
        if frame.arbitration_id != VR2_JOY_ID or len(frame.data) < 4:
            return None
        # Provisional: 16-bit little-endian signed for X, Y.
        x = int.from_bytes(frame.data[0:2], "little", signed=True) / 32768.0
        y = int.from_bytes(frame.data[2:4], "little", signed=True) / 32768.0
        return ControllerSignal(linear=y, angular=x, deadman_pressed=True)

    def encode(self, signal: ControllerSignal) -> Iterable[AdapterFrame]:
        x = max(-32768, min(32767, int(signal.angular * 32768.0)))
        y = max(-32768, min(32767, int(signal.linear * 32768.0)))
        if not signal.deadman_pressed:
            x = y = 0
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=VR2_JOY_ID,
                data=x.to_bytes(2, "little", signed=True)
                + y.to_bytes(2, "little", signed=True),
            ),
        )

    def safe_idle_frames(self) -> Tuple[AdapterFrame, ...]:
        return (
            AdapterFrame(
                timestamp_s=0.0,
                arbitration_id=VR2_JOY_ID,
                data=b"\x00\x00\x00\x00",
            ),
        )
