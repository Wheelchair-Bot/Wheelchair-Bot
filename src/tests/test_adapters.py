"""Unit tests for the controller-family adapter skeletons.

These exercise the codec **shape**, not the (provisional) byte layouts.
Real-protocol regression tests land in Phase 3 once captures from a
Permobil M3 / Quantum Q6 / Pride Jazzy are committed to
``tests/captures/`` (gitignored binary fixtures, replay CSVs go in
``tests/captures/*.csv``).
"""

from __future__ import annotations

import pytest

from wheelchair.adapters import (
    CANAdapter,
    ControllerSignal,
    RNetAdapter,
    SharkAdapter,
    VR2Adapter,
)


ADAPTERS = [RNetAdapter(), SharkAdapter(), VR2Adapter()]


@pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.family)
def test_adapter_round_trips_centre(adapter: CANAdapter) -> None:
    sig_in = ControllerSignal(linear=0.0, angular=0.0, deadman_pressed=True)
    frames = list(adapter.encode(sig_in))
    assert frames, f"{adapter.family} produced no frames"
    sig_out = adapter.decode(frames[0])
    assert sig_out is not None
    assert abs(sig_out.linear) < 0.02
    assert abs(sig_out.angular) < 0.02


@pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.family)
def test_adapter_safe_idle_decodes_to_zero(adapter: CANAdapter) -> None:
    for frame in adapter.safe_idle_frames():
        sig = adapter.decode(frame)
        if sig is None:
            continue
        assert abs(sig.linear) < 0.02
        assert abs(sig.angular) < 0.02


@pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.family)
def test_adapter_releases_deadman_emits_safe(adapter: CANAdapter) -> None:
    sig = ControllerSignal(linear=0.5, angular=0.5, deadman_pressed=False)
    out = list(adapter.encode(sig))
    decoded = adapter.decode(out[0]) if out else None
    if decoded is not None:
        assert abs(decoded.linear) < 0.02
        assert abs(decoded.angular) < 0.02
