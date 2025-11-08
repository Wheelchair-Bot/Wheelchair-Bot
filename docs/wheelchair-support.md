# WHEELCHAIR SUPPORT COMPATIBILITY REFERENCE

> Status: Living document (v2025-11-08). Purpose: Define and prioritize electronic wheelchair models targeted for adapter / interface support (input devices, sensing, telemetry) based on US market popularity and connector accessibility.

## 1. Scope & Goals
This document catalogs high-impact electric wheelchair models sold in (or frequently imported to) the United States from 2022–2025 and assigns support priority tiers for a universal adapter / integration kit. It emphasizes:
- Controller interface availability (analog proportional, digital bus, CAN / RS485, proprietary multi-drop).
- Connector physical form factors (DB9, 4-pin DCI, 3-pin / 4-pin XLR, LiNX DX bus module, proprietary battery port, USB-C).
- Market share concentration to maximize addressable users with minimal hardware SKUs.
- Technical feasibility (signal accessibility without firmware reverse engineering, safety isolation).

## 2. Support Prioritization Framework
| Tier | Target Coverage Goal | Criteria | Typical Tasks |
|------|----------------------|---------|--------------|
| **Tier 1 (Immediate)** | ~55–65% of active US users | High-volume consumer & travel models; rehab platforms with open/known joystick analog input (R-Net DB9, VR2/Pilot+ 4-pin, Shark DCI) | Adapter harnesses, input mapping, basic telemetry (speed, battery %). |
| **Tier 2 (Near-Term)** | +20–25% incremental | Mid / heavy-duty & emerging digital bus (LiNX DX, Q-Logic 3, NE Series) where documentation or reverse-engineering path is moderate | Bus sniffing tools, protocol abstraction layer, configuration utilities. |
| **Tier 3 (Backlog / Specialized)** | Remaining niche (<15%) | Proprietary or low-volume, advanced seating integration (standing, vertical lift, pediatric), or encrypted buses | Research partnerships, OEM NDAs, safety validation. |

## 3. Key Connector & Protocol Focus
| Interface | Controller Family | Tier | Notes |
|-----------|-------------------|------|-------|
| DB9 (R-Net analog proportional) | PG Drives R-Net (legacy analog input sidecar) | 1 | Provides joystick X/Y, mode, enable lines. Widely used on Permobil & Sunrise Quickie (premium rehab). |
| 4-pin DCI (Dynamic Shark) | Dynamic Controls Shark / DX | 1 | Common on Merits, Shoprider, budget imports. Straightforward voltage & hall sense lines. |
| 4-pin VR2/Pilot+ | PG Drives VR2 / Pilot+ / VSI | 1 | Pride & Golden mid-tier; simple analog axis and switch matrix. |
| LiNX DX Bus (4-pin micro) | Dynamic Controls LiNX | 2 | Digital (CAN-like) bus; requires protocol sniffing; used by Invacare TDX SP2, Aviva RX, Golden LiteRider Envy (variants), Drive Titan AXS. |
| Q-Logic 3 / NE Series harness | Quantum Rehab (Q-Logic), PG Drives NE | 2 | Digital CAN/RS485 hybrid; supports specialty controls. Need abstraction layer. |
| Proprietary battery-side ports (WHILL, Robooter) | WHILL Intelligent, Robooter App-enabled | 2 | Integration via external accessory rather than joystick inline (safety). |
| High-current bariatric (VR2 120A / MK6i) | PG VR2 variants, Dynamic MK5/MK6i | 2 | Same signaling as standard VR2 + seat elevation interface. |
| Specialty pediatric / standing (Permobil F5 VS, Karman standing) | R-Net extended seat modules | 3 | Requires multi-module coordination; safety-critical. |

Coverage projection: Implementing Tier 1 harnesses yields adapter readiness for ~60–65% of targeted user base; Tier 2 expands to ~85%; Tier 3 completes long tail.

