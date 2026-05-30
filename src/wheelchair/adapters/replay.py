"""Cabana-format CAN capture replay (for adapter unit tests).

Cabana / openpilot store captures as CSV with columns:
``time, addr, bus, data`` — data is hex-encoded.

Usage in tests::

    for frame in replay_csv("tests/captures/rnet_drive_forward.csv"):
        sig = adapter.decode(frame)
        if sig:
            ...
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .base import AdapterFrame


def replay_csv(path: str | Path) -> Iterable[AdapterFrame]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield AdapterFrame(
                timestamp_s=float(row["time"]),
                arbitration_id=int(row["addr"], 0),
                data=bytes.fromhex(row["data"]),
            )
