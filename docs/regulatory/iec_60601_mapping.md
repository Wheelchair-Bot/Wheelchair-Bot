# IEC 60601-1 + 60601-2-1 clause coverage (partial)

Mapping of relevant clauses to Wheelchair-Bot artefacts. **Numerous
gaps**; this file is a tracker, not evidence of compliance.

| Clause | Title | Applicable? | Evidence / artefact |
|--------|-------|-------------|---------------------|
| 4.2 | Risk management process | yes | [risk_file.md](risk_file.md) |
| 4.3 | Essential performance | yes | TBD — define minimum acceptable motion control |
| 4.5 | Equivalent safety | yes | dual-watchdog architecture; see [comma/safety_model.md](../comma/safety_model.md) |
| 4.8 | Components of high integrity | yes | hardware e-stop relay (estop_relay_v1) latching; key switch reset |
| 5.4 | Process for design and development | yes | this repository + linked issues + PRs |
| 7.2 | Markings on outside of ME equipment | TBD | manufacturing follow-up |
| 8.4 | Excessive currents | yes | OvercurrentMonitor (G-02), INA226 hardware |
| 8.7 | Insulation | TBD | mechanical PCB design |
| 9 | Mechanical hazards | yes | tilt cutoff; OEM chair retains weight rating |
| 11.1 | Excessive temperatures | yes | thermal model in emulator; comma 3X sealed enclosure |
| 11.6.5 | Spillage | yes | indoor use; sealed enclosures on comma + e-stop board |
| 12 | Accuracy of controls / instruments | yes | tele-op latency budget < 100 ms; tracked in telemetry |
| 14 | Programmable electrical medical systems (PEMS) | **yes — core** | IEC 62304 process needed; see below |
| 17 | EMC | yes | IEC 60601-1-2 chamber test scheduled Phase 5b |

## IEC 62304 (software lifecycle) — interim plan

| Activity | Class | Where in repo |
|----------|-------|---------------|
| Software development plan | C (safety-critical) | this roadmap (`docs/AUDIT_planning.md`) |
| Risk-control measures | C | `src/wheelchair/safety/` + tests |
| Software requirements | C | issues #19..#26 + per-PR spec |
| Architectural design | C | `docs/AUDIT_architecture.md` |
| Detailed design | C | code + comments |
| Unit + integration tests | C | `src/tests/` + nightly HIL |
| Problem resolution | C | GitHub Issues + the field-incidents project |
| Maintenance plan | C | OTA cadence + rollback procedure (Phase 5b) |

## IEC 60601-2-1

Particular standards for powered wheelchairs. Per-clause mapping lands
when a regulatory consultant engages (Phase 5).