## 4. Comprehensive Model Support Matrix (Expanded)
Legend: P=Planned (tier assigned), S=Supported (implemented in code/hardware), R=Research. Popularity Rank: Derived from aggregated 2024–2025 reseller listings, insurance/DME claims, and online review volume (indicative, not absolute).

| Model | Manufacturer | Popularity Cluster | Tier | Status | Controller System | Primary Interface | Battery (Chemistry / Nominal) | MSRP Range (USD) | Segment | Integration Notes |
|-------|--------------|--------------------|------|--------|-------------------|-------------------|------------------------------|------------------|---------|------------------|
| Jazzy Carbon | Pride Mobility | Top 10 Travel | 1 | P | PG Drives VR2/Pilot+ | 4-pin analog | 24V Li-ion 12Ah (~288Wh) | 2.5K–3.5K | Portable/Travel | Lightweight; joystick removable; simple axis. |
| Jazzy Ultra Light | Pride Mobility | Top 10 Travel | 1 | P | PG Drives VR2/Pilot+ | 4-pin analog | 25.2V Li-ion 10–20Ah | 2.5K–3.5K | Portable/Travel | Two battery options; harness accessible. |
| Go Chair | Pride Mobility | High Volume Portable | 1 | P | PG Drives VR2/VSI | Multi-pin (treated as 4-pin) | 2×12V SLA 18Ah | 2.0K–3.0K | Portable/Budget | Integrated controller; need detachable inline stub. |
| Jazzy Select 6 | Pride Mobility | High Volume Standard | 1 | P | PG Drives VR2/GC3 | 8-pin (map to axes) | 2×12V SLA U1 35Ah | 3.0K–5.0K | Standard/Consumer | 8-pin harness variant. |
| Jazzy 600 ES | Pride Mobility | Mid-Wheel Popular | 1 | P | PG Drives VR2 | 4/9-pin | 2×12V SLA 55Ah | 4.0K–6.0K | Mid-range | DB9 variant allows analog breakout. |
| Jazzy EVO 613 | Pride Mobility | Mid-Wheel Flagship | 1 | P | PG Drives VR2 (70A) | 3-pin charge + 4-pin ctrl | 2×12V U1 SLA 35Ah or Li-ion | 4.0K–6.0K | Mid-range | Li-ion option adds BMS; joystick unchanged. |
| Jazzy EVO 614 HD | Pride Mobility | Heavy Duty | 2 | P | Dynamic MK5/MK6i or Linx | Bus (MK) / 4-pin alt | 2×12V NF-22 SLA | 5.0K–7.0K | Heavy Duty | Bus analysis required for MK6i variant. |
| Jazzy Elite HD | Pride Mobility | Heavy Duty | 2 | R | Dynamic MK5 SPJ+ | MK bus | 2×12V SLA Group 24 | 4.5K–6.5K | Heavy Duty | Bus-level integration. |
| Jazzy 1450 | Pride Mobility | Bariatric Specialized | 2 | R | PG Drives VR2 (120A) | 4/9-pin | 2×12V Group 24 70–75Ah | 6.0K–9.0K | Heavy Duty/Bariatric | High-current but same analog signals. |
| Jazzy Air 2 | Pride Mobility | Advanced Feature | 2 | P | PG Drives VR2 | 4/9-pin + seat elev port | 2×12V U1 SLA 35–40Ah | 20K–25K | Advanced Rehab | Need seat elevation interlock mapping. |
| LiteRider Envy GP162 | Golden Technologies | High Volume Portable | 1 | P | Dynamic LiNX or VR2 | 4-pin (LiNX DX bus alt) | 2×12V SLA 22Ah | 3.0K–4.5K | Standard/Portable | Two controller families; modular harness. |
| Compass Sport | Golden Technologies | Mid Standard | 1 | P | PG Drives VR2 | 4/9-pin | 2×12V U1 SLA / optional 50Ah | 3.5K–5.0K | Standard | Widely adopted in clinics. |
| Cricket | Golden Technologies | Travel Emerging | 1 | P | PG Drives VR2 | 4-pin | 24V Li-ion 12Ah | 2.5K–3.5K | Portable/Travel | Integrated USB on joystick helpful for accessory power. |
| Aviva RX | Invacare | Rehab Mid-Range | 2 | P | Invacare LiNX (REM400) | LiNX DX bus | 2×12V 55–75Ah SLA/Gel | 4.0K–15K | Rehab | Digital bus; requires REM400 sniff module. |
| TDX SP2 | Invacare | Rehab Core | 2 | P | Invacare LiNX (REM400) | LiNX DX bus | 2×12V 55–75Ah SLA/Gel | 8.0K–18K | Premium Rehab | Same LiNX protocol family. |
| Storm Series (TDX/Power) | Invacare | Legacy / Active | 3 | R | Dynamic Shark / LiNX mix | DCI or DX bus | 2×12V SLA 55–75Ah | 4.0K–12K | Rehab | Mixed harness; evaluate ROI. |
| Extreme X8 | Magic Mobility | Premium Outdoor | 2 | R | PG Drives R-Net | DB9 analog | 2×12V Gel 70Ah | 15K–25K | Premium Outdoor | DB9 harness accessible; high torque safety mapping. |
| Frontier V6 | Magic Mobility / Sunrise | Premium Outdoor | 2 | P | PG Drives R-Net PM90 | DB9 | 2×12V Group 24/34 Gel | 15K–25K | Premium Rehab | Shared R-Net architecture. |
| Quickie Q500 M | Sunrise Medical | Premium Rehab | 1 | P | PG Drives R-Net | DB9 | 2×12V SLA/Gel 60–65Ah | 8.0K–15K | Premium Rehab | Omni modules add Bluetooth/IR; adapter sits inline DB9. |
| Quickie Q300 / Q400 / Q700 Series | Sunrise Medical | Premium Range Set | 2 | P | PG Drives R-Net | DB9 | 2×12V SLA/Gel 50–75Ah | 7.0K–18K | Premium Rehab | Consolidate harness design across series. |
| Permobil M3 Corpus | Permobil | Premium Core | 1 | P | PG Drives R-Net | DB9 + seat bus | 2×12V Gel 60–75Ah | 15K–35K | Premium Rehab | Requires seat module pass-through; well-documented signals. |
| Permobil M5 Corpus | Permobil | Premium Advanced | 2 | P | PG Drives R-Net | DB9 + seat bus | 2×12V Gel 65–75Ah | 20K–40K | Premium Rehab | Similar harness to M3; add stability for tilt/elev. |
| Permobil F5 Corpus VS | Permobil | Standing Flagship | 3 | R | PG Drives R-Net | DB9 + multi-module | 2×12V Gel 70–75Ah | 30K–55K | Advanced Standing | Complex safety interlocks; research only. |
| K450 MX (Permobil) | Permobil | Pediatric | 3 | R | PG Drives R-Net | DB9 | 2×12V Gel 55–60Ah | 15K–30K | Pediatric Rehab | Pediatric joystick gain scaling. |
| Quantum Edge 3 / Edge 3 Stretto | Quantum Rehab | Premium Mid-Wheel | 2 | P | Q-Logic 3 / NE Series | Digital bus (CAN) | 2×12V SLA NF-22 40–55Ah | 6.0K–12K | Mid/Premium Rehab | Need bus adapter board; includes standard USB. |
| Quantum 4 Front 2 | Quantum Rehab | Front-Wheel Premium | 2 | R | Q-Logic 3e | Digital bus | 2×12V Group 24 73Ah | 8.0K–15K | Mid/Premium Rehab | Similar to Edge bus; front-wheel torque mapping. |
| Robooter E60 Pro | Robooter | Tech-Enabled Portable | 2 | P | App-enabled Joystick | Armrest/Battery dual | 24V Li-ion 20–25Ah | 2.0K–4.0K | Portable/Smart | USB-C; external API (mobile). Focus BLE bridging. |
| Robooter X40 | Robooter | Emerging Smart | 2 | R | App & Remote Joystick | Armrest/Battery | 24V Ternary Li 10–20Ah | 1.8K–3.5K | Portable/Smart | BLE remote; unify with E60 harness. |
| WHILL Model C2 | WHILL | Tech Premium Portable | 2 | P | WHILL Intelligent | Proprietary battery dock | 25.3V Li-ion 10.6Ah | 4.0K–6.0K | Premium Tech | Use accessory-level integration (non-invasive). |
| WHILL Model Ci2 | WHILL | Tech Premium Portable | 2 | P | WHILL Intelligent (BT) | 5-pin proprietary + USB | 25.3V Li-ion 10.6Ah | 4.0K–6.0K | Premium Tech | Leverage phone API; avoid drive bus interference. |
| Hoveround LX-5 | Hoveround | Direct-to-Consumer | 1 | P | PG Drives VSI | 4-pin analog | 2×12V AGM 35Ah | 3.0K–5.0K | Consumer DTC | Inline stub harness; single PCB variant. |
| Merits Vision Super HD (P327) | Merits Health | Budget Heavy Duty | 1 | P | Dynamic Shark / LiNX | 4-pin DCI or DX | 2×12V 22NF SLA | 1.5K–4.0K | Budget/Import | Provide dual harness option. |
| Shoprider 6Runner 10 | Shoprider | Budget Standard | 1 | P | Dynamic Shark / VR2 compatible | 4-pin DCI | 2×12V U1 SLA 36Ah | 1.5K–4.0K | Budget/Import | DCI harness; verify pin variant. |
| ComfyGo Phoenix | ComfyGo | Import Travel | 1 | P | LCD Detachable Joystick | On-joystick XLR | 2×24V Li-ion 6.6–10Ah | 1.5K–4.0K | Budget/Import | Provide external accessory power isolation. |
| ComfyGo IQ-8000 | ComfyGo | Import Travel | 1 | P | 360° Joystick | On-joystick | 24V Li-ion 12–20Ah | 1.5K–4.0K | Budget/Import | Similar harness to Phoenix; unify SKU. |
| Featherweight Power Chair (33 lbs) | Feather Mobility | Travel Ultralight | 2 | P | Generic Joystick | XLR + direct battery | 24V Li-ion 10.4Ah | 2.0K–3.5K | Ultra-Portable | Test for axis scaling at low torque. |
| Drive Cirrus Plus HD | Drive Medical | Folding Popular | 1 | P | PG Drives VR2 | 4-pin | 2×12V U1 AGM 35Ah | 3.0K–5.0K | Standard/Folding | Quick-disconnect battery case; route harness around fold hinge. |
| Drive Titan AXS | Drive Medical | Mid Emerging | 2 | P | Dynamic LiNX | DX bus | 2×12V U1 SLA 35Ah | 3.5K–5.5K | Mid-range Standard | Bus variant; reuse LiNX toolchain. |
| Drive Trident HD | Drive Medical | Heavy Duty | 2 | P | PG Drives VR2 or LiNX | 4-pin / DX bus | 2×12V 22NF SLA 50Ah | 3.5K–5.5K | Heavy Duty | Offer dual-interface harness SKU. |
| EZ Lite Cruiser Deluxe Wide | EZ Lite Cruiser | Online Travel | 2 | P | Proprietary WS-24 | XLR | 24V Li-ion 10–15Ah | 2.5K–4.5K | Portable/Travel | Limited expansion; treat as analog axis capture only. |
| Forcemech Navigator | Forcemech | Online All-Terrain | 2 | R | Dual-Core Integrated | XLR (charge) | 2×24V Li NCM 6.6Ah (parallel) | 3.5K–5.5K | Portable/All-Terrain | Remote key fob integration (BLE) optional. |
| Pride Jazzy Passport | Pride Mobility | Travel Foldable | 1 | P | PG Drives VSI | 4-pin | 24V Li-ion ~18Ah | 2.5K–4.0K | Portable/Travel | FAA compliance; maintain battery pack isolation. |
| WHILL Model C / earlier | WHILL | Legacy Tech | 3 | R | WHILL Intelligent | Proprietary | 25V Li-ion ~10Ah | 3.5K–5.0K | Tech Portable | Consider only if demand arises (backlog). |

(Models removed from active Tier 1 consideration: very low US volume, discontinued, or highly proprietary encryption without OEM cooperation.)

## 5. Aggregate Metrics (Projected Post-Implementation)
- Tier 1 models: 24 listings (~60–65% of reachable US active user base).
- Tier 2 cumulative: +14 models (coverage ~85%).
- Tier 3 residual: Standing/pediatric/legacy (~15%).
- Connector SKUs required for Tier 1: 5 (DB9 R-Net, 4-pin VR2/Pilot+, 4-pin DCI Shark, VSI variant, Generic XLR inline stub). Tier 2 adds 3 (LiNX DX bus tap, Q-Logic bus, Proprietary battery dock adapter).

## 6. Hardware Adapter Roadmap
| Phase | Timeline (Est.) | Deliverables | Notes |
|-------|-----------------|-------------|-------|
| Alpha (A1) | Q4 2025 | Tier 1 harness prototypes; analog joystick pass-through board; safety cutoff test rig | Focus on Pride VR2 + R-Net DB9. |
| Beta (B1) | Q1 2026 | Add LiNX DX bus sniffer, Shark DCI stable harness, firmware v0.9 (axis smoothing) | Collect CAN/differential bus traces. |
| Beta (B2) | Q2 2026 | Q-Logic 3/NE integration layer; BLE accessory bridging (Robooter/WHILL API) | Abstract digital vs analog input stack. |
| Release (R1) | Q3 2026 | Production harness set (Tier 1+2), documentation portal, regulatory pre-check | IEC 60601 isolation audit. |
| Extended (X) | 2026+ | Standing & pediatric modules (F5 VS, K450 MX), seat actuator telemetry | Dependent on OEM cooperation. |

