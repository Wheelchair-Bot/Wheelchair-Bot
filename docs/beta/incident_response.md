# Incident response playbook

If anything unexpected happens during a tele-op session.

## Severities

| Sev | Definition | Notify within | Engineering response |
|-----|------------|---------------|----------------------|
| **SEV-0** | Harm to person or property; rollover; injury | 15 min | All-hands; suspend all beta sessions until RCA |
| **SEV-1** | Loss of control without harm; unexpected e-stop; wrong direction | 1 hour | On-call engineer; affected participant pauses until RCA |
| **SEV-2** | Degraded service; high latency; battery scare; UI bug | next business day | Standard issue triage |
| **SEV-3** | Cosmetic; minor confusion | weekly review | Backlog |

## SEV-0 / SEV-1 sequence

1. **Rider safety first.** If on, OEM joystick takes over. Power down chair if needed.
2. Page on-call via PagerDuty / phone (per the duty roster).
3. Engineer pulls device telemetry within 15 min (`telemetry/incident_pull.py <device_id> --since-30m`).
4. Open incident issue in `Wheelchair-Bot/field-incidents` GitHub project; link telemetry.
5. Suspend tele-op for affected participant via remote disable flag.
6. RCA within 5 business days. Postmortem doc per `engineering:incident-response` template.
7. Resolution gate: regression test added + HIL test added + safety review sign-off.

## Reporting obligations

- SEV-0: regulatory consultant within 24 h; post-market surveillance log
- SEV-0 with harm: FDA MedWatch (US) / MHRA Yellow Card (UK) within statutory window
- All SEVs: included in monthly safety report
