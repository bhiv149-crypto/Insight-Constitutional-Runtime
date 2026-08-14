# InsightBridge Dependency Mapping

## Component Overview

**Component:** InsightBridge

**Constitutional Layer:** Intelligence Layer

**Purpose:**

Acts as the integration and orchestration participant that enables secure communication between the Insight Stack and the Constitutional Runtime through approved runtime interfaces.

---

# Upstream Dependencies

| Component | Purpose | Status |
|-----------|---------|--------|
| Platform Service Registry | Runtime registration | Identified |
| Capability Registry | Capability discovery | Identified |
| Platform Discovery Service | Service discovery | Identified |
| Platform Capability SDK | Runtime attachment | Identified |
| Runtime Core | Runtime participation | Identified |
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

- Runtime Registration Events
- Capability Discovery Events
- Runtime Health Events

---

# Events Emitted

- Insight Integration Events
- Runtime Invocation Events
- Integration Status Events

---

# Evidence Produced

- Runtime Registration Evidence
- Integration Evidence
- Trace Evidence

---

# Replay Participation

Participates through the existing Replay Registry.

---

# Runtime Health

Uses the existing Heartbeat Manager for lease renewal and liveness.

---

# Observability

InsightBridge uses the Platform Telemetry Adapter. The current backend is a local development stub (`src/platform/stubs.py`). No live telemetry backend is configured or reachable. OpenTelemetry export methods exist but return local dictionaries only.

---

# Notes

InsightBridge consumes existing Constitutional Runtime services and does not implement duplicate platform functionality.