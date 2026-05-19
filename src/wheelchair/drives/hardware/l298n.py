"""L298N H-bridge drive (audit gap G-15).

Wraps the legacy ``wheelchair_controller.MotorDriver`` in the canonical
``WheelchairDrive`` ABC. This is the bridge that lets the Phase 2
tele-op server, Phase 1 safety stack, and Phase 4 comma supervisor all
talk to the same H-bridge that ``main.py`` has been using all along —
without anyone having to import the deprecated package.

Once Phase 3 completes the consolidation, the legacy MotorDriver gets
inlined here and ``wheelchair_controller/`` is deleted.
"""

from __future__ import annotations

from typing import Tuple

from wheelchair.interfaces import WheelchairDrive


class L298NDrive(WheelchairDrive):
    """Differential drive over an L298N (or compatible) H-bridge."""

    def __init__(
        self,
        left_forward_pin: int = 17,
        left_backward_pin: int = 18,
        right_forward_pin: int = 22,
        right_backward_pin: int = 23,
        left_enable_pin: int = 12,
        right_enable_pin: int = 13,
        use_mock: bool = False,
    ) -> None:
        from wheelchair_controller.motor_driver import MotorDriver  # legacy bridge

        self._md = MotorDriver(
            left_forward_pin=left_forward_pin,
            left_backward_pin=left_backward_pin,
            right_forward_pin=right_forward_pin,
            right_backward_pin=right_backward_pin,
            left_enable_pin=left_enable_pin,
            right_enable_pin=right_enable_pin,
            use_mock=use_mock,
        )
        self._left = 0.0
        self._right = 0.0

    @property
    def motor_driver(self):
        """Legacy ``MotorDriver`` instance.

        Exposed so callers still using the legacy ``WheelchairController``
        API (e.g. main.py before its Phase-0 cleanup) can construct it
        from the canonical ``L298NDrive`` instead of importing
        ``MotorDriver`` directly. New code should drive through
        ``set_motor_speeds`` instead.
        """
        return self._md

    def set_motor_speeds(self, left: float, right: float) -> None:
        self._left = max(-1.0, min(1.0, left))
        self._right = max(-1.0, min(1.0, right))
        # MotorDriver takes percent -100..100.
        self._md.set_motor_speed(int(self._left * 100), int(self._right * 100))

    def get_motor_speeds(self) -> Tuple[float, float]:
        return self._left, self._right

    def emergency_stop(self) -> None:
        self._left = self._right = 0.0
        self._md.stop()

    def update(self, dt: float) -> None:
        # L298N is stateless from our POV; nothing to integrate here.
        pass

    def cleanup(self) -> None:
        self._md.cleanup()
