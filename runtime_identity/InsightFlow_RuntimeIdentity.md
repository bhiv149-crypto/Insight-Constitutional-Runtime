# Runtime Identity Card – InsightFlow

## Runtime Participant Information

| Property | Value |
|----------|-------|
| Participant Name | InsightFlow |
| Constitutional Layer | Intelligence Layer |
| Runtime Type | Constitutional Runtime Participant |
| Permanent Runtime Identity | insightflow.runtime.intelligence.v1 |
| Current Version | v1.0.0 |
| Status |Implemented – Pending External Runtime Validation|

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

Participates in deterministic replay through the existing Replay Registry without implementing independent replay functionality.

---

# Observability Model

Publishes distributed traces, runtime metrics, execution logs, and correlation identifiers through the existing OpenTelemetry-based observability infrastructure.

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

Repository implementation completed.

Pending:

- Platform Runtime deployment
- Runtime validation against live services
- Production certification