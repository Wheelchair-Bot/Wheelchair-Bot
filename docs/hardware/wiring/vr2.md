# VR2 / Pilot+ (PG Drives)

Common on Sunrise Medical, older Permobil mid-tier chairs. Same DB9
host connector as R-Net mechanically but **different bitrate and
message set** — do not assume the R-Net adapter will work on VR2.

## Differences vs. R-Net

| | R-Net | VR2 |
|---|-------|-----|
| Bitrate | 125 kbps | 125 kbps |
| Joystick frame ID | `0x02000000` (provisional) | `0x0CFF1000` (provisional) |
| Joystick payload | two signed-8 | two signed-16 LE |
| Heartbeat | required | required, different ID |
| Programming tool | R-Net PG Programmer | PG Drives PC Programmer |

Pinout is identical to `rnet_db9_pinout.md`.
