# Wheelchair-Bot risk file — v0.1 (skeleton)

Per **IEC 60601-1 §4.2** and **ISO 14971** risk-management process.

> ⚠️ This is a draft skeleton produced by engineering for the regulatory
> consultant to expand into a formal dossier. It is not a substitute
> for a qualified ISO 14971 process. **Not for submission.**

## 1. Intended use

A retrofittable computer + sensor pack that allows a qualified rider or
attendant to **tele-operate** a commercial powered wheelchair using a
smartphone or browser interface. Tele-operation is supervised at all
times by the rider or a designated remote driver. The device does
**not** replace the OEM joystick and does **not** make autonomous
decisions about destination, route, or speed.

Operational design domain (ODD):
- Indoor (homes, care facilities, accessible buildings)
- Outdoor sidewalks and accessible pathways
- Daylight or well-lit indoor conditions
- Single occupant; rider weight within OEM chair's spec
- Ambient temperature 0–40 °C
- Not on public roads, not in vehicle lanes, not in airport tarmac, not in mines/industrial sites

## 2. Stakeholders

- Primary user — wheelchair rider
- Secondary user — remote driver (caregiver / family / clinician)
- Maintainer — clinician or technician who pairs devices and reviews logs
- Manufacturer — Wheelchair-Bot project

## 3. Hazards & risk register (initial pass)

| ID | Hazard | Cause | Sequence of events | Harm | Severity | Probability | Mitigation | Residual |
|----|--------|-------|--------------------|------|----------|-------------|------------|----------|
| H-01 | Unintended motion | Stale tele-op command | network lag → command repeats | minor injury, property damage | 3 | 3 | `CommandWatchdog` (G-01) + panda heartbeat watchdog | 2×2 |
| H-02 | Unintended motion | Software crash | Python OOM → no further commands | as above | 3 | 2 | dual watchdog + e-stop relay (G-04) | 2×1 |
| H-03 | Rider lost control | Authority conflict | tele-op contradicts OEM joystick | minor injury | 3 | 2 | OEM joystick is authoritative; dual deadman required in inject mode | 2×1 |
| H-04 | Rollover | Tilt while turning | high speed on uneven ground | major injury | 4 | 2 | `TiltMonitor` (G-05) + speed-on-tilt limiter | 3×1 |
| H-05 | Thermal runaway | Motor overcurrent | locked rotor against obstacle | fire, burns | 4 | 1 | `OvercurrentMonitor` (G-02) at MCU level | 3×1 |
| H-06 | Loss of mobility | Battery drained | extended tele-op with display on | stranded user | 2 | 3 | `LowVoltageCutoff` (G-06) at 22.5 V | 2×2 |
| H-07 | Unauthorised control | Stolen / replayed token | weak auth | privacy + safety | 4 | 2 | bearer token + sha256-hashed store + TLS (G-23) | 3×1 |
| H-08 | Privacy leak | Camera stream | unencrypted WebRTC | privacy | 3 | 2 | DTLS-SRTP (WebRTC default); auth-gated signaling | 2×1 |
| H-09 | Bus collision | Concurrent OEM + adapter | both writing R-Net joystick frames | erratic motion | 3 | 2 | adapter mode requires OEM deadman released; rate-limit | 2×1 |
| H-10 | Firmware regression | OTA breaks adapter | new R-Net version changes codec | unintended motion | 3 | 2 | per-chair captures committed to CI; nightly replay | 2×1 |

Severity / Probability scale: 1 (negligible) → 5 (catastrophic).

## 4. Risk-control verification matrix

Each control points to the test that verifies it. CI must run those
tests on every commit (`@pytest.mark.safety` job) and the HIL rig must
run them nightly (`@pytest.mark.hil`).

| Control | Software test | HIL test | Field test |
|---------|---------------|----------|------------|
| `CommandWatchdog` | `test_watchdog_stops_motors_within_100ms_of_command_loss` | `test_watchdog_drop_after_kill_9` | telemetry sentinel |
| `DeadmanSwitch` GPIO | `test_deadman_release_drives_pwm_to_zero_at_gpio_level` | same name, logic-analyser-asserted | n/a |
| `TiltMonitor` | `test_tilt_cutoff_at_25_deg_sustains_under_vibration` | manual tilt-table test | beta opt-in only |
| `LowVoltageCutoff` | `test_lvc_cuts_at_22_5V_for_24V_pack` | bench PSU sweep | telemetry alert |
| `OvercurrentMonitor` | `test_overcurrent_uses_max_of_both_motors` | `test_overcurrent_trip_within_one_pwm_cycle` | telemetry alert |
| `EmergencyStop` latch | `test_estop_is_latched_until_cleared` | full-stack | incident log |
| Hardware e-stop relay | n/a | `test_estop_drop_time` | quarterly inspection |
| Panda safety mode | `test_panda_blocks_send_in_nooutput` | bench bring-up | continuous |

## 5. Post-market surveillance

- Telemetry uploader (Phase 5) writes anonymised event logs to S3.
- Any S0 event (e-stop engagement during tele-op, watchdog timeout,
  current trip) opens an issue in the field-incidents GitHub project
  within 24 h.
- Quarterly review by regulatory consultant.

## 6. Open items for regulatory counsel

- Classification under FDA 21 CFR 890.3700 (powered wheelchair) — does
  this retrofit re-classify the host chair?
- EU MDR 2017/745 — class I or II? Notified body needed?
- ISO 14971 risk acceptability criteria — formal numeric thresholds.
- ISO 7176-14 — full controller compliance test plan.
- IEC 60601-1-2 EMC — chamber test in Phase 5b.
