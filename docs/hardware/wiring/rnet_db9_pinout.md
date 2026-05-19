# R-Net DB9 pinout (host port)

Used on most R-Net chairs (Permobil, Quantum, some Sunrise). The DB9
on the joystick or seat module exposes the bus to a host (PC programmer,
attendant control, our adapter).

## Pinout (DB9 female, looking into the connector)

```
   1  2  3  4  5
    o  o  o  o  o
     o  o  o  o
     6  7  8  9
```

| Pin | Signal | Notes |
|-----|--------|-------|
| 1 | +12 V (switched) | from chair battery via DC-DC; ~500 mA available |
| 2 | CAN_H | 125 kbps, ISO 11898-2 |
| 3 | CAN_L | |
| 4 | GND | chassis ground |
| 5 | (reserved) | leave NC |
| 6 | INHIBIT | active low — pulls down to inhibit drive (latched) |
| 7 | LOCK | active low — engages park brake |
| 8 | +5 V (logic) | low-current logic supply |
| 9 | (reserved) | NC |

## Safe-tap procedure

1. Battery off.
2. Insert a DB9 M-F passthrough with all pins broken out to test points.
3. Battery on. Confirm with meter: pin 1 ≈ 12 V, pin 8 ≈ 5 V, pin 4 GND.
4. Confirm CAN with logic analyser; should see ~10 ms cadence joystick
   frames at 125 kbps.
5. Capture 60 s baseline (joystick stationary) → `tests/captures/rnet_idle.csv`.
6. Capture 60 s drive sequence (forward, back, L, R) → `rnet_drive.csv`.
7. Disconnect; analyse offline.

## Adapter board

The Phase 3 adapter is a small PCB with:
- ISO1050 isolated CAN transceiver
- 12 V → 5 V DC-DC for the RP2040 supervisor
- DB9 M passthrough + 3.5 mm e-stop jack (wired to estop_relay_v1)

Only after captures match the adapter skeleton in
`src/wheelchair/adapters/rnet.py` does the adapter ever drive the
`INHIBIT` pin or inject joystick frames.

## Inject mode (the "live" mode)

Two safety locks must be cleared before inject mode is permitted:

1. The hardware e-stop relay must be present and verified (HIL test).
2. The user must hold the **physical** deadman on the OEM joystick at
   the same time as their tele-op input — true joint authority. The
   OEM joystick remains the legal control.
