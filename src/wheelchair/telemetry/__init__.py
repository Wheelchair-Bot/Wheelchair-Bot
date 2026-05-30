"""Field-beta telemetry uploader (Phase 5).

Buffered, lossy-by-design uploader. The Pi / comma device must never
block on telemetry — safety is the priority. If the uploader cannot
keep up it drops oldest first.
"""

from .uploader import Event, TelemetryUploader

__all__ = ["Event", "TelemetryUploader"]
