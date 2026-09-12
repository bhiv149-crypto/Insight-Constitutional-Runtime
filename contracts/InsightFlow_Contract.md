> STATUS: CONTRACT / NOT YET IMPLEMENTED
> This document describes intended behavior and is not evidence of current implementation.

# Constitutional Runtime Participant Contract – InsightFlow

## Participant Information

| Property | Value |
|----------|-------|
| Participant | InsightFlow |
| Constitutional Layer | Intelligence Layer |
| Runtime Identity | insightflow.runtime.intelligence.v1 |
| Contract Version | v1.0.2 |
| Convergence Release | Live Runtime Convergence — 2026-08-14 |

---

# Contract Purpose

InsightFlow participates in the Constitutional Runtime by orchestrating intelligence workflows through approved Platform Services and Quantum Runtime interfaces. It consumes existing runtime contracts and does not introduce parallel runtime implementations.

---

# Runtime Contracts Consumed

- Communication Contract
- Execution Contract
- Runtime Identity Contract
- Capability Manifest
- Platform Service Record

---

# Platform Services Consumed

- Platform Service Registry
- Capability Registry
- Platform Discovery Service
- Platform Capability SDK
- Runtime Core
- Replay Registry
- Observability Service
- Heartbeat Manager

---

# Capabilities Provided

- Intelligence workflow orchestration
- Runtime capability invocation
- Runtime trace generation
- Runtime evidence generation

---

# Supported Operations

| Operation | Input Contract | Output Contract |
|-----------|---------------|-----------------|
| `execute` | `{ type: "object" }` | `{ participant, runtime_identity, version, status, payload }` |
| `health` | `{ type: "object" }` | `{ participant, runtime_identity, state }` |

---

# Runtime Guarantees

- Deterministic runtime participation
- Registry-based discovery
- Replay-safe execution
- Distributed trace propagation
- Runtime health reporting
- Version compatibility through Platform SDK
- Evidence chain integrity

---

# Runtime Outputs

- Runtime traces
- Registration evidence
- Execution evidence
- Health metrics
- SDK evidence chain records

---

# Integration Constraints

- No custom runtime interfaces
- No independent replay implementation
- No direct Runtime Core modification
- Uses only approved Platform Services

---

# Certification Status

**INTEGRATED** — Live runtime integration verified 2026-08-14.

- Platform Runtime registration: 🟢 LIVE VERIFIED
- Capability discovery: 🟢 LIVE VERIFIED
- Canonical invocation (SDK + direct): 🟢 LIVE VERIFIED
- Replay lineage retrieval: 🟢 VERIFIED-LIVE — canonical lineage returns HTTP 200 with `VALID`
- Local duplicate replay submission: 🟡 VERIFIED-LOCAL — in-memory authority only
- Telemetry/observability: 🟡 VERIFIED-LOCAL — `TraceStore` stub; canonical storage not established
- Failure-path behaviour: 🟢 LIVE VERIFIED (SERVICE_NOT_FOUND, VERSION_REJECTED, INVALID_OP)
- Version negotiation: 🟢 LIVE VERIFIED

## Boundary and Limitations

- InsightFlow owns workflow execution and local execution evidence.
- Registration, discovery, invocation infrastructure, replay authority, and telemetry
	ownership remain Platform concerns delegated through adapters.
- The live endpoint `https://insight-flow-f5j4.onrender.com/health` reports
	`service: InsightBridge`; the service identity mismatch is not resolved.
- No `/enforce` request or response contract is established by the retrieved OpenAPI.