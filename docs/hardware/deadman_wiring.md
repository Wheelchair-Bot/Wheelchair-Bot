# Deadman wiring — design

Closes the hardware half of [G-03](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/21).
Talks to `wheelchair.safety.DeadmanSwitch`.

## Topology

```
   Operator deadman (NO momentary)
              │
              │
      +5V ────┤
              │
              ├── DEADMAN_IN (BCM 6, pulled down on Pi)
              │
              └── direct hard-wire to AND-gate input of estop_relay_v1
```

The deadman input is **dual-purpose**:

1. Pi reads it (GPIO BCM 6), passes presence to `DeadmanSwitch.press()`
   on each control-loop iteration while held.
2. **Same wire** feeds the AND gate in `estop_relay_v1` directly.
   Release of the deadman drops `MOTOR_CTRL_ENABLE` even if the Pi has
   wedged. Verified with logic analyser in the Phase 1 HIL test
   `test_deadman_release_drives_pwm_to_zero_at_gpio_level` (also exists
   as a pure-software contract test in `src/tests/test_safety_deadman.py`).

## Why dual-purpose

Software-only deadman has been documented to have a race window between
expiry detection and the next motor-write. By tying the operator switch
to the hardware e-stop chain we get the same property as a chain saw
chain brake: release = stop, no path that depends on software.

## Timing budget

| Event | Max latency |
|-------|------------|
| Operator release → AND gate goes low | < 1 ms (wire + switch bounce) |
| AND low → relay drop | < 30 ms (relay datasheet) |
| `DeadmanSwitch.check()` → `stop_callback()` | < 1 ms (software) |
| **Total release-to-PWM-zero** | < 50 ms |
