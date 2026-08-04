# InsightCore Dependency Mapping

## Component Overview

**Component:** InsightCore

**Constitutional Layer:** Intelligence Layer

**Purpose:**

Acts as the primary Intelligence Layer runtime participant responsible for contributing insight capabilities while operating through the Constitutional Runtime architecture.

---

# Upstream Dependencies

| Component | Purpose | Status |
|-----------|---------|--------|
| Platform Service Registry | Runtime registration | Identified |
| Capability Registry | Capability discovery | Identified |
| Platform Discovery Service | Service discovery | Identified |
| Platform Capability SDK | Runtime attachment | Identified |
| Runtime Core | Runtime execution | Identified |
| Replay Registry | Replay-safe execution | Identified |
| Observability | Distributed tracing | Identified |
| Heartbeat Manager | Runtime health | Identified |

---

# Runtime Contracts Consumed

- Communication Contract
- Execution Contract
- Runtime Identity
- Capability Manifest
- Platform Service Record

---

# APIs Consumed

- Platform Discovery APIs
- Capability Registry APIs
- Runtime Health APIs

---

# Events Consumed

- Runtime Execution Events
- Capability Invocation Events
- Runtime Health Events

---

# Events Emitted

- Insight Result Events
- Runtime Completion Events
- Evidence Events

---

# Evidence Produced

- Execution Evidence
- Runtime Evidence
- Trace Evidence

---

# Replay Participation

Participates through the existing Replay Registry.

---

# Runtime Health

Uses the existing Heartbeat Manager for lease renewal and runtime health monitoring.

---

# Observability

Publishes execution traces through the existing OpenTelemetry-based observability infrastructure.

---

# Notes

InsightCore integrates with the Constitutional Runtime through existing runtime contracts and does not replace Runtime Core or Platform Services.