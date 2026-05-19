"""Safety tests for the deadman switch (audit gap G-03)."""

from __future__ import annotations

import pytest

from wheelchair.safety import DeadmanSwitch


class FakeClock:
    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.mark.safety
def test_deadman_fires_stop_callback_on_construction_until_pressed() -> None:
    stops: list[None] = []
    dms = DeadmanSwitch(
        timeout_s=0.1, stop_callback=lambda: stops.append(None), clock=FakeClock()
    )
    assert dms.check() is False
    assert stops == [None]


@pytest.mark.safety
def test_deadman_stop_is_idempotent_per_expiry() -> None:
    stops: list[None] = []
    clk = FakeClock()
    dms = DeadmanSwitch(
        timeout_s=0.1, stop_callback=lambda: stops.append(None), clock=clk
    )
    dms.check()
    dms.check()
    dms.check()
    assert len(stops) == 1  # one stop per expiry, not one per tick


@pytest.mark.safety
def test_deadman_held_does_not_stop() -> None:
    stops: list[None] = []
    clk = FakeClock()
    dms = DeadmanSwitch(
        timeout_s=0.1, stop_callback=lambda: stops.append(None), clock=clk
    )
    dms.press()
    clk.advance(0.05)
    assert dms.check() is True
    assert stops == []


@pytest.mark.safety
def test_deadman_release_drives_pwm_to_zero_at_gpio_level() -> None:
    """G-03 contract: release fires the stop callback synchronously."""
    pwm = [50.0]
    clk = FakeClock()
    dms = DeadmanSwitch(
        timeout_s=0.1, stop_callback=lambda: pwm.__setitem__(0, 0.0), clock=clk
    )
    dms.press()
    assert pwm[0] == 50.0
    dms.release()
    # Synchronous: pwm is already zero before any next loop iteration.
    assert pwm[0] == 0.0


@pytest.mark.safety
def test_deadman_timeout_stops_in_same_call_that_observes_expiry() -> None:
    pwm = [50.0]
    clk = FakeClock()
    dms = DeadmanSwitch(
        timeout_s=0.1, stop_callback=lambda: pwm.__setitem__(0, 0.0), clock=clk
    )
    dms.press()
    clk.advance(0.101)
    assert dms.check() is False
    assert pwm[0] == 0.0  # GPIO went low in the check() call


@pytest.mark.safety
def test_deadman_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        DeadmanSwitch(timeout_s=0, stop_callback=lambda: None)
