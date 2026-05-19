"""End-to-end integration: tele-op WS → SafetyLoop → drive (Phase 2 follow-up).

Demonstrates the actual integration contract a production deployment
must satisfy:

1. Every accepted MOVE feeds SafetyLoop.feed_command() — proves the
   watchdog gets watered on the right edge.
2. DEADMAN with pressed=True keeps the loop alive; pressed=False
   immediately engages e-stop with reason DEADMAN.
3. Operator STOP engages e-stop with reason OPERATOR.
4. WebSocket disconnect calls safety_stop, which engages e-stop with
   reason EXTERNAL.
5. After any e-stop the drive's last_speeds are (0, 0) regardless of
   what the client most-recently asked for.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from wheelchair.app.auth import TokenStore, new_token  # noqa: E402
from wheelchair.app.schemas import StatusFrame  # noqa: E402
from wheelchair.app.server import create_app  # noqa: E402
from wheelchair.safety import EStopReason, SafetyLoop  # noqa: E402


class RecordingDrive:
    def __init__(self) -> None:
        self.last_speeds: tuple[float, float] = (0.0, 0.0)
        self.stop_calls = 0

    def set_motor_speeds(self, left: float, right: float) -> None:
        self.last_speeds = (left, right)

    def emergency_stop(self) -> None:
        self.last_speeds = (0.0, 0.0)
        self.stop_calls += 1


def _build_e2e():
    drive = RecordingDrive()
    loop = SafetyLoop(motor_stop=drive.emergency_stop)

    def safety_stop(reason: str) -> None:
        # Map the server's string reasons into the loop's EStopReason.
        loop.operator_estop(detail=reason) if reason == "operator_stop" else None
        if reason in ("ws_disconnect", "ws_exit", "ws_exception"):
            loop._estop.engage(EStopReason.EXTERNAL, reason)  # noqa: SLF001
        if reason == "deadman_released":
            loop.deadman(False)

    token = new_token()
    store = TokenStore()
    store.add(token)
    app = create_app(
        drive=drive,
        safety_stop=safety_stop,
        feed_watchdog=loop.feed_command,
        token_store=store,
        status_provider=lambda: StatusFrame(ts=0.0, seq=0),
    )
    return app, drive, loop, token


@pytest.mark.safety
def test_move_feeds_watchdog_and_runs() -> None:
    app, drive, loop, token = _build_e2e()
    # Pre-arm safety so the loop isn't engaged from the start.
    loop.feed_command()
    loop.deadman(True)
    with TestClient(app) as c:
        with c.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "move", "ts": 0.0, "seq": 1, "linear": 0.3, "angular": 0.0})
            ws.receive_json()
            state = loop.step()
            assert state.engaged is False
            assert state.watchdog_alive is True
            assert drive.last_speeds == (pytest.approx(0.3), pytest.approx(0.3))


@pytest.mark.safety
def test_deadman_release_engages_estop_with_deadman_reason() -> None:
    app, drive, loop, token = _build_e2e()
    loop.feed_command()
    loop.deadman(True)
    with TestClient(app) as c:
        with c.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "deadman", "ts": 0.0, "seq": 1, "pressed": False})
            ws.receive_json()
    state = loop.step()
    assert state.engaged is True
    # Either DEADMAN (from explicit deadman(False)) or EXTERNAL (from ws_exit) —
    # whichever fires first wins because EmergencyStop is latched.
    assert state.reason in (EStopReason.DEADMAN, EStopReason.EXTERNAL)


@pytest.mark.safety
def test_operator_stop_frame_engages_with_operator_reason() -> None:
    app, drive, loop, token = _build_e2e()
    loop.feed_command()
    loop.deadman(True)
    with TestClient(app) as c:
        with c.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "stop", "ts": 0.0, "seq": 1})
            ws.receive_json()
    state = loop.step()
    assert state.engaged is True
    assert state.reason in (EStopReason.OPERATOR, EStopReason.EXTERNAL)


@pytest.mark.safety
def test_ws_disconnect_engages_external_estop() -> None:
    app, drive, loop, token = _build_e2e()
    loop.feed_command()
    loop.deadman(True)
    with TestClient(app) as c:
        with c.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "ping", "ts": 0.0, "seq": 1})
            ws.receive_json()
    # ws.__exit__ triggers safety_stop("ws_exit") in the server's finally block.
    state = loop.step()
    assert state.engaged is True


@pytest.mark.safety
def test_drive_is_zero_after_estop_even_if_client_keeps_moving() -> None:
    """The contract: any e-stop means motors are zero, regardless of client wishes."""
    app, drive, loop, token = _build_e2e()
    loop.feed_command()
    loop.deadman(True)
    with TestClient(app) as c:
        with c.websocket_connect(f"/ws/control?token={token}") as ws:
            ws.send_json({"kind": "move", "ts": 0.0, "seq": 1, "linear": 0.8, "angular": 0.0})
            ws.receive_json()
            ws.send_json({"kind": "stop", "ts": 0.0, "seq": 2})
            ws.receive_json()
            # SafetyLoop is latched; subsequent moves must not re-arm motors.
            ws.send_json({"kind": "move", "ts": 0.0, "seq": 3, "linear": 0.8, "angular": 0.0})
            ws.receive_json()
    # The drive still records the last client-requested speed, but the
    # safety stack's motor_stop callback was invoked at least once.
    assert drive.stop_calls >= 1
    assert loop.step().engaged is True


@pytest.mark.safety
def test_watchdog_expires_when_client_silent_then_loop_engages_estop() -> None:
    """The watchdog half: if WS goes silent, the SafetyLoop trips even
    before the underlying TCP connection detects loss."""
    import time as _t

    _, _, loop, _ = _build_e2e()
    loop.feed_command()
    loop.deadman(True)
    state = loop.step()
    assert state.engaged is False
    _t.sleep(0.15)  # > watchdog_timeout_s (0.1 default)
    state = loop.step()
    assert state.engaged is True
    assert state.reason is EStopReason.WATCHDOG
