# Runtime Integration

## Purpose

This document describes how the Insight Runtime integrates with the Constitutional Runtime.

---

# Integration Philosophy

The Insight Runtime never reimplements Platform Runtime functionality.

Instead it consumes Platform Runtime interfaces through a thin adapter layer.

---

# Runtime Flow

Insight Participant

↓

Registration Builder

↓

Platform Runtime Adapters

↓

PlatformCapabilitySDK

↓

Platform Runtime

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

Completed:

- Repository Readiness
- Runtime Validation
- Registration Framework
- Discovery Framework
- Capability Invocation Framework

---

# External Dependencies

Live integration requires:

- Platform Runtime
- Runtime Registry
- Replay Registry
- TraceStore
- OpenTelemetry

---

# Platform Runtime APIs Referenced

Operational Readiness

GET    /health
GET    /health/live
GET    /health/ready
GET    /capabilities
POST   /verify
POST   /gc/validate

Platform Discovery

GET    /platform/v1/services
POST   /platform/v1/register
POST   /platform/v1/heartbeat
POST   /platform/v1/negotiate
GET    /platform/v1/federation/status
GET    /platform/v1/services/{service_id}