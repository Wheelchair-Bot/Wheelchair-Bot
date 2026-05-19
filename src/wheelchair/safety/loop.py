"""SafetyLoop — single integration point for every Phase-1 safety module.

Callers (tele-op server, comma supervisor, HIL rig) shouldn't have to
re-implement the wiring of CommandWatchdog + DeadmanSwitch + TiltMonitor
+ LowVoltageCutoff + OvercurrentMonitor + EmergencyStop. This module
does it once.

Design:
- Every monitor is created with a `stop_callback` that fans into the
  shared `EmergencyStop` coordinator with the matching `EStopReason`.
- The control loop calls `step(...)` on every iteration with the
  latest sensor + battery + current snapshot. `step()` is non-blocking
  and returns the current `SafetyState`.
- If `state.engaged` is True the caller MUST command motors to zero
  (and the drive's hardware-level `EmergencyStop.hardware_gpio_drop`
  already pulled the GPIO line low independently).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .current_limit import MotorCurrent, OvercurrentMonitor
from .deadman import DeadmanSwitch
from .estop import EmergencyStop, EStopReason
from .lvc import LowVoltageCutoff, LVCState
from .tilt import TiltMonitor
from .watchdog import CommandWatchdog


@dataclass
class SafetyState:
    """Snapshot returned from `SafetyLoop.step()`."""

    engaged: bool
    reason: Optional[EStopReason]
    watchdog_alive: bool
    deadman_alive: bool
    tilt_tripped: bool
    lvc_state: LVCState
    overcurrent_tripped: bool


@dataclass
class SafetyLoop:
    """Aggregator for every Phase-1 safety subsystem.

    Args:
        motor_stop: invoked once by EmergencyStop on first trip.
        hardware_gpio_drop: invoked once on first trip; production
            wiring pulls the e-stop relay's enable line low.
        watchdog_timeout_s: max gap between feed() calls (default 100 ms).
        deadman_timeout_s: max gap between press() calls (default 500 ms).
        tilt_limit_deg / tilt_debounce_s: TiltMonitor parameters.
        lvc_*: LowVoltageCutoff parameters.
        oc_max_continuous_a / oc_max_peak_a / oc_peak_window_s:
            OvercurrentMonitor parameters (per chair from WheelchairSpec.motor).
    """

    motor_stop: Callable[[], None]
    hardware_gpio_drop: Callable[[], None] = lambda: None  # noqa: E731
    watchdog_timeout_s: float = 0.1
    deadman_timeout_s: float = 0.5
    tilt_limit_deg: float = 25.0
    tilt_debounce_s: float = 0.2
    lvc_warn_v: float = 23.5
    lvc_cutoff_v: float = 22.5
    lvc_debounce_s: float = 1.0
    oc_max_continuous_a: float = 30.0
    oc_max_peak_a: float = 50.0
    oc_peak_window_s: float = 0.1
    _estop: EmergencyStop = field(init=False)
    _watchdog: CommandWatchdog = field(init=False)
    _deadman: DeadmanSwitch = field(init=False)
    _tilt: TiltMonitor = field(init=False)
    _lvc: LowVoltageCutoff = field(init=False)
    _ocm: OvercurrentMonitor = field(init=False)

    def __post_init__(self) -> None:
        self._estop = EmergencyStop(
            motor_stop=self.motor_stop,
            hardware_gpio_drop=self.hardware_gpio_drop,
        )
        self._watchdog = CommandWatchdog(timeout_s=self.watchdog_timeout_s)
        self._deadman = DeadmanSwitch(
            timeout_s=self.deadman_timeout_s,
            stop_callback=lambda: self._estop.engage(EStopReason.DEADMAN),
        )
        self._tilt = TiltMonitor(
            limit_deg=self.tilt_limit_deg,
            debounce_s=self.tilt_debounce_s,
            stop_callback=lambda: self._estop.engage(EStopReason.TILT),
        )
        self._lvc = LowVoltageCutoff(
            warn_v=self.lvc_warn_v,
            cutoff_v=self.lvc_cutoff_v,
            debounce_s=self.lvc_debounce_s,
            stop_callback=lambda: self._estop.engage(EStopReason.LVC),
        )
        self._ocm = OvercurrentMonitor(
            max_continuous_a=self.oc_max_continuous_a,
            max_peak_a=self.oc_max_peak_a,
            peak_window_s=self.oc_peak_window_s,
            stop_callback=lambda: self._estop.engage(EStopReason.OVERCURRENT),
        )

    # ---- inputs ----

    def feed_command(self) -> None:
        """Call on every valid command from the tele-op server."""
        self._watchdog.feed()

    def deadman(self, pressed: bool) -> None:
        if pressed:
            self._deadman.press()
        else:
            self._deadman.release()

    def update_imu(self, ax: float, ay: float, az: float) -> None:
        self._tilt.update(ax, ay, az)

    def update_battery(self, voltage_v: float) -> None:
        self._lvc.update(voltage_v)

    def update_current(self, left_a: float, right_a: float, ts_s: float) -> None:
        self._ocm.update(MotorCurrent(left_a=left_a, right_a=right_a, timestamp_s=ts_s))

    def operator_estop(self, detail: str = "") -> None:
        self._estop.engage(EStopReason.OPERATOR, detail)

    # ---- per-tick step ----

    def step(self) -> SafetyState:
        """Run all checks and return the current state."""
        # The watchdog isn't a callback-style monitor; check it here.
        if not self._watchdog.is_alive():
            self._estop.engage(EStopReason.WATCHDOG)
        self._deadman.check()  # fires stop on expiry
        return SafetyState(
            engaged=self._estop.is_engaged(),
            reason=self._estop.event.reason if self._estop.event else None,
            watchdog_alive=self._watchdog.is_alive(),
            deadman_alive=not self._deadman.stopped,
            tilt_tripped=self._tilt.tripped,
            lvc_state=self._lvc.state,
            overcurrent_tripped=self._ocm.tripped,
        )

    # ---- ops ----

    def clear(self, operator_confirm: bool = False) -> None:
        """Release the latched e-stop. Requires explicit confirmation."""
        self._estop.clear(operator_confirm=operator_confirm)
        # Reset stateful monitors so the next step() doesn't immediately retrip.
        self._tilt.reset()

    @property
    def estop(self) -> EmergencyStop:
        return self._estop
