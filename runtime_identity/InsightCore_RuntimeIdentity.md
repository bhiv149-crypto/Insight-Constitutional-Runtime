9# Runtime Identity Card – InsightCore

## Runtime Participant Information

| Property | Value |
|----------|-------|
| Participant Name | InsightCore |
| Constitutional Layer | Intelligence Layer |
| Runtime Type | Constitutional Runtime Participant |
| Permanent Runtime Identity | insightcore.runtime.intelligence.v1 |
| Current Version | v1.0.2 |
| Status | 🟢 LIVE VERIFIED — Registered, Discoverable, Executable |

---

# Purpose

InsightCore is the primary intelligence execution participant responsible for providing reusable intelligence capabilities while operating as a Constitutional Runtime Participant through approved runtime contracts and execution interfaces.

---

# Authority Owned

- Intelligence capability execution
- Runtime capability participation
- Execution evidence generation
- Runtime trace contribution

---

# Authority Explicitly NOT Owned

- Runtime orchestration
- Registry management
- Replay management
- Trust verification
- Governance
- Consensus
- Identity management

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
- Runtime Execution APIs

---

# APIs Exposed

- Capability Execution Endpoint
- Runtime Health Endpoint
- Capability Metadata Endpoint

---

# Events Consumed

- Runtime Execution Events
- Capability Invocation Events
- Runtime Health Events

---

# Events Emitted

- Execution Result Events
- Runtime Trace Events
- Evidence Events

---

# SDK Attachment Contracts

- Platform Capability SDK
- Runtime Integration Interfaces

---

# Registry Participation

Registers through the Platform Service Registry and publishes runtime capabilities through the Capability Registry.

---

# Evidence Produced

- Execution Evidence
- Runtime Evidence
- Trace Evidence

---

# Replay Participation

Participates in deterministic replay using the existing Replay Registry. Canonical lineage retrieval via QCG is VERIFIED-LIVE (HTTP 200, `VALID`); local duplicate submission is separate stub behavior.

---

# Observability Model

Publishes distributed traces, metrics, structured logs, and execution telemetry through the Platform Telemetry Adapter. The current backend is a local development stub (`src/platform/stubs.py`). No live telemetry backend is configured or reachable. Methods return local dictionaries only.

---

# Knowledge Contribution

Provides reusable intelligence capabilities to the Constitutional Runtime ecosystem.

---

# Runtime Health Model

Uses the existing Heartbeat Manager for runtime health monitoring and lease management.

---

# Version Compatibility

Supports registry-managed version compatibility through the Platform Capability SDK.

---

# Production Certification Status

🟢 LIVE VERIFIED: Registration, discovery, version negotiation, SDK invocation, direct execution, health.
🔴 NOT VERIFIED: Canonical replay reconstruction.
⚪ NOT EXPOSED: Live telemetry export.
🟡 EXTERNAL DEPENDENCY: Production certification pending platform/governance requirements.