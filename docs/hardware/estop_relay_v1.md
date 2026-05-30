# E-stop relay v1 — design

Closes the hardware half of [G-04](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/22).
Talks to `wheelchair.safety.EmergencyStop.hardware_gpio_drop`.

## Goals

- Drop motor controller enable line within **50 ms** of any of:
  - Pi software asserting E-STOP GPIO low
  - Pi watchdog GPIO stops toggling
  - Operator pressing the physical e-stop button (NC)
  - Loss of 5 V logic supply
- **Latched** — only manual reset (key-switch) re-energises.
- **Energise-to-run** — power loss = stop. No fault possible by losing power.

## Topology

```
                  +12V
                   │
                   ┴   [user e-stop button NC]
                   ┬
                   │
       ┌───────────┼────────────────┐
       │           │                │
   [555 monostable]                 │
       │ Q                          │
   ┌───┴───┐                        │
   │ ↗ ↗   │  ← retriggerable; Pi GPIO toggles its trigger pin
   │ ↗     │      at >=100 Hz. If kicks stop, Q drops low after T_out.
   │       │
   └───┬───┘                        │
       │ NOT Q                      │
       └─────►┐ AND ◄───────────────┘
              │       ◄── PI_ESTOP_N (active low from software)
              ▼
        +5V ──┤
              │
           [latching relay]
              │
              ▼
        MOTOR_CTRL_ENABLE (to H-bridge / wheelchair controller enable input)
```

## Parts (indicative)

| Ref | Part | Notes |
|-----|------|-------|
| U1 | NE555 (TLC555 CMOS variant) | `T_out` ≈ 30 ms |
| U2 | 74HC08 (AND) | 5 V logic |
| K1 | Omron G6S latching DPDT | 5 V coil, 2 A contacts |
| SW1 | EAO 84-series mushroom | IEC 60947-5-5 compliant, NC |
| SW2 | Key switch | reset only |
| D1..D3 | 1N4148 | flyback / clamp |
| R/C | per NE555 datasheet | sized for T_out ≈ 30 ms |

## Pi GPIO contract

| Signal | BCM pin (suggested) | Direction | Idle | Active | Notes |
|--------|---------------------|-----------|------|--------|-------|
| `PI_ESTOP_N` | 27 | OUT | HIGH | LOW = STOP | Software-driven by `EmergencyStop.hardware_gpio_drop` |
| `WD_KICK` | 4 | OUT | toggling | static = STOP | Watchdog — toggle every 10 ms in control loop |
| `RELAY_STATE` | 5 | IN | — | — | Read-back; CI HIL test asserts state |

## Acceptance test (HIL)

- `tests/hil/test_estop_drop_time.py` — Saleae captures `MOTOR_CTRL_ENABLE`; software issues `EmergencyStop.engage()`; assert falling edge within 50 ms.
- `tests/hil/test_watchdog_drop.py` — `kill -9` the controller process; assert `MOTOR_CTRL_ENABLE` low within 100 ms (G-01 contract + 555 T_out).
- `tests/hil/test_power_loss.py` — Yank 5 V supply; assert `MOTOR_CTRL_ENABLE` low within 50 ms.

## Out of scope (Phase 1)

- PCB layout, Gerbers, fabrication (use a perfboard prototype for Phase 1 HIL).
- IEC 60601-1 essential-performance documentation (Phase 5).
