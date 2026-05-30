# Panda + Wheelchair-Bot safety model

The panda is a **second independent watchdog** on top of the software
`CommaPandaDrive`. This is the property that makes the comma stack
attractive for safety-critical control.

## Boot-time

1. Comma 3X boots, openpilot launches, panda enters `SILENT` mode by default.
2. Wheelchair-Bot supervisor launches; `CommaPandaDrive.__init__` does
   NOT yet enable output.
3. Operator pairs their phone (auth handshake from Phase 2).
4. Operator presses-and-holds physical deadman on the OEM joystick AND
   the tele-op deadman in their phone app simultaneously.
5. Supervisor calls `PandaBridge.enable_output()` → `set_safety_mode(ALLOUTPUT)`.
6. Heartbeats start at 100 Hz.

## Runtime

```
                  ┌───────────────────────────┐
                  │ Wheelchair-Bot supervisor │
                  └─────────────┬─────────────┘
                                │ heartbeat (100 Hz)
                                ▼
                  ┌───────────────────────────┐
                  │ panda firmware            │
                  │   safety_mode=ALLOUTPUT   │
                  │   heartbeat watchdog      │
                  └─────────────┬─────────────┘
                                │ sendcan
                                ▼
                      Chair controller CAN bus
```

Loss of heartbeat for >500 ms → panda drops to `NOOUTPUT`. Drive stops.
Wheelchair-Bot software watchdog `CommandWatchdog` independently catches
the same condition and engages `EmergencyStop`. The two watchdogs are
intentionally redundant.

## Failure modes covered

| Failure | Caught by | Recovery |
|---------|-----------|----------|
| Linux crash | panda heartbeat timeout | manual reset of EmergencyStop |
| Python GIL stall | panda heartbeat timeout | as above |
| USB cable unplug | panda heartbeat timeout | as above |
| Wi-Fi loss → tele-op disconnect | `wheelchair.app.server` calls `safety_stop("ws_disconnect")` | operator reconnect + clear |
| OEM joystick deadman release | dual-purpose deadman wire (`deadman_wiring.md`) | re-grip |
| Tele-op deadman release | `DeadmanSwitch.release()` | re-press |
| Tilt / current / LVC | Phase 1 monitors | manual reset |

## Out of scope here

- The panda's *built-in* model-specific safety modes for cars: we don't
  use them; this is a wheelchair, not an automobile. We use panda only
  as a CAN bridge + heartbeat-gated output.
- Custom panda firmware: we should stay on stock for as long as
  possible to inherit upstream fixes.
