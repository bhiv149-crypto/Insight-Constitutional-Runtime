# Integration

## Service Registration
Service is discovered and active on the live platform registry.

- **platform_service_id:** `insightflow.runtime.intelligence.v1`
- **service_name:** `InsightFlow` (or `InsightFlow Runtime Intelligence`)
- **version:** `1.0.2`
- **status:** `ACTIVE`

## TraceStore / Telemetry Integration
The runtime currently imports `src.platform.stubs.TraceStore`. Persistent restart continuity is NOT verified. Telemetry is strictly local.
