# Failure and Fallback Policy

**Owner:** Ganesh Vishwakarma
**Date:** 2026-09-03

This document describes how the Insight Constitutional Runtime handles failures at each layer of the integration stack.

---

## 1. Quantum Provider Failure

| Scenario | Behaviour | Classification |
|---|---|---|
| Marine Quantum Runtime unreachable (localhost:8000 down) | Adapter returns `UNAVAILABLE` status; InsightBridge falls back to classical processing | `FALLBACK` |
| Malformed quantum payload (missing/invalid circuit parameters) | Adapter validates attachment schema; rejects with `VALIDATION_ERROR` before dispatch | `LOCAL` |
| Quantum mode explicitly set to `UNAVAILABLE` | Adapter immediately returns `UNAVAILABLE` without attempting any execution | `LOCAL` |
| Live quantum provider SDK not installed | Runtime reports `CREDENTIALS_REQUIRED` / `UNAVAILABLE`; falls back to local simulator | `FALLBACK` |

**Fallback chain:** `QUANTUM_LIVE` → `QUANTUM_SIMULATED` (AerSimulator) → `QUANTUM_LOCAL` (deterministic stub) → `CLASSICAL`

The local deterministic stub (`classical_deterministic_stub`) is always available, requires no network, and uses stdlib only.

---

## 2. QCG Platform Failure

| Scenario | Behaviour | Classification |
|---|---|---|
| QCG unreachable (network / cold start) | SDK raises `requests.exceptions.Timeout`; SDK adapter catches and returns `UNREACHABLE` | `FALLBACK` |
| Service not registered / not found | SDK returns `SERVICE_NOT_FOUND` status; no crash | `LIVE` |
| Version negotiation rejected | SDK returns `DEPRECATED` or `UNSUPPORTED`; adapter surfaces this cleanly | `LIVE` |
| Trust stage failure | `/qcg/verify` returns HTTP 422; replay stage evidence remains independently valid | `LIVE` |

---

## 3. Platform SDK (`tantra_platform_sdk`) Failure

| Scenario | Behaviour | Classification |
|---|---|---|
| SDK not installed | `src/platform/imports.py` catches `ImportError`; logs error; `PlatformCapabilitySDK = None`; local stubs take over | `FALLBACK` |

**Resolution:** The official SDK is installed via:
```bash
pip install git+https://github.com/PriteshPatra-BHIV/QCG_task1.git#subdirectory=sdk
```

---

## 4. TraceStore (Telemetry) Failure

| Scenario | Behaviour | Classification |
|---|---|---|
| TraceStore in-memory stub (current state) | All telemetry is recorded in-session; evidence is lost on process restart | `LOCAL STUB` |
| Persistent backend (future, Pritesh's scope) | Once Pritesh's persistence implementation is deployed, TraceStore survives restart | `NOT PROVEN` |

---

## 5. Resolved Blockers (previously blocked, now passing)

| Item | Previous State | Current State |
|---|---|---|
| Trust stage (`/qcg/verify`) | `BLOCKED — INVALID_SIGNATURE` | **VERIFIED — `passed: True`** |
| Platform SDK import | `ImportError` | **INSTALLED — `tantra-platform-sdk==1.0.0`** |
| Local replay simulation stubs | `CanonicalReplayAuthority` faking VALID locally | **REMOVED — routes to LIVE QCG only** |

---

## 6. Unresolved Blockers (External Scope)

| Blocker | Owner | Impact |
|---|---|---|
| `TraceStore` has no persistent backend | Pritesh | Replay continuity does not survive restart |
| Live quantum SDK / API keys not available | Infrastructure / Dhiraj | Execution remains `QUANTUM_LOCAL` |
| Quantum-network coordination not implemented | Dhiraj Chavan | Quantum-network tests remain `NOT PROVEN` |
| End-to-end collective convergence not assembled | Kanishk | Full collective path is `NOT PROVEN` |
