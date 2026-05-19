"""Safety tests for the tilt monitor (audit gap G-05)."""

from __future__ import annotations

import math

import pytest

from wheelchair.safety import TiltMonitor


class FakeClock:
    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.mark.safety
def test_tilt_level_does_not_trip() -> None:
    tm = TiltMonitor(limit_deg=25.0, debounce_s=0.2, clock=FakeClock())
    assert tm.update(0.0, 0.0, 9.81) is False


@pytest.mark.safety
def test_tilt_cutoff_at_25_deg_sustains_under_vibration() -> None:
    """G-05 contract: trip at 25° held for debounce window."""
    trips: list[None] = []
    clk = FakeClock()
    tm = TiltMonitor(
        limit_deg=25.0,
        debounce_s=0.2,
        stop_callback=lambda: trips.append(None),
        clock=clk,
    )
    # 30° tilt = some lateral + some vertical
    ax = 9.81 * math.sin(math.radians(30))
    az = 9.81 * math.cos(math.radians(30))
    tm.update(ax, 0.0, az)
    clk.advance(0.1)
    tm.update(ax, 0.0, az)
    assert trips == []  # not debounced yet
    clk.advance(0.15)
    tm.update(ax, 0.0, az)
    assert len(trips) == 1
    assert tm.tripped


@pytest.mark.safety
def test_tilt_below_limit_resets_debounce() -> None:
    clk = FakeClock()
    tm = TiltMonitor(limit_deg=25.0, debounce_s=0.2, clock=clk)
    ax_high = 9.81 * math.sin(math.radians(30))
    az_high = 9.81 * math.cos(math.radians(30))
    tm.update(ax_high, 0.0, az_high)
    clk.advance(0.1)
    tm.update(0.0, 0.0, 9.81)  # leveled out
    clk.advance(0.2)
    tm.update(ax_high, 0.0, az_high)
    clk.advance(0.1)
    assert tm.update(ax_high, 0.0, az_high) is False


@pytest.mark.safety
def test_tilt_handles_zero_accel_gracefully() -> None:
    tm = TiltMonitor(clock=FakeClock())
    assert tm.update(0.0, 0.0, 0.0) is False
