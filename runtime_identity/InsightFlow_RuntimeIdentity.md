# Runtime Identity Card – InsightFlow

## Runtime Participant Information

| Property | Value |
|----------|-------|
| Participant Name | InsightFlow |
| Constitutional Layer | Intelligence Layer |
| Runtime Type | Constitutional Runtime Participant |
| Permanent Runtime Identity | insightflow.runtime.intelligence.v1 |
| Current Version | v1.0.2 |
| Status | 🟢 LIVE VERIFIED — Registered, Discoverable, Executable |

---

# Purpose

InsightFlow is the primary intelligence orchestration participant responsible for initiating, coordinating, and managing insight execution workflows within the Constitutional Runtime. It integrates exclusively through approved Platform Services and Quantum Runtime interfaces without introducing parallel runtime implementations.

---

# Authority Owned

- Intelligence workflow orchestration
- Insight execution initiation
- Runtime capability invocation
- Runtime evidence contribution
- Runtime trace participation

---

# Authority Explicitly NOT Owned

- Runtime orchestration
- Capability Registry management
- Platform Service Registry management
- Runtime identity management
- Quantum Runtime execution
- Replay Registry management
- Trust verification
- Consensus management
- Platform governance

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

- InsightBridge
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
- Runtime Execution APIs (via approved interfaces)

---

# APIs Exposed

- Runtime Health Endpoint
- Capability Metadata Endpoint
- Insight Execution Endpoint

---

# Events Consumed

- Capability Discovery Events
- Runtime Registration Events
- Runtime Health Events
- Runtime Invocation Events

---

# Events Emitted

- Insight Execution Events
- Runtime Trace Events
- Evidence Events
- Runtime Health Events

---

# SDK Attachment Contracts

- Platform Capability SDK
- Platform Discovery SDK
- Runtime Integration Interfaces

---

# Registry Participation

Registers as a Constitutional Runtime Participant through the existing Platform Service Registry and publishes capability metadata through the Capability Registry.

---

# Evidence Produced

- Registration Evidence
- Execution Evidence
- Trace Evidence
- Runtime Participation Evidence

---

# Replay Participation

Participates in deterministic replay through the existing Replay Registry. Canonical replay reconstruction via QCG is NOT YET VERIFIED — the lineage endpoint returns 404 and `PlatformReplayAdapter.submit()` is not implemented.

---

# Observability Model

Publishes execution traces through the Platform Telemetry Adapter. The current backend is a local development stub (`src/platform/stubs.py`). No live telemetry backend is configured or reachable. Methods such as `record_execution_trace()` and `export_opentelemetry()` return local dictionaries only.

---

# Knowledge Contribution

Provides reusable intelligence execution capabilities to the Constitutional Runtime ecosystem.

---

# Runtime Health Model

Participates in runtime liveness, readiness, and lease management through the existing Heartbeat Manager.

---

# Version Compatibility

Supports runtime compatibility through Platform Capability SDK version negotiation and registry-managed compatibility validation.

---

# Production Certification Status

🟢 LIVE VERIFIED: Registration, discovery, version negotiation, SDK invocation, direct execution, health.
🔴 NOT VERIFIED: Canonical replay reconstruction.
⚪ NOT EXPOSED: Live telemetry export.
🟡 EXTERNAL DEPENDENCY: Production certification pending platform/governance requirements.