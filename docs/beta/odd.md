# Operational Design Domain (ODD)

Wheelchair-Bot field beta operates **only** within this envelope.
Anything outside is unsupported and the system should refuse to
enable tele-op.

| Dimension | In-ODD | Out-of-ODD |
|-----------|--------|------------|
| Environment | Indoor; outdoor sidewalks; accessible building campuses | Public roads; vehicle lanes; rail crossings; tarmac; mines / industrial |
| Lighting | Daylight or well-lit indoor (>=200 lux) | Night without comma's IR; storm conditions |
| Weather | Dry; light drizzle OK | Heavy rain; snow; ice; standing water |
| Temperature | 0 – 40 °C ambient | Outside range |
| Speed cap | OEM chair's "indoor" profile (typ. 6 km/h) | High-speed outdoor profiles disabled in tele-op |
| Surface | Smooth concrete, indoor flooring, packed dirt | Loose gravel; deep mud; stairs (always); slopes > OEM rating |
| Battery | > 25 % | LVC engaged below 22.5 V regardless of % |
| Network | LTE or Wi-Fi ≥ 1 Mbps, ≤ 200 ms RTT | Anything else → tele-op disabled; OEM joystick only |
| Driver | Trained remote driver + present rider | Unattended tele-op |
| Chair | Permobil M3 (alpha); add Quantum + Pride per beta protocol | Anything else |

Geofencing for outdoor segments uses `liveLocationKalman` from comma.
Tele-op enable gate checks ODD on every supervised loop iteration.
