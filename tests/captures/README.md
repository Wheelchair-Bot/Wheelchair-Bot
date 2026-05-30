# CAN captures

Cabana-format CSV files of real wheelchair-controller traffic.

These are the regression fixtures that turn the Phase 3 adapter
skeletons into actual codecs. **Committed CSVs are anonymised** —
no serial numbers, no chair-specific session keys.

| File | Family | Source | Notes |
|------|--------|--------|-------|
| `rnet_idle.csv` | R-Net | Permobil M3, 60 s | joystick centre |
| `rnet_drive.csv` | R-Net | same | forward / reverse / left / right |
| `shark_idle.csv` | Shark | Pride Jazzy, 60 s | |
| `shark_drive.csv` | Shark | same | |
| `vr2_idle.csv` | VR2 | Sunrise Quickie, 60 s | |
| `vr2_drive.csv` | VR2 | same | |

Captures land in follow-up PRs once bench access to each family exists
(#29).
