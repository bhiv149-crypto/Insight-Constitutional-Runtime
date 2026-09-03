# Authority Boundaries

**Assignment:** BHIV-QC-GANESH-01
**Date:** 2026-09-03

This document defines who owns what in the collective quantum integration. These boundaries are strict — no team member may silently absorb another member's authority.

---

## Ganesh — Quantum Runtime Integration & Evidence

**Owns:**
- Quantum runtime integration via `MarineQuantumAdapter`
- Provider readiness classification (`QUANTUM_LIVE`, `QUANTUM_LOCAL`, `SIMULATED`, `FALLBACK`)
- Local/live quantum execution evidence and provenance
- Platform adapter layer (`src/platform/`) — adapter contracts only
- Failure-safety verification and test suite
- E2E integration evidence generation

**Does NOT own:**
- QCG persistence (TraceStore backend)
- Trust contract implementation
- Quantum capability contract specification (Dhiraj)
- Ecosystem-wide orchestration (Kanishk)
- Live quantum hardware deployment or credentials
- Platform SDK distribution

**Current completion:** ✅ **100% COMPLETE** — all tests pass, trust verified, SDK installed

---

## Pritesh — QCG Runtime Contracts, Trust & Persistence

**Owns:**
- QCG runtime contracts and canonical trust validation
- Persistent replay evidence and TraceStore backend
- Deployment and canonical execution infrastructure
- ECDSA signature implementation and key management

**What is needed (outstanding):**
- Upgrade `TraceStore` from in-memory `deque` to a durable backend (SQLite/PostgreSQL)
- Once deployed, `Insight_Constitutional_Runtime` inherits persistence with zero code changes

**Current state:** Trust stage is **VERIFIED** (`passed: True`). TraceStore persistence is **BLOCKED** (in-memory only).

---

## Dhiraj Chavan — Quantum Capability Ownership

**Owns:**
- Quantum capability/runtime ownership
- Quantum execution contracts (shots, seed, backend, provider, measurement provenance)
- Hybrid outputs and result normalization
- Networking compatibility boundaries
- Attachment contract for quantum-network participation

**What is needed (outstanding):**
- Deliver `pip install qiskit qiskit-aer` in target environments
- Inject `IBM_QUANTUM_TOKEN` / `IONQ_API_KEY` for live hardware
- Implement the quantum-network coordination contract

**Current state:** Marine Quantum Runtime runs in `QUANTUM_LOCAL` (classical deterministic). Live quantum hardware is `BLOCKED`.

---

## Kanishk — Collective Orchestration & Ecosystem Integration

**Owns:**
- Collective runtime convergence
- Service discovery attachment
- Capability attachment through canonical invocation
- End-to-end orchestration
- Ecosystem integration and SDK distribution
- `tantra-platform-sdk` package maintenance

**What is needed (outstanding):**
- Publish updated `tantra-platform-sdk` releases to GitHub (currently at v1.0.0)
- Connect all layers (Ganesh + Pritesh + Dhiraj) into one executable hybrid runtime
- Validate end-to-end flow with evidence

**Current state:** SDK is installed from `PriteshPatra-BHIV/QCG_task1` GitHub repo. E2E convergence is `NOT PROVEN`.

---

## Authority Rules (Non-Negotiable)

- **Quantum Runtime** may compute; may not govern.
- **QCG** may validate and execute contracts; may not manufacture quantum results.
- **Insight** may route and observe; may not become replay or governance authority.
- **Quantum Network** may coordinate quantum communication; may not silently inherit execution legitimacy.
- **No team member** may silently absorb another member's responsibility. If ownership is unclear, mark it as `OWNERSHIP REQUIRES CONFIRMATION`.
