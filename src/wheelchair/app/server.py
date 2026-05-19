"""FastAPI tele-op server.

Replaces the stub in ``packages/backend/wheelchair_bot/main.py``
(audit gaps G-07, G-14). Every accepted control frame feeds the
command watchdog; loss of WS connection releases the deadman.

The drive backend is injected so this server runs against either the
emulator (CI, dev) or the L298N hardware wrapper (Phase 3) or the
comma+panda bridge (Phase 4).

FastAPI is a required dependency of this module.
"""

import logging
from typing import Any, Callable, Optional

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from .auth import TokenStore
from .schemas import ControlFrame, ErrorFrame, FrameKind, StatusFrame

logger = logging.getLogger(__name__)


def create_app(
    drive: Any,
    safety_stop: Callable[[str], None],
    feed_watchdog: Callable[[], None],
    token_store: TokenStore,
    status_provider: Callable[[], StatusFrame],
) -> FastAPI:
    app = FastAPI(title="wheelchair-bot tele-op", version="0.2.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/status")
    def api_status() -> dict:
        return status_provider().model_dump()

    @app.websocket("/ws/control")
    async def ws_control(
        websocket: WebSocket, token: Optional[str] = Query(default=None)
    ) -> None:
        auth_header = websocket.headers.get("authorization", "")
        bearer = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else None
        candidate = bearer or token
        if not token_store.verify(candidate):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        try:
            while True:
                raw = await websocket.receive_json()
                try:
                    frame = ControlFrame.model_validate(raw)
                except Exception as exc:  # noqa: BLE001
                    err = ErrorFrame(ts=0.0, seq=0, code="bad_frame", message=str(exc))
                    await websocket.send_json(err.model_dump())
                    continue
                _handle_frame(frame, drive, safety_stop, feed_watchdog)
                await websocket.send_json(status_provider().model_dump())
        except WebSocketDisconnect:
            pass
        except Exception:  # noqa: BLE001
            logger.exception("ws_control crashed")
        finally:
            safety_stop("ws_exit")

    @app.post("/api/move")
    def http_move() -> None:
        # Deprecated in favour of WS — kept here so callers get a 410
        # rather than a 404 during the transition window.
        raise HTTPException(status_code=410, detail="use ws://.../ws/control")

    return app


def _handle_frame(
    frame: ControlFrame,
    drive: Any,
    safety_stop: Callable[[str], None],
    feed_watchdog: Callable[[], None],
) -> None:
    if frame.kind is FrameKind.MOVE:
        drive.set_motor_speeds(_diff_drive_left(frame), _diff_drive_right(frame))
        feed_watchdog()
    elif frame.kind is FrameKind.DEADMAN:
        if frame.pressed:
            feed_watchdog()
        else:
            safety_stop("deadman_released")
    elif frame.kind is FrameKind.STOP:
        safety_stop("operator_stop")
    elif frame.kind is FrameKind.PING:
        feed_watchdog()


def _diff_drive_left(f: ControlFrame) -> float:
    return max(-1.0, min(1.0, f.linear - f.angular))


def _diff_drive_right(f: ControlFrame) -> float:
    return max(-1.0, min(1.0, f.linear + f.angular))
