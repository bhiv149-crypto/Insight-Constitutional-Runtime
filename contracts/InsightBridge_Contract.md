# Constitutional Runtime Participant Contract – InsightBridge

## Participant Information

| Property | Value |
|----------|-------|
| Participant | InsightBridge |
| Constitutional Layer | Intelligence Layer |
| Runtime Identity | insightbridge.runtime.intelligence.v1 |
| Contract Version | v1.0.2 |
| Convergence Release | Live Runtime Convergence — 2026-08-14 |

---

# Contract Purpose

InsightBridge participates in the Constitutional Runtime by bridging runtime communication, trace propagation, and event forwarding between the Insight Stack and the Constitutional Runtime ecosystem. Platform concerns are delegated through the canonical Platform Runtime contracts.

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
- Quantum Communication Gateway
- Replay Registry
- Observability Service

---

# Capabilities Provided

- Runtime bridge communication
- Trace propagation
- Event forwarding

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
- Bridge event evidence

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

- InsightBridge owns bridge execution and delegates Quantum requests to
	`MarineQuantumAdapter` in local mode.
- The Marine Quantum Runtime is not a production or cloud deployment in this repository.
- Live InsightBridge `POST /ingest` success is separately verified; it is not proof of
	Platform telemetry storage.
- The `/enforce` endpoint observed on the separate live service has no verified payload
	or response schema.