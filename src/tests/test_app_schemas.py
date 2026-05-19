"""Schema validation tests for tele-op frames (G-07)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wheelchair.app import ControlFrame, FrameKind


def test_move_frame_round_trips() -> None:
    f = ControlFrame(kind=FrameKind.MOVE, ts=1.0, seq=1, linear=0.5, angular=-0.2)
    assert f.linear == 0.5
    assert f.angular == -0.2


def test_move_frame_clamps_via_validation() -> None:
    with pytest.raises(ValidationError):
        ControlFrame(kind=FrameKind.MOVE, ts=1.0, seq=1, linear=2.0)
    with pytest.raises(ValidationError):
        ControlFrame(kind=FrameKind.MOVE, ts=1.0, seq=1, angular=-2.0)


def test_extra_fields_rejected() -> None:
    """A misbehaving client cannot smuggle extra fields into a control frame."""
    with pytest.raises(ValidationError):
        ControlFrame.model_validate(
            {"kind": "move", "ts": 0.0, "seq": 0, "linear": 0.0, "angular": 0.0, "raw_pwm": 999}
        )


def test_negative_seq_rejected() -> None:
    with pytest.raises(ValidationError):
        ControlFrame(kind=FrameKind.STOP, ts=0.0, seq=-1)
