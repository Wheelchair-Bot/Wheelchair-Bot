"""Tele-op application layer (Phase 2).

The single canonical home for FastAPI + WebSocket + WebRTC signaling.
Replaces the stub `packages/backend/wheelchair_bot/main.py`.

Issues closed by this package's PRs:
- #25 G-07 backend WebSocket route
- #26 G-08 WebRTC signaling server
- #32 G-14 packages/backend stub
- #41 G-23 auth + TLS
"""

from .schemas import ControlFrame, FrameKind, StatusFrame

__all__ = ["ControlFrame", "FrameKind", "StatusFrame"]
