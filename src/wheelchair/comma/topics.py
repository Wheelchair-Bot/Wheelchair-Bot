"""Cereal topic registry for the wheelchair use case.

We reuse openpilot's existing topics where they fit and define our own
under the ``wcbot`` prefix for wheelchair-specific state. Topic names
are the contract between processes; bump the schema version at the
bottom whenever a field changes meaning.
"""

from __future__ import annotations

from enum import Enum


class Topic(str, Enum):
    # From openpilot — read-only for us
    PANDA_STATES = "pandaStates"
    CAN = "can"
    SEND_CAN = "sendcan"
    ROAD_CAMERA = "roadCameraState"
    WIDE_ROAD_CAMERA = "wideRoadCameraState"
    DRIVER_CAMERA = "driverCameraState"
    LIVE_KALMAN = "liveLocationKalman"
    DRIVER_MONITORING = "driverMonitoringState"

    # Wheelchair-specific
    WCBOT_STATE = "wcbotState"
    WCBOT_CONTROL = "wcbotControl"
    WCBOT_SAFETY = "wcbotSafety"
    WCBOT_TELEMETRY = "wcbotTelemetry"


SCHEMA_VERSION = 1
