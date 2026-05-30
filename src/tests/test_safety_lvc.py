"""Safety tests for low-voltage cutoff (audit gap G-06)."""

from __future__ import annotations

import pytest

from wheelchair.safety import LowVoltageCutoff, LVCState


class FakeClock:
    def __init__(self, t: float = 0.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.mark.safety
def test_lvc_normal_at_full_charge() -> None:
    lvc = LowVoltageCutoff(clock=FakeClock())
    assert lvc.update(24.8) is LVCState.NORMAL


@pytest.mark.safety
def test_lvc_warns_between_thresholds() -> None:
    lvc = LowVoltageCutoff(clock=FakeClock())
    assert lvc.update(23.0) is LVCState.WARNING


@pytest.mark.safety
def test_lvc_cuts_at_22_5V_for_24V_pack() -> None:
    """G-06 contract: 22.5 V sustained = cutoff."""
    stops: list[None] = []
    clk = FakeClock()
    lvc = LowVoltageCutoff(
        cutoff_v=22.5,
        debounce_s=1.0,
        stop_callback=lambda: stops.append(None),
        clock=clk,
    )
    lvc.update(22.0)
    assert lvc.state is LVCState.WARNING  # not debounced yet
    clk.advance(1.1)
    lvc.update(22.0)
    assert lvc.state is LVCState.CUTOFF
    assert stops == [None]


@pytest.mark.safety
def test_lvc_debounces_regen_spikes() -> None:
    """A momentary dip should not cut."""
    clk = FakeClock()
    lvc = LowVoltageCutoff(cutoff_v=22.5, debounce_s=1.0, clock=clk)
    lvc.update(22.0)
    clk.advance(0.5)
    lvc.update(24.0)  # recovered
    clk.advance(2.0)
    assert lvc.update(24.0) is LVCState.NORMAL


@pytest.mark.safety
def test_lvc_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        LowVoltageCutoff(cutoff_v=24.0, warn_v=23.0)
