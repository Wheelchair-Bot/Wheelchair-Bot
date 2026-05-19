# Perception via comma sensors (G-25)

comma 3X exposes (via cereal):
- dual road cameras (forward + wide) — `roadCameraState`, `wideRoadCameraState`
- driver camera — `driverCameraState`
- BMI088 IMU at 100 Hz
- u-blox NEO-M9N GPS
- Snapdragon ISP + GPU

For Wheelchair-Bot we re-purpose them:

| Sensor | OpenPilot use | Wheelchair-Bot use |
|--------|---------------|---------------------|
| Forward road cam | lane / lead-car | obstacle avoidance, tele-op video, doorway alignment |
| Wide road cam | adjacent lanes | side clearance check |
| Driver cam | gaze / drowsy | operator presence (optional deadman input) |
| IMU | localisation, gyro health | tilt cutoff (Phase 1 `TiltMonitor` feeds from this) |
| GPS | location | telemetry / geofencing for beta |

Forwarding the road camera to the tele-op WebRTC track replaces the
Phase 2 stubbed video path (the one that needed a Pi camera). On a
comma device we get a properly time-synced H.265 stream for free.
