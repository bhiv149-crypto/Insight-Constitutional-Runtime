# Failure and Fallback Policy

## Implemented Fallbacks
- **Quantum Provider Unavailable:** Results in `FALLBACK` (Classical).
- **Live Platform Dependency Unavailable:** Handled via local stubs (e.g. `src/platform/stubs.py`).
- **Trust Validation Failure:** The system records `INVALID_SIGNATURE` at the QCG `/verify` stage.

## Unresolved Blockers
- **Live quantum provider unavailable:** BLOCKED. The execution strictly runs as `QUANTUM_LOCAL`.
- **TraceStore persistence:** Replay continuity across restarts is NOT verified; it uses an in-memory stub.
