"""Safety tests for overcurrent monitor (audit gap G-02)."""

from __future__ import annotations

import pytest

from wheelchair.safety import MotorCurrent, OvercurrentMonitor


@pytest.mark.safety
def test_overcurrent_trip_above_peak() -> None:
    trips: list[None] = []
    ocm = OvercurrentMonitor(
        max_continuous_a=30.0,
        max_peak_a=60.0,
        stop_callback=lambda: trips.append(None),
    )
    ocm.update(MotorCurrent(left_a=70.0, right_a=10.0, timestamp_s=0.0))
    assert ocm.tripped is True
    assert trips == [None]


@pytest.mark.safety
def test_overcurrent_continuous_must_persist_to_trip() -> None:
    trips: list[None] = []
    ocm = OvercurrentMonitor(
        max_continuous_a=30.0,
        max_peak_a=60.0,
        peak_window_s=0.1,
        stop_callback=lambda: trips.append(None),
    )
    ocm.update(MotorCurrent(left_a=40.0, right_a=0.0, timestamp_s=0.0))
    assert trips == []
    ocm.update(MotorCurrent(left_a=40.0, right_a=0.0, timestamp_s=0.05))
    assert trips == []
    ocm.update(MotorCurrent(left_a=40.0, right_a=0.0, timestamp_s=0.11))
    assert trips == [None]


@pytest.mark.safety
def test_overcurrent_below_continuous_resets_window() -> None:
    ocm = OvercurrentMonitor(max_continuous_a=30.0, max_peak_a=60.0, peak_window_s=0.1)
    ocm.update(MotorCurrent(left_a=40.0, right_a=0.0, timestamp_s=0.0))
    ocm.update(MotorCurrent(left_a=5.0, right_a=5.0, timestamp_s=0.05))  # recovered
    ocm.update(MotorCurrent(left_a=40.0, right_a=0.0, timestamp_s=0.08))
    assert ocm.tripped is False


@pytest.mark.safety
def test_overcurrent_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        OvercurrentMonitor(max_continuous_a=50.0, max_peak_a=30.0)


@pytest.mark.safety
def test_overcurrent_uses_max_of_both_motors() -> None:
    ocm = OvercurrentMonitor(max_continuous_a=30.0, max_peak_a=60.0)
    ocm.update(MotorCurrent(left_a=10.0, right_a=80.0, timestamp_s=0.0))
    assert ocm.tripped is True
