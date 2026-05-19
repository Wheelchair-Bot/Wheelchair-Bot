"""Integration tests for SafetyLoop (Phase 1 follow-up).

These tests exercise the wiring between every safety module via the
SafetyLoop facade. They are marked `safety` and run under the
dedicated CI gate.
"""

from __future__ import annotations

import math

import pytest

from wheelchair.safety import EStopReason, LVCState, SafetyLoop


@pytest.fixture
def loop() -> SafetyLoop:
    stops: list[None] = []
    gpio: list[None] = []
    sl = SafetyLoop(
        motor_stop=lambda: stops.append(None),
        hardware_gpio_drop=lambda: gpio.append(None),
        watchdog_timeout_s=0.1,
        deadman_timeout_s=0.5,
    )
    sl._motor_stops = stops  # type: ignore[attr-defined]
    sl._gpio_drops = gpio  # type: ignore[attr-defined]
    return sl


@pytest.mark.safety
def test_safety_loop_starts_engaged_because_no_feed_yet(loop: SafetyLoop) -> None:
    state = loop.step()
    assert state.engaged is True
    assert state.reason is EStopReason.WATCHDOG


@pytest.mark.safety
def test_fed_watchdog_and_pressed_deadman_runs_clean(loop: SafetyLoop) -> None:
    loop.feed_command()
    loop.deadman(True)
    loop.update_imu(0.0, 0.0, 9.81)
    loop.update_battery(24.5)
    loop.update_current(5.0, 5.0, 0.0)
    state = loop.step()
    assert state.engaged is False
    assert state.watchdog_alive is True
    assert state.deadman_alive is True
    assert state.tilt_tripped is False
    assert state.lvc_state is LVCState.NORMAL
    assert state.overcurrent_tripped is False


@pytest.mark.safety
def test_overcurrent_engages_estop_via_loop(loop: SafetyLoop) -> None:
    loop.feed_command()
    loop.deadman(True)
    loop.update_current(left_a=70.0, right_a=10.0, ts_s=0.0)
    state = loop.step()
    assert state.engaged is True
    assert state.reason is EStopReason.OVERCURRENT


@pytest.mark.safety
def test_tilt_engages_estop_via_loop(loop: SafetyLoop) -> None:
    import time as _t

    loop.feed_command()
    loop.deadman(True)
    ax = 9.81 * math.sin(math.radians(30))
    az = 9.81 * math.cos(math.radians(30))
    loop.update_imu(ax, 0.0, az)
    _t.sleep(0.3)
    loop.update_imu(ax, 0.0, az)
    state = loop.step()
    assert state.engaged is True
    assert state.reason is EStopReason.TILT


@pytest.mark.safety
def test_operator_estop_latches(loop: SafetyLoop) -> None:
    loop.feed_command()
    loop.deadman(True)
    loop.operator_estop("panic button")
    assert loop.step().engaged is True
    # Re-feeding doesn't clear; only explicit clear() with operator_confirm does.
    loop.feed_command()
    assert loop.step().engaged is True


@pytest.mark.safety
def test_clear_requires_operator_confirm(loop: SafetyLoop) -> None:
    loop.feed_command()
    loop.operator_estop()
    with pytest.raises(PermissionError):
        loop.clear()
    loop.clear(operator_confirm=True)
    loop.feed_command()
    loop.deadman(True)
    state = loop.step()
    assert state.engaged is False


@pytest.mark.safety
def test_lvc_propagates_to_loop_state(loop: SafetyLoop) -> None:
    loop.feed_command()
    loop.deadman(True)
    loop.update_battery(23.0)  # warn
    state = loop.step()
    assert state.engaged is False
    assert state.lvc_state is LVCState.WARNING
