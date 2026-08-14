# Runtime Identity Card – InsightBridge

## Runtime Participant Information

| Property | Value |
|----------|-------|
| Participant Name | InsightBridge |
| Constitutional Layer | Intelligence Layer |
| Runtime Type | Constitutional Runtime Participant |
| Permanent Runtime Identity | insightbridge.runtime.intelligence.v1 |
| Current Version | v1.0.2 |
| Status | 🟢 LIVE VERIFIED — Registered, Discoverable, Executable |

---

# Purpose

InsightBridge serves as the secure integration participant responsible for connecting Insight Stack capabilities with Constitutional Runtime services through approved runtime interfaces and SDKs.

---

# Authority Owned

- Runtime integration
- Capability coordination
- Runtime communication
- Integration evidence generation
- Trace propagation

---

# Authority Explicitly NOT Owned

- Runtime orchestration
- Registry management
- Runtime execution
- Replay management
- Trust verification
- Governance
- Consensus
- Identity issuance

---

# Upstream Participants

- Platform Service Registry
- Capability Registry
- Platform Discovery Service
- Platform Capability SDK
- Runtime Core
- Replay Registry
- Observability Service
- Heartbeat Manager

---

# Downstream Participants

- InsightCore
- Runtime Consumers
- Intelligence Consumers

---

# Runtime Contracts Consumed

- Communication Contract
- Execution Contract
- Runtime Identity Contract
- Capability Manifest
- Platform Service Record

---

# APIs Consumed

- Platform Discovery APIs
- Capability Registry APIs
- Runtime Health APIs

---

# APIs Exposed

- Runtime Integration Endpoint
- Runtime Health Endpoint
- Capability Metadata Endpoint

---

# Events Consumed

- Runtime Registration Events
- Capability Discovery Events
- Runtime Health Events

---

# Events Emitted

- Runtime Integration Events
- Trace Events
- Evidence Events

---

# SDK Attachment Contracts

- Platform Capability SDK
- Runtime Integration Interfaces

---

# Registry Participation

Registers through the Platform Service Registry and publishes integration capabilities through the Capability Registry.

---

# Evidence Produced

- Integration Evidence
- Registration Evidence
- Runtime Trace Evidence

---

# Replay Participation

Participates in deterministic replay through the existing Replay Registry. Canonical replay reconstruction via QCG is NOT YET VERIFIED — the lineage endpoint returns 404 and `PlatformReplayAdapter.submit()` is not implemented.

---

# Observability Model

Publishes distributed traces, metrics, and structured runtime logs through the Platform Telemetry Adapter. The current backend is a local development stub (`src/platform/stubs.py`). No live telemetry backend is configured or reachable. Methods return local dictionaries only.

---

# Knowledge Contribution

Provides standardized runtime integration capabilities for the Insight Stack.

---

# Runtime Health Model

Uses the existing Heartbeat Manager for runtime health monitoring.

---

# Version Compatibility

Managed through Platform Capability SDK compatibility negotiation.

---

# Production Certification Status

🟢 LIVE VERIFIED: Registration, discovery, version negotiation, SDK invocation, direct execution, health.
🔴 NOT VERIFIED: Canonical replay reconstruction.
⚪ NOT EXPOSED: Live telemetry export.
🟡 EXTERNAL DEPENDENCY: Production certification pending platform/governance requirements.