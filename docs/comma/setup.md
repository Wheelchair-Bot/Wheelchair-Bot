# comma 3X bench bring-up

Goal: get a comma 3X reading CAN from a bench harness and forwarding to
Wheelchair-Bot's `CommaPandaDrive`. No chair on the floor.

## Hardware

- comma 3X (or comma three — same software target, just better thermals on 3X)
- red panda or panda tres (CAN-FD where available)
- OBD-C cable + breakout to DB9 (R-Net) or DCI (Shark) or 4-pin (VR2)
- Bench wheelchair-controller (Permobil M3 ICS for the alpha)
- Lab PSU 24 V / 5 A
- E-stop relay (see `docs/hardware/estop_relay_v1.md`)

## Topology

```
       +24V lab PSU                       +12V comma 3X
            │                                  │
            ▼                                  ▼
     ┌──────────────┐                  ┌──────────────────┐
     │ Permobil M3  │ ◄──── CAN ──────►│ red panda (CAN0) │ ◄─USB─ comma 3X
     │ ICS bench    │                  │                  │
     └──────────────┘                  └──────────────────┘
            │                                  │
            └─────── e-stop relay ─────────────┘
                          ▲
                          │
                  user mushroom button
```

## Software

1. Flash comma 3X with current openpilot dev branch (or a Wheelchair-Bot
   fork once we have one).
2. SSH into the device. Clone Wheelchair-Bot into `/data/wcbot`.
3. Add a manager entry:
   ```python
   from wheelchair.comma.supervisor import Supervisor, ProcessSpec
   sup = Supervisor(
       processes=[
           ProcessSpec("teleop", run_teleop_server, essential=True),
           ProcessSpec("comma_drive", run_comma_drive_loop, essential=True),
           ProcessSpec("telemetry", run_telemetry_uploader, essential=False),
       ],
       on_essential_failure=lambda _n: emergency_stop.engage(EStopReason.EXTERNAL),
   )
   sup.start()
   ```
4. `cd /data/wcbot && python -m wheelchair.cli --drive comma_panda --adapter rnet`.
5. Watch `pandaStates` and `wcbotState` with `cereal_log` to confirm.

## Smoke checks

- `panda.set_safety_mode(ALLOUTPUT)` only when we heartbeat at ≥10 Hz; loss of heartbeat drops to `NOOUTPUT` within 500 ms.
- HIL test `test_can_bus_fault_reverts_to_local_safe_state` passes against the bench rig.

## Out of scope (Phase 4)

- comma four — wait for SDK availability.
- Vehicle-in-loop on a real chair — Phase 5.
- Field beta — Phase 5.
