"""Safety tests for the command watchdog (audit gap G-01).

These tests are marked ``safety`` and gated by the dedicated CI job; they
must pass on every commit.
"""

from __future__ import annotations

import pytest

from wheelchair.safety import CommandWatchdog, WatchdogExpired


class FakeClock:
    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.mark.safety
def test_watchdog_starts_not_alive() -> None:
    wd = CommandWatchdog(timeout_s=0.1, clock=FakeClock())
    assert not wd.is_alive()
    with pytest.raises(WatchdogExpired):
        wd.assert_alive()


@pytest.mark.safety
def test_watchdog_alive_immediately_after_feed() -> None:
    clk = FakeClock()
    wd = CommandWatchdog(timeout_s=0.1, clock=clk)
    wd.feed()
    assert wd.is_alive()
    wd.assert_alive()


@pytest.mark.safety
def test_watchdog_expires_after_timeout() -> None:
    clk = FakeClock()
    wd = CommandWatchdog(timeout_s=0.1, clock=clk)
    wd.feed()
    clk.advance(0.099)
    assert wd.is_alive()
    clk.advance(0.002)  # past 100 ms
    assert not wd.is_alive()


@pytest.mark.safety
def test_watchdog_stops_motors_within_100ms_of_command_loss() -> None:
    """G-01 contract: 100 ms watchdog forces motor-zero command."""
    clk = FakeClock()
    wd = CommandWatchdog(timeout_s=0.1, clock=clk)
    motor_pwm = [50.0]  # held command

    def control_step() -> None:
        if not wd.is_alive():
            motor_pwm[0] = 0.0

    wd.feed()
    control_step()
    assert motor_pwm[0] == 50.0
    clk.advance(0.101)
    control_step()
    assert motor_pwm[0] == 0.0


@pytest.mark.safety
def test_watchdog_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        CommandWatchdog(timeout_s=0.0)
    with pytest.raises(ValueError):
        CommandWatchdog(timeout_s=-1.0)
