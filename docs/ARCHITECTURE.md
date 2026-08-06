# Constitutional Runtime Architecture

## Overview

The Insight Runtime integrates with the Constitutional Runtime as a reusable Intelligence Layer participant.

The implementation follows a thin adapter architecture, consuming Platform Runtime services without duplicating Platform-owned infrastructure.

---

# Runtime Participants

Implemented participants:

- InsightFlow
- InsightBridge
- InsightCore

---

# Integration Architecture

```
Insight Participants
        │
        ▼
Platform Runtime Adapters
        │
        ├── PlatformSDKAdapter
        ├── PlatformRegistryAdapter
        ├── PlatformDiscoveryAdapter
        ├── PlatformReplayAdapter
        ├── PlatformHealthAdapter
        ├── PlatformTelemetryAdapter
        │
        ▼
PlatformCapabilitySDK
        │
        ▼
Platform Runtime (Live Federated Nodes)
```

---

# Runtime Responsibilities

## Insight Runtime

Responsible for:

- Intelligence execution
- Capability consumption
- Runtime participation
- Participant lifecycle
- Runtime validation

## Platform Runtime

Responsible for:

- Service discovery
- Runtime registration
- Capability registry
- Replay validation
- Runtime health
- Trace propagation
- Observability
- Trust verification
- Evidence generation

---

# Design Principles

- Consume existing Platform Runtime interfaces.
- Do not duplicate Platform infrastructure.
- Implement only Insight-owned responsibilities.
- Delegate runtime services through adapters.
- Preserve Constitutional ownership boundaries.

---

# Validation Status

**Live Federated Platform Integration Completed and Verified:**

- Repository Readiness (17/17 Passed)
- Runtime Validation (Passed)
- Live Federated Discovery node registration (InsightFlow, InsightBridge, InsightCore registered: OK)
- Live Capability Discovery via Platform Capability SDK (OK)
- Replay validation and duplication enforcement (OK)
- Observability tracing and lineage export (OK)
