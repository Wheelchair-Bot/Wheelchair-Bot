# INA226 current sense board — design

Closes the hardware half of [G-02](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/20).
Talks to `wheelchair.safety.OvercurrentMonitor` via a dedicated MCU.

## Why a separate MCU

Linux is not fit for hard real-time over-current protection. A wall-clock
hiccup of 10 ms at 60 A motor current causes thermal damage. The
sense board mounts a small MCU (RP2040 or ATtiny1614) that polls the
INA226 at >=1 kHz and trips an output line independent of Linux state.
Linux gets a low-rate telemetry stream and a trip-event interrupt.

## Per-motor channel

```
                  Battery + ──── Shunt R_S ──── Motor L+ ────► H-bridge
                                  │   │
                                  │   │
                                ┌─┴───┴─┐
                                │ INA226│  I2C
                                │       │──────► RP2040 ───► TRIP_N (open-drain)
                                │       │                       │
                                └───────┘                       │
                                                                ▼
                                                 wired-OR into  E-STOP chain (estop_relay_v1)
```

Repeat for the right motor.

## Parts per channel

| Ref | Part | Notes |
|-----|------|-------|
| R_S | 1 mΩ 5 W shunt | Bourns CSS2H-3920K |
| U1 | INA226 | I2C, programmable alert |
| U2 | RP2040 (shared between channels) | Pico W footprint |
| D1 | TVS diode | bus protection |

## Trip thresholds (Permobil M3 example)

| Threshold | Value | Source |
|-----------|-------|--------|
| `max_continuous_a` | 30 A | `wheelchair_bot/wheelchairs/models.py` Permobil M3 |
| `max_peak_a` | 50 A | same |
| `peak_window_s` | 100 ms | conservative; tune per chair |

Values programmed into the RP2040 over I2C at boot; mirrored in
`OvercurrentMonitor` for telemetry assertion (configurable via the
wheelchair model dataclass in `wheelchair.wheelchairs`).

## Telemetry stream

| Field | Type | Rate |
|-------|------|------|
| `left_a` | float32 | 100 Hz to Linux |
| `right_a` | float32 | 100 Hz |
| `bus_v` | float32 | 10 Hz |
| `trip_event` | bool + reason byte | edge-triggered |

Linux subscribes via the existing cereal topic registry (Phase 4) or
a simple UART JSON line until then.

## Acceptance test (HIL)

`tests/hil/test_overcurrent_trip_within_one_pwm_cycle.py` — electronic
load steps to 70 A; assert `TRIP_N` falls within 1 ms (target) /
10 ms (max acceptable for Phase 1 release).
