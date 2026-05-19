"""WebRTC signaling server (G-08).

Thin SDP / ICE relay over WebSocket. Sits alongside the control WS
endpoint in the same FastAPI app so there's one port, one auth model.

Phase 2 ships the signaling only; the actual video pipeline
(libcamera → GStreamer → aiortc track) lands as a follow-up because
it needs a Pi camera on the bench.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SignalingRoom:
    """A tiny in-memory room.

    Each paired device is its own room; the Pi is always the offerer.
    """

    pending_offers: List[dict] = field(default_factory=list)
    pending_answers: List[dict] = field(default_factory=list)
    pending_candidates: List[dict] = field(default_factory=list)

    def post_offer(self, sdp: dict) -> None:
        self.pending_offers.append(sdp)

    def post_answer(self, sdp: dict) -> None:
        self.pending_answers.append(sdp)

    def post_candidate(self, c: dict) -> None:
        self.pending_candidates.append(c)

    def drain(self, key: str) -> list:
        bucket = {
            "offers": self.pending_offers,
            "answers": self.pending_answers,
            "candidates": self.pending_candidates,
        }[key]
        out = list(bucket)
        bucket.clear()
        return out


@dataclass
class SignalingRegistry:
    rooms: Dict[str, SignalingRoom] = field(default_factory=dict)

    def room(self, device_id: str) -> SignalingRoom:
        return self.rooms.setdefault(device_id, SignalingRoom())
