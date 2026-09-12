# Authority Boundaries

> STATUS: CURRENT
> Last reconciled against code: 2026-09-12
> Source of truth: Current implementation + tests

**Assignment:** BHIV-QC-GANESH-01
**Date:** 2026-09-12

This document defines who owns what in the collective quantum integration. These boundaries are strict — no team member may silently absorb another member's authority.

---

## Vijay — Insight Functional Semantics

**Owns:**
- InsightFlow functional semantics and orchestration logic.
- InsightBridge classical routing and event bus logic.
- InsightCore intelligence processing semantics.
- Pydantic models and policies for the Insight Stack endpoints (`/enforce`, etc.).

**Current state:** STRUCTURALLY INTEGRATED — FUNCTIONAL SEMANTICS NOT IMPLEMENTED.

---

## Ganesh — Quantum Runtime Integration & E2E Validation

**Owns:**
- Quantum runtime integration via `MarineQuantumAdapter`.
- Provider readiness classification (`QUANTUM_LIVE`, `QUANTUM_LOCAL`, `SIMULATED`, `FALLBACK`).
- E2E Integration structural evidence and provenance.
- Platform adapter layer (`src/platform/`) — adapter contracts.
- E2E integration test suite across the boundaries.

**Does NOT own:**
- InsightFlow, InsightBridge, or InsightCore business logic / functional semantics (Vijay).
- QCG persistence (TraceStore backend) (Pritesh).
- Quantum capability contract specification (Dhiraj).
- local simulated quantum hardware deployment or credentials (Infrastructure).
- Platform SDK distribution (Kanishk).

**Current completion:** STRUCTURALLY INTEGRATED AND VERIFIED. Functional semantic limitations remain external dependencies.

---

## Pritesh — QCG Runtime Contracts, Trust & Persistence

**Owns:**
- QCG runtime contracts and canonical trust validation.
- transient replay evidence and TraceStore backend.
- Deployment and canonical execution infrastructure.
- ECDSA signature implementation and key management.

**Current state:** Trust stage is **VERIFIED** (`passed: True`). TraceStore persistence is **BLOCKED** (transient/in-memory only).

---

## Dhiraj Chavan — Quantum Capability Ownership

**Owns:**
- Quantum capability/runtime ownership.
- Quantum execution contracts (shots, seed, backend, provider, measurement provenance).
- Hybrid outputs and result normalization.
- Networking compatibility boundaries.

**Current state:** Marine Quantum Runtime runs in `QUANTUM_LOCAL` (classical deterministic). local simulated quantum hardware is **NOT YET IMPLEMENTED**.

---

## Kanishk — Collective Orchestration & SDK

**Owns:**
- Service discovery architecture.
- Platform SDK (`tantra-platform-sdk`) maintenance and distribution.
- End-to-end orchestration specifications.

**Current state:** SDK is installed and utilized. QCG discovery and invocation are verified structurally.

---

## Authority Rules (Non-Negotiable)

- **Insight** (Vijay) may define intelligence and workflows; may not govern replay.
- **Quantum Runtime** (Dhiraj) may compute; may not govern.
- **QCG** (Pritesh) may validate and execute contracts; may not manufacture quantum results.
- **Platform Integration** (Ganesh) may validate E2E flows; may not invent missing business logic or fake success.
- **No team member** may silently absorb another member's responsibility.