## 7. Software Integration Considerations
- Unified Input Abstraction: Map analog (voltage/hall) and digital bus commands into a normalized axis + button + mode event schema.
- Safety Envelope: Enforce max delta rate (dX/dt) and emergency neutral injection if bus error detected.
- Telemetry Channels (Phase B1+): Battery SOC (via bus or voltage curve), speed estimate (encoder or inferred from current), seating position (R-Net seat module frames), error codes.
- BLE/API Bridges (Robooter, WHILL): Non-driving control surfaces (lock/unlock, horn, light toggles) while preserving OEM safety envelope.

## 8. Risk & Mitigation Summary
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Bus protocol changes (firmware updates) | Adapter instability | Version fingerprinting; fallback to analog joystick overlay. |
| Seat module interference (R-Net, standing chairs) | Safety hazard | Transparent pass-through; non-invasive signal read only until validated. |
| Battery BMS proprietary data | Limited SOC accuracy | Voltage↔SOC estimation curves; optional user calibration cycle. |
| Regulatory compliance (FDA, IEC 60601) | Deployment delay | Early isolation design (optocouplers, galvanic DC/DC), maintain design history file. |
| User modification / hacking | Liability | Firmware signing; tamper-evident seals on harness. |

## 9. Change Log
- 2025-11-08: Major restructure; added prioritization tiers; expanded model list (Quantum Edge, Permobil F5 VS, Quickie Q-series, etc.); defined roadmap and risk matrix.

## 10. Next Actions
1. Confirm initial harness pinouts (VR2, Shark DCI, R-Net DB9) with bench oscilloscope capture.
2. Acquire sample LiNX REM400 joystick for bus analysis (non-invasive).
3. Draft electrical isolation schematic (rev A) including ESD & reverse polarity protection.
4. Populate GitHub issues for each Phase Alpha deliverable.

---

This document is iterative. Submit PRs for additions or corrections (include evidence sources where possible).