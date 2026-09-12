> STATUS: CONTRACT / NOT YET IMPLEMENTED
> This document describes intended behavior and is not evidence of current implementation.

# Constitutional Runtime Participant Contract – InsightCore

## Participant Information

| Property | Value |
|----------|-------|
| Participant | InsightCore |
| Constitutional Layer | Intelligence Layer |
| Runtime Identity | insightcore.runtime.intelligence.v1 |
| Contract Version | v1.0.2 |
| Convergence Release | Live Runtime Convergence — 2026-08-14 |

---

# Contract Purpose

InsightCore participates in the Constitutional Runtime by providing intelligence processing, runtime analysis, and knowledge contribution within the Insight Stack. Platform concerns are delegated through the canonical Platform Runtime contracts.

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

---

# Capabilities Provided

- Intelligence processing
- Knowledge contribution
- Runtime analysis

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

- InsightCore executes inside the shared Insight Execution Service.
- Platform integration, registration, discovery, health, compatibility, and invocation
	are verified. No separate external InsightCore service is established.
- No dedicated `src/platform/insightcore_adapter.py` is required or present under the
	current architecture; no external InsightCore OpenAPI contract is available.