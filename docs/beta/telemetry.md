# Telemetry — what we collect and why

Beta participants give informed consent for the collection of the
following data. Personally identifying information is **never**
collected by the device; PII lives only in the paired-device registry
on the server.

## Collected

| Field | Rate | Reason |
|-------|------|--------|
| `device_id` (UUID) | per session | join key |
| Wheelchair state (linear/angular velocity, battery %, motor currents) | 10 Hz | safety RCA, performance |
| Tele-op latency RTT | 1 Hz | network QoS |
| Watchdog kicks vs. expiries | event | safety |
| E-stop engagements (reason + timestamp) | event | safety |
| Adapter codec stats (frames decoded / encoded / rejected) | 1 Hz | regression detection |
| Anonymised location (~100 m grid) | 1 Hz | ODD validation |
| App / device versions | per session | OTA + bug correlation |

## Not collected

- Camera frames
- Audio
- Exact GPS coordinates
- Names, addresses, payment info
- Health information

## Storage

- Encrypted in-transit (TLS 1.3) and at-rest (S3 SSE-KMS).
- 90-day rolling retention for routine fields; **permanent** for SEV-0/1 incident snapshots.
- Aggregated, anonymised summaries published quarterly.

## Withdrawal

Participants can revoke consent at any time. On revocation:
- Device removed from registry within 24 h.
- All collected telemetry deleted within 30 days *except* SEV-0/1 incident records (legal hold).
