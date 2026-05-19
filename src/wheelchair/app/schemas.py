"""WebSocket frame schemas (Pydantic v2).

These replace the loose TypedDicts in the abandoned `packages/shared`
package. All frames over the control channel MUST validate against
one of these. Anything else is rejected and the watchdog is NOT fed.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class FrameKind(str, Enum):
    MOVE = "move"
    STOP = "stop"
    DEADMAN = "deadman"
    PING = "ping"
    PONG = "pong"
    STATUS = "status"
    ERROR = "error"


class _Frame(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: FrameKind
    ts: float = Field(..., description="client monotonic seconds")
    seq: int = Field(..., ge=0)


class ControlFrame(_Frame):
    """Inbound from Android / Web."""

    # MOVE
    linear: float = Field(0.0, ge=-1.0, le=1.0)
    angular: float = Field(0.0, ge=-1.0, le=1.0)
    # DEADMAN
    pressed: bool = False


class StatusFrame(_Frame):
    """Outbound — wheelchair → client."""

    kind: FrameKind = FrameKind.STATUS
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0
    battery_v: float = 0.0
    battery_pct: float = 0.0
    estop_engaged: bool = False
    estop_reason: str | None = None


class ErrorFrame(_Frame):
    kind: FrameKind = FrameKind.ERROR
    code: str
    message: str
