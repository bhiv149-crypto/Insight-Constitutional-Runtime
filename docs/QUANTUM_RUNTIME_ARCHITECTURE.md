> STATUS: CURRENT
> Last reconciled against code: 2026-09-12
> Source of truth: Current implementation + tests

# Quantum Runtime Architecture

**Owner:** Ganesh Vishwakarma
**Assignment:** BHIV-QC-GANESH-01
**Date:** 2026-09-03

---

## 1. Target Architecture

The target architecture for the Insight Constitutional Runtime envisions a fully integrated hybrid classical-quantum execution environment where:

1. Workloads are evaluated for quantum suitability.
2. The runtime delegates quantum operations to a live remote quantum provider over the QCG.
3. The platform canonical Replay and Trust authorities validate execution provenance, authenticate signatures, and store cryptographic evidence.
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
Live Provider Execution Path (IBM Quantum / IonQ / Aer)
      ↓
Normalized Result
      ↓
QCG Contract Boundary
      ↓
Trust / Validation (ECDSA Verified) ✓
      ↓
Persistent Replay / Evidence (durable TraceStore)
      ↓
Insight Routing / Observability
      ↓
Quantum-Network Integration Boundary
      ↓
Provenance / Handover
```

---

## 2. Current Verified Runtime State

```text
BHIV Workload (via SDK / Tests)
      ↓
Workload / Suitability Decision           [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
Quantum / Classical Route                 [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
Quantum Runtime / Classical Runtime       [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
Local Execution Path                      [QUANTUM_LOCAL — classical deterministic sim]
      ↓                                   [local simulated quantum PROVIDER — BLOCKED, no credentials]
Normalized Result                         [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
QCG Contract Boundary                     [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
Trust / Validation                        [LIVE VERIFIED — passed: True]
      ↓
Replay / Evidence                         [LIVE VERIFIED — /qcg/replay/lineage → VALID]
      |                                   [LOCAL STUB — TraceStore transient only]
      ↓
Insight Routing / Observability           [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
      ↓
Quantum-Network Integration Boundary      [BOUNDED CONTRACT ONLY — NOT VERIFIED LIVE]
      ↓
Provenance / Handover                     [STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED]
```

---

## 3. Ownership Boundaries

**Ganesh's Scope (Complete):**
- Quantum runtime integration via `MarineQuantumAdapter`
- Provider readiness and classification
- Local/live execution classification (`QUANTUM_LOCAL`, `SIMULATED`, `FALLBACK`)
- Provider identity and attachment surface
- Execution provenance and evidence generation
- Capability discovery, health, failure exposure
- Platform adapter layer (`src/platform/`)

**External Scope (Not Ganesh's):**

| Component | Owner | Notes |
|---|---|---|
| Canonical TraceStore persistence | Pritesh | In-memory stub; needs durable backend |
| QCG trust contracts and deployment | Pritesh | Trust is now passing; persistence is next |
| Quantum capability contracts | Dhiraj Chavan | Hardware SDK, normalization, uncertainty |
| local simulated quantum SDK credentials | Infrastructure | `IBM_QUANTUM_TOKEN`, `IONQ_API_KEY` |
| Quantum network coordination | Dhiraj Chavan | Network contract; not live |
| Collective ecosystem convergence | Kanishk | End-to-end orchestration |

---

## 4. Execution Classification Reference

| Classification | Meaning | Current Example |
|---|---|---|
| `QUANTUM_LIVE` | Real quantum hardware via cloud API | **BLOCKED** — no credentials |
| `QUANTUM_SIMULATED` | Qiskit AerSimulator (local) | **BLOCKED** — `qiskit-aer` not installed |
| `QUANTUM_LOCAL` | Deterministic classical stub (seeds) | **ACTIVE** — Marine Quantum Runtime default |
| `CLASSICAL` | Standard execution path | **ACTIVE** — InsightFlow / InsightCore |
| `FALLBACK` | Degraded path due to provider failure | **ACTIVE** — when quantum unreachable |

---

## 5. Key File Map

| File | Role |
|---|---|
| `src/platform/quantum_adapter.py` | MarineQuantumAdapter — HTTP client to Marine runtime |
| `src/platform/replay_adapter.py` | Live QCG replay and verify adapter |
| `src/platform/sdk_adapter.py` | PlatformSDKAdapter — wraps tantra-platform-sdk |
| `src/platform/telemetry_adapter.py` | PlatformTelemetryAdapter — routes to TraceStore |
| `src/platform/stubs.py` | Development stubs (TraceStore, CapabilityManifest, etc.) |
| `src/platform/imports.py` | Canonical SDK import with graceful fallback |
| `src/participants/insightbridge/participant.py` | Quantum gateway routing in InsightBridge |
| `tests/test_quantum_adapter.py` | 6 real HTTP tests against Marine runtime |
| `tests/test_live_platform.py` | 5 live QCG integration tests |
