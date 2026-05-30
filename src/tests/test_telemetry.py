"""Tests for the field-beta telemetry uploader (Phase 5)."""

from __future__ import annotations

from wheelchair.telemetry import Event, TelemetryUploader
from wheelchair.telemetry.uploader import event_to_jsonl


def test_buffered_emit_then_flush() -> None:
    sunk: list = []
    up = TelemetryUploader(sink=lambda batch: sunk.extend(list(batch)), max_buffer=100)
    up.emit(Event(timestamp_s=1.0, kind="estop", payload={"reason": "tilt"}))
    up.emit(Event(timestamp_s=2.0, kind="wd_expiry"))
    n = up.flush_once()
    assert n == 2
    assert [e.kind for e in sunk] == ["estop", "wd_expiry"]


def test_overflow_drops_oldest() -> None:
    sunk: list = []
    up = TelemetryUploader(sink=lambda batch: sunk.extend(list(batch)), max_buffer=3)
    for i in range(10):
        up.emit(Event(timestamp_s=float(i), kind="x"))
    up.flush_once()
    assert len(sunk) == 3
    assert [e.timestamp_s for e in sunk] == [7.0, 8.0, 9.0]


def test_batch_chunks_to_sink() -> None:
    chunks: list[int] = []

    def sink(batch):
        chunks.append(sum(1 for _ in batch))

    up = TelemetryUploader(sink=sink, max_buffer=1000, batch_size=4)
    for i in range(10):
        up.emit(Event(timestamp_s=float(i), kind="x"))
    up.flush_once()
    assert chunks == [4, 4, 2]


def test_jsonl_serialisation_round_trip() -> None:
    import json

    e = Event(timestamp_s=1.5, kind="estop", payload={"reason": "tilt"})
    line = event_to_jsonl(e)
    parsed = json.loads(line)
    assert parsed == {"t": 1.5, "kind": "estop", "reason": "tilt"}


def test_sink_failure_does_not_propagate() -> None:
    def bad_sink(batch):
        raise RuntimeError("network down")

    up = TelemetryUploader(sink=bad_sink, max_buffer=100, flush_interval_s=0.05)
    up.emit(Event(timestamp_s=0.0, kind="x"))
    up.start()
    import time as _t

    _t.sleep(0.15)
    up.stop()  # must not raise
