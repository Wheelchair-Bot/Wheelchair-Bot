"""WheelchairDrive backed by a comma panda CAN bridge.

This is the production hardware target for Phase 4+. It takes a
``CANAdapter`` (R-Net / Shark / VR2 / LiNX / Q-Logic) and routes
encode()-d frames through ``PandaBridge``. The panda's safety mode
acts as an independent enforcement layer: even if Linux misbehaves,
the panda refuses to send unless it heartbeats.
"""

from __future__ import annotations

from typing import Tuple

from wheelchair.adapters.base import CANAdapter, ControllerSignal
from wheelchair.comma.panda import PandaBridge
from wheelchair.interfaces import WheelchairDrive


class CommaPandaDrive(WheelchairDrive):
    def __init__(self, adapter: CANAdapter, bridge: PandaBridge, bus: int = 0) -> None:
        self.adapter = adapter
        self.bridge = bridge
        self.bus = bus
        self._left = 0.0
        self._right = 0.0
        self._deadman = False

    def attach_deadman(self, pressed: bool) -> None:
        self._deadman = pressed

    def set_motor_speeds(self, left: float, right: float) -> None:
        self._left = max(-1.0, min(1.0, left))
        self._right = max(-1.0, min(1.0, right))
        # Diff-drive inverse: linear = (l+r)/2; angular = (r-l)/2
        linear = 0.5 * (self._left + self._right)
        angular = 0.5 * (self._right - self._left)
        signal = ControllerSignal(
            linear=linear, angular=angular, deadman_pressed=self._deadman
        )
        for frame in self.adapter.encode(signal):
            self.bridge.send(frame.arbitration_id, frame.data, bus=self.bus)

    def get_motor_speeds(self) -> Tuple[float, float]:
        return self._left, self._right

    def emergency_stop(self) -> None:
        self._left = self._right = 0.0
        self._deadman = False
        for frame in self.adapter.safe_idle_frames():
            try:
                self.bridge.send(frame.arbitration_id, frame.data, bus=self.bus)
            except PermissionError:
                # If panda is gating, that's fine — output is already off.
                pass
        self.bridge.disable_output()

    def update(self, dt: float) -> None:
        # Heartbeat the panda so its watchdog doesn't engage.
        self.bridge.heartbeat()
