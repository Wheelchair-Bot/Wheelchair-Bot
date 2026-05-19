"""Integration tests for the tele-op FastAPI server (G-07, G-14)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from wheelchair.app.auth import TokenStore, new_token  # noqa: E402
from wheelchair.app.schemas import StatusFrame  # noqa: E402
from wheelchair.app.server import create_app  # noqa: E402


class FakeDrive:
    def __init__(self) -> None:
        self.last_speeds: tuple[float, float] | None = None

    def set_motor_speeds(self, left: float, right: float) -> None:
        self.last_speeds = (left, right)


def _build(token: str | None = None):
    drive = FakeDrive()
    stops: list[str] = []
    feeds: list[None] = []
    store = TokenStore()
    if token is None:
        token = new_token()
    store.add(token)
    app = create_app(
        drive=drive,
        safety_stop=lambda reason: stops.append(reason),
        feed_watchdog=lambda: feeds.append(None),
        token_store=store,
        status_provider=lambda: StatusFrame(ts=0.0, seq=0),
    )
    return app, drive, stops, feeds, token


def test_health_endpoint_is_unauthenticated() -> None:
    app, *_ = _build()
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


def test_legacy_http_move_returns_410() -> None:
    app, *_ = _build()
    with TestClient(app) as client:
        r = client.post("/api/move")
        assert r.status_code == 410


def test_ws_rejects_unauthenticated() -> None:
    app, *_ = _build()
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/control"):
                pass


def test_ws_accepts_authenticated_and_handles_move() -> None:
    app, drive, stops, feeds, token = _build()
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json(
                {
                    "kind": "move",
                    "ts": 0.0,
                    "seq": 1,
                    "linear": 0.4,
                    "angular": 0.2,
                }
            )
            ws.receive_json()  # status echo
    assert drive.last_speeds == (pytest.approx(0.2), pytest.approx(0.6))
    assert feeds  # watchdog was fed


def test_ws_disconnect_releases_deadman() -> None:
    app, drive, stops, feeds, token = _build()
    with TestClient(app) as client:
        with client.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "ping", "ts": 0.0, "seq": 1})
            ws.receive_json()
    assert "ws_exit" in stops or "ws_disconnect" in stops
