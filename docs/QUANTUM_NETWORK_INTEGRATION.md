# Quantum Network Integration

## Boundary Status
- **Insight Routing / Observability:** IMPLEMENTED, VERIFIED
- **Quantum-Network Integration Boundary:** NOT PROVEN
- **Provider Status:** No live quantum provider verified. The Marine Quantum Adapter uses `QUANTUM_LOCAL` fallback.

## Integration Points
The Quantum Communication Gateway (QCG) processes quantum invocations, routing them via the InsightBridge. However, the final network integration layer that links out to the live quantum nodes remains unverified. 

### `/verify` and Replay Lineage Status
- `/qcg/verify` currently returns HTTP 422 `INVALID_SIGNATURE` at the Trust stage after reaching the Replay stage. This is retained as verified Trust/authentication-failure evidence. The test does not bypass or fabricate the trust result.
- The replay objective is evaluated through the canonical replay lineage endpoint (`/qcg/replay/lineage/{invocation_id}`) using the generated `invocation_id`. Replay evidence is therefore documented independently from the Trust failure response.
