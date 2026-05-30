"""Safety tests for the e-stop coordinator (audit gap G-04 software half)."""

from __future__ import annotations

import pytest

from wheelchair.safety import EmergencyStop, EStopReason


@pytest.mark.safety
def test_estop_engages_motor_stop_and_gpio() -> None:
    motors: list[None] = []
    gpio: list[None] = []
    es = EmergencyStop(
        motor_stop=lambda: motors.append(None),
        hardware_gpio_drop=lambda: gpio.append(None),
    )
    es.engage(EStopReason.OPERATOR, "panic button")
    assert es.is_engaged()
    assert motors == [None]
    assert gpio == [None]
    assert es.event is not None and es.event.reason is EStopReason.OPERATOR


@pytest.mark.safety
def test_estop_is_latched_until_cleared() -> None:
    motors: list[None] = []
    es = EmergencyStop(motor_stop=lambda: motors.append(None))
    es.engage(EStopReason.TILT)
    es.engage(EStopReason.WATCHDOG)
    es.engage(EStopReason.OVERCURRENT)
    assert motors == [None]  # only the first call ran
    assert es.event is not None and es.event.reason is EStopReason.TILT


@pytest.mark.safety
def test_estop_clear_requires_operator_confirm() -> None:
    es = EmergencyStop(motor_stop=lambda: None)
    es.engage(EStopReason.OPERATOR)
    with pytest.raises(PermissionError):
        es.clear()
    es.clear(operator_confirm=True)
    assert not es.is_engaged()


@pytest.mark.safety
def test_estop_listener_failure_does_not_block_stop() -> None:
    motors: list[None] = []
    es = EmergencyStop(
        motor_stop=lambda: motors.append(None),
        listeners=[lambda _e: (_ for _ in ()).throw(RuntimeError("bad listener"))],
    )
    es.engage(EStopReason.EXTERNAL)
    assert motors == [None]
    assert es.is_engaged()
