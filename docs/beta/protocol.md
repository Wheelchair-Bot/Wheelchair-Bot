# Beta participant protocol

5 participants. 30 days. IRB-approved consent.

## Eligibility

- Rider over 18, regular user of a compatible powered wheelchair
- Caregiver / remote driver willing to participate
- Stable home network ≥ 1 Mbps up
- Willing to accept telemetry collection per [telemetry.md](telemetry.md)

## Onboarding

1. Engineer site visit: install adapter board + comma 3X + e-stop relay
2. Pair phone + browser via QR (Phase 2 auth)
3. 60-min training: tele-op interface, deadman discipline, e-stop reset
4. Supervised first session in the participant's primary indoor environment
5. Sign daily log of any tele-op session

## Daily ops

- Tele-op sessions limited to 60 min initially; extended after 14 days clean
- Mandatory weekly check-in call
- Any S0 telemetry event triggers immediate review; tele-op disabled until cleared

## Exit criteria

Beta successful if at end of 30 days for all 5 participants:
- Zero S0 incidents (no e-stop activation outside operator intent)
- ≤ 2 S1 incidents per participant (any control degradation)
- Subjective usability score ≥ 4/5 on post-study questionnaire
- No equipment damage to chair or environment

Beta fails — and ships do not move to general availability — if any of:
- Any harm to rider or third party
- Any rollover, even if no harm
- Two or more network-loss incidents within a single week
