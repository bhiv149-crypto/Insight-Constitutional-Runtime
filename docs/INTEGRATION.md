# Runtime Integration

## Purpose

This document describes how the Insight Runtime integrates with the Constitutional Runtime.

---

# Integration Philosophy

The Insight Runtime never reimplements Platform Runtime functionality.

Instead it consumes Platform Runtime interfaces through a thin adapter layer.

---

# Runtime Flow

```
Insight Participant
        │
        ▼
Registration Builder
        │
        ▼
Platform Runtime Adapters
        │
        ▼
PlatformCapabilitySDK
        │
        ▼
Platform Runtime (Live Federated Nodes)
```

---

# Platform Adapters

Implemented:

- PlatformSDKAdapter
- PlatformRegistryAdapter
- PlatformDiscoveryAdapter
- PlatformRuntimeAdapter
- PlatformReplayAdapter
- PlatformHealthAdapter
- PlatformTelemetryAdapter

---

# Runtime Validation

**Live Platform Runtime Integration Completed and Verified:**

- **Repository Readiness:** 17/17 checks passed.
- **Runtime Validation:** Completed successfully.
- **Registration Verification:** InsightFlow, InsightBridge, and InsightCore successfully registered on Node 1 and federated.
- **Discovery Validation:** Verified capability discovery via `PlatformCapabilitySDK`.
- **Replay Verification:** Verified deduplication and replay safety checks via `PlatformReplayAdapter` and `CanonicalReplayAuthority`.
- **Telemetry Verification:** Verified execution trace recording and OpenTelemetry trace continuity.

---

# Platform Runtime APIs Referenced

Operational Readiness

- GET    /health
- GET    /health/live
- GET    /health/ready
- GET    /capabilities
- POST   /verify
- POST   /gc/validate

Platform Discovery

- GET    /platform/v1/services
- POST   /platform/v1/register
- POST   /platform/v1/heartbeat
- POST   /platform/v1/negotiate
- GET    /platform/v1/federation/status
- GET    /platform/v1/services/{service_id}