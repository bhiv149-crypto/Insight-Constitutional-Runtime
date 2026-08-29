# Quantum Runtime Architecture

## 1. Target Architecture

The target architecture for the Insight Constitutional Runtime envisions a fully integrated hybrid classical-quantum execution environment where:
1. Workloads are evaluated for quantum suitability.
2. The runtime delegates quantum operations to a live remote quantum provider (e.g., Marine Quantum Runtime) over the Quantum Communication Gateway (QCG).
3. The platform canonical Replay and Trust authorities validate the execution provenance, authenticate signatures, and store cryptographic evidence of execution.
4. The execution relies on a fully persistent platform telemetry system (TraceStore).

```text
BHIV Workload
      ↓
Workload / Suitability Decision
      ↓
Quantum / Classical Route
      ↓
Quantum Runtime / Classical Runtime
      ↓
Live Provider Execution Path
      ↓
Normalized Result
      ↓
QCG Contract Boundary
      ↓
Trust / Validation (ECDSA Verified)
      ↓
Persistent Replay / Evidence
      ↓
Insight Routing / Observability
      ↓
Quantum-Network Integration Boundary
      ↓
Provenance / Handover
```

## 2. Current Verified Runtime

The *actual* verified state of the runtime differs from the target. The current implementation relies on local execution, stubbed persistence, and a partially integrated QCG boundary that reaches the replay stage but encounters a Trust layer signature validation failure.

```text
BHIV Workload (Simulated via SDK / Tests)
      ↓
Workload / Suitability Decision (IMPLEMENTED, VERIFIED)
      ↓
Quantum / Classical Route (IMPLEMENTED, VERIFIED)
      ↓
Quantum Runtime / Classical Runtime (IMPLEMENTED, VERIFIED)
      ↓
Local Execution Path (LOCAL, QUANTUM_LOCAL) - NO LIVE PROVIDER
      ↓
Normalized Result (IMPLEMENTED, VERIFIED)
      ↓
QCG Contract Boundary (IMPLEMENTED, VERIFIED)
      ↓
Trust / Validation (BLOCKED - HTTP 422 INVALID_SIGNATURE)
      ↓
Replay / Evidence (IMPLEMENTED, TRANSIENT / LOCAL STUB)
      ↓
Insight Routing / Observability (IMPLEMENTED, VERIFIED)
      ↓
Quantum-Network Integration Boundary (NOT VERIFIED)
      ↓
Provenance / Handover (IMPLEMENTED, VERIFIED)
```

## 3. Ownership Boundaries

**Ganesh's Scope:**
* Quantum runtime integration
* Provider readiness
* Local/live execution classification
* Provider identity
* Execution provenance
* Capability discovery/health/failure exposure
* Provider attachment surface
* Quantum execution evidence

**Not Ganesh's Scope (External / Teammates):**
* QCG persistence (Pritesh)
* Quantum capability contract ownership (Dhiraj)
* Ecosystem-wide convergence (Kanishk)
* Live platform registry stability (Platform Dependency)
* Canonical TraceStore persistence (Platform Dependency)

## 4. Execution Classification

- **Quantum Execution:** `QUANTUM_LOCAL`
- **Classical Execution:** `CLASSICAL`
- **Fallback Execution:** `FALLBACK`
- **Live Platform Registration:** `LIVE VERIFIED`
- **Trust Validation:** `BLOCKED`

*Note: No live quantum provider execution was verified in this evidence set. The underlying Marine Quantum Adapter is defaulting to a local or mocked instance.*
