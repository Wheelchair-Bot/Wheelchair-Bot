# Cereal topic mapping

| Cereal topic | Direction | Wheelchair-Bot consumer/producer | Notes |
|--------------|-----------|----------------------------------|-------|
| `pandaStates` | comma → wcbot | `wheelchair.safety.comma_watchdog` (Phase 4 follow-up) | engages local stop on heartbeat loss |
| `can` | bi-directional | `wheelchair.drives.comma_panda.CommaPandaDrive` | sniff (decode) + inject (encode) |
| `sendcan` | wcbot → comma | `CommaPandaDrive.send` | gated by panda safety mode |
| `carState` | comma → wcbot | mapped to `wheelchair.interfaces.WheelchairState` | reuse OpenPilot's KalmanFilter |
| `carControl` | wcbot → comma | from tele-op `(linear, angular)` | desired velocity |
| `roadCameraState` / `wideRoadCameraState` | comma → wcbot → client | streamed to tele-op WebRTC track | Phase 4 follow-up |
| `driverMonitoringState` | comma → wcbot | folds into `DeadmanSwitch.press()` | optional gaze-based deadman |
| `liveLocationKalman` | comma → wcbot | telemetry + path replay | |
| `wcbotState` | local | `WheelchairState` snapshot | wheelchair-specific |
| `wcbotControl` | local | desired motion + deadman | replaces direct fn calls in supervised process |
| `wcbotSafety` | local | `EStopEvent` fan-out | |
| `wcbotTelemetry` | local → cloud | rolled-up state for field beta | Phase 5 |
