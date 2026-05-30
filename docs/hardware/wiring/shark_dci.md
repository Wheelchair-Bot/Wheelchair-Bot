# Shark / DX (Dynamic Controls) DCI bus

DCI is a proprietary 4-pin bus on most Invacare and Pride chairs with
Dynamic Controls electronics. Some newer chairs expose CAN at 250 kbps
on the same physical connector.

## Pinout (4-pin square, looking into harness)

| Pin | Signal | Notes |
|-----|--------|-------|
| 1 | +24 V (switched) | from battery; ~200 mA |
| 2 | DCI_A / CAN_H | |
| 3 | DCI_B / CAN_L | |
| 4 | GND | |

## Safe-tap

Same procedure as `rnet_db9_pinout.md`. If you see CAN cadence at
250 kbps, the chair is on the newer CAN-DCI; otherwise treat as a
differential DCI bus and use the Dynamic Controls programming dongle
schematic (see Dynamic Controls Service Manual, chapter 4) as a guide
for line termination.
