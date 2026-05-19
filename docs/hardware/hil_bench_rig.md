# Hardware-in-the-loop bench rig

Closes [G-17](https://github.com/Wheelchair-Bot/Wheelchair-Bot/issues/35).
Expanded from `AUDIT_planning.md §3.4`.

## Purpose

A repeatable bench setup that exercises the Phase 1 safety stack
without any live wheelchair. Every PR labelled `severity:S0` runs
against this rig nightly via a self-hosted GitHub Actions runner.

## Bill of materials (~$965)

| Qty | Item | Part / model | ≈ cost | Purpose |
|-----|------|--------------|--------|---------|
| 1 | Raspberry Pi 5 8 GB | — | $90 | DUT (compute) |
| 1 | PoE+ HAT | Waveshare | $30 | clean power + cooling |
| 1 | H-bridge | BTS7960 dual | $20 | motor driver |
| 2 | 12 V geared motor + encoder | Pololu 70:1 | $80 | load |
| 2 | INA226 breakout | Adafruit | $20 | current sense |
| 1 | RP2040 Pico W | — | $10 | safety MCU (current-trip) |
| 1 | Programmable PSU 30 V / 10 A | Riden RD6018 | $200 | battery sim |
| 1 | CAN board MCP2515 + TJA1050 | — | $25 | bench R-Net/Shark capture |
| 1 | Saleae Logic Pro 8 | — | $400 | PWM + CAN capture |
| 1 | Latching relay + 555 perfboard | per `estop_relay_v1.md` | $40 | e-stop |
| 1 | Frame + DIN rail + cabling | — | $50 | mechanical |
| **Total** | | | **≈$965** | |

## Topology

```
            ┌─────────────────────────────────────────────────┐
            │                                                 │
            │     Riden PSU (battery sim, 24V/10A)            │
            │                                                 │
            └────────┬──────────────────┬─────────────────────┘
                     │ +24V             │ -
                     ▼                  │
            ┌────────────────┐          │
            │ E-stop relay   │ ─────────┤
            └────┬───────────┘          │
                 │                      │
            ┌────▼───────┐     ┌────────▼────────┐
            │ BTS7960    │     │ INA226 ×2       │
            │ H-bridge   │ ◄── │ + RP2040 trip   │
            └────┬───────┘     └─────────────────┘
                 │
        ┌────────┼────────┐
        │L+   L-  R+   R-│
        ▼                ▼
       Motor L          Motor R  (encoders → Pi)
              │
              │ PWM, DIR
              │
            ┌─▼──────────────────────┐
            │ Raspberry Pi 5 (DUT)   │◄── Saleae Logic Pro 8
            │   - control loop       │      (PWM, e-stop line, CAN)
            │   - watchdog kick      │
            └──────────────┬─────────┘
                           │ USB
                           ▼
                    GitHub Actions
                    self-hosted runner
```

## Running locally

```bash
# scripts/hil_smoke.py runs the full HIL suite on the rig.
# Assumes the rig is at $HIL_TARGET (ssh user@host).
python scripts/hil_smoke.py --target $HIL_TARGET
```

## CI integration

Nightly GitHub Actions job on a self-hosted runner labelled `hil`:

```yaml
hil-nightly:
  if: github.event.schedule
  runs-on: [self-hosted, hil]
  steps:
    - uses: actions/checkout@v4
    - run: pytest -m hil -v --junitxml=hil.xml
    - uses: actions/upload-artifact@v4
      with:
        name: saleae-captures
        path: captures/
```
