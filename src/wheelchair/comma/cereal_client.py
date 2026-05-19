"""Thin abstraction over openpilot's cereal IPC.

We don't bundle cereal — it's pulled in on the comma device's image.
This module degrades to an in-process queue when cereal isn't
importable, so unit tests can pretend they're publishing/subscribing
without the comma stack present.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from typing import Any, Callable, Deque, Dict, Optional

from .topics import Topic

logger = logging.getLogger(__name__)


try:  # pragma: no cover - exercised on comma device only
    import cereal.messaging as messaging  # type: ignore[import-not-found]

    _HAS_CEREAL = True
except Exception:  # noqa: BLE001
    messaging = None  # type: ignore[assignment]
    _HAS_CEREAL = False


class _InProcessBus:
    """Fallback bus used when cereal isn't available.

    Tests that need to exercise pub/sub plumbing without the comma
    stack use this. Behaviour matches cereal's send/recv semantics
    closely enough for unit tests.
    """

    def __init__(self) -> None:
        self._queues: Dict[str, Deque[Any]] = defaultdict(lambda: deque(maxlen=128))
        self._listeners: Dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def publish(self, topic: str, payload: Any) -> None:
        self._queues[topic].append(payload)
        for cb in self._listeners[topic]:
            try:
                cb(payload)
            except Exception:  # noqa: BLE001
                logger.exception("listener for %s raised", topic)

    def recv(self, topic: str) -> Optional[Any]:
        q = self._queues[topic]
        return q.popleft() if q else None

    def subscribe(self, topic: str, cb: Callable[[Any], None]) -> None:
        self._listeners[topic].append(cb)


_FALLBACK = _InProcessBus()


def publish(topic: Topic, payload: Any) -> None:
    if _HAS_CEREAL:  # pragma: no cover
        pm = messaging.PubMaster([topic.value])
        msg = messaging.new_message(topic.value)
        setattr(msg, topic.value, payload)
        pm.send(topic.value, msg)
    else:
        _FALLBACK.publish(topic.value, payload)


def recv(topic: Topic) -> Optional[Any]:
    if _HAS_CEREAL:  # pragma: no cover
        sm = messaging.SubMaster([topic.value])
        sm.update(0)
        if sm.updated[topic.value]:
            return getattr(sm[topic.value], topic.value)
        return None
    return _FALLBACK.recv(topic.value)


def subscribe(topic: Topic, cb: Callable[[Any], None]) -> None:
    if _HAS_CEREAL:  # pragma: no cover - cereal does this via SubMaster polling
        raise RuntimeError("subscribe() is in-process only; on comma poll SubMaster directly")
    _FALLBACK.subscribe(topic.value, cb)


def cereal_present() -> bool:
    return _HAS_CEREAL
