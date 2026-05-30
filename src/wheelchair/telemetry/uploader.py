"""Buffered telemetry uploader.

In-process producer/consumer queue with bounded depth (lossy). Real
backend (S3 multipart upload + KMS) lands once the beta participant
agreements are signed and the receiving infra is in place.
"""

from __future__ import annotations

import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Iterable


@dataclass
class Event:
    timestamp_s: float
    kind: str  # e.g. "estop", "wd_expiry", "session_start"
    payload: dict = field(default_factory=dict)


@dataclass
class TelemetryUploader:
    """Buffered uploader. Drops oldest on overflow.

    Args:
        sink: pluggable callable that consumes a batch. In Phase 5
            production this is an S3 multipart upload; in tests it's
            a list.append.
        max_buffer: deque maxlen — drops oldest above this.
        flush_interval_s: target time between sink invocations.
        batch_size: max events per sink call.
    """

    sink: Callable[[Iterable[Event]], None]
    max_buffer: int = 10_000
    flush_interval_s: float = 5.0
    batch_size: int = 256
    _buffer: Deque[Event] = field(default_factory=lambda: deque(maxlen=10_000))
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _stop: threading.Event = field(default_factory=threading.Event)
    _thread: threading.Thread | None = None

    def __post_init__(self) -> None:
        self._buffer = deque(maxlen=self.max_buffer)

    def emit(self, event: Event) -> None:
        with self._lock:
            self._buffer.append(event)

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="wcbot-telemetry"
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.flush_interval_s + 1)
        self.flush_once()

    def flush_once(self) -> int:
        with self._lock:
            batch = list(self._buffer)
            self._buffer.clear()
        if not batch:
            return 0
        # Best-effort: chunk into batch_size groups for the sink.
        for i in range(0, len(batch), self.batch_size):
            self.sink(batch[i : i + self.batch_size])
        return len(batch)

    def _run(self) -> None:
        while not self._stop.wait(self.flush_interval_s):
            try:
                self.flush_once()
            except Exception:  # noqa: BLE001 — telemetry must never crash the host
                pass


def event_to_jsonl(event: Event) -> str:
    return json.dumps(
        {"t": event.timestamp_s, "kind": event.kind, **event.payload}
    )


def now_s() -> float:
    return time.time()
