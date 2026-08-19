# Technical Proof of Runtime Integration

## Purpose
This document provides empirical technical proof of the integration between the Insight Constitutional Runtime and the live BHIV Constitutional Platform.

## Scope
The evidence demonstrates that `InsightFlow`, `InsightBridge`, and `InsightCore` successfully register, discover, negotiate versions, and execute via the canonical Platform SDK and direct execution endpoint. Canonical replay lineage retrieval is verified live; Platform telemetry export remains local stub behavior.

## Integration Workflow Proof
The following workflow was verified live:

**Registration -> Discovery -> Negotiation -> Invocation -> Evidence -> Execute -> Health -> Failure paths**

1. **Registration**: Services successfully registered via `POST /registry/platform/v1/register` and `POST /registry/capabilities/register`. Evidence shows `REGISTERED` or `ALREADY_REGISTERED` responses.
2. **Discovery**: `GET /registry/platform/v1/services` returned 4 services (3 Insight + 1 test). `GET /registry/capabilities/capabilities` returned the 3 Insight capabilities.
3. **Negotiation**: 3/3 services reported COMPATIBLE versions via SDK `negotiate_version()`.
4. **Invocation (SDK)**: Capabilities invoked successfully via `PlatformCapabilitySDK.invoke_capability()` — 3/3 SUCCESS, `invocation_id` returned.
5. **Invocation (direct)**: Capabilities invoked successfully via `POST /api/v1/execute` — 3/3 SUCCESS, HTTP 200.
6. **Evidence**: SDK evidence chain captured locally. Service-level evidence (request_hash, response_hash) included in every execution response.
7. **Health**: Platform health check returned UP. Insight execution service health returned UP for all 3 participants.
8. **Failure paths**: Verified `SERVICE_NOT_FOUND`, `VERSION_REJECTED`, and `INVALID_OP` paths.
9. **Replay**: `GET /qcg/replay/lineage/{invocation_id}` returns HTTP 200 with `VALID`. Local duplicate submission through `CanonicalReplayAuthority` is separate and local. `/qcg/verify` reaches Replay but halts at Trust with HTTP 422 and `INVALID_SIGNATURE`.
10. **Telemetry**: LOCAL STUB ONLY — `TraceStore` returns local dictionaries; no live backend.

## Known Limitations
* **Platform-side Manifest Forwarding**: The deployed Platform HTTP registration handler does not currently forward a manifest into the underlying registry registration call. The manifest field can be null in metadata. This is a Platform-owned dependency limitation, but it does not block the convergence workflow.
* **Replay**: Canonical lineage retrieval is live-verified. Canonical replay submission exposure is not established by the available contract. Local duplicate behavior is provided by `CanonicalReplayAuthority` and must not be described as a live canonical submission.
* **Telemetry**: No live telemetry backend is configured. `TraceStore` is a local stub.

## Final Assessment
* **Live Server Integration**: **SUCCESS** for registration, discovery, negotiation, invocation, execution, health, and replay lineage retrieval.
* **Zero Duplication**: All platform services delegated to adapters.
* **Test Verification**: The recorded pytest run is 27 passed with 3 warnings. Script-style checks under `tests/` are not all pytest-discoverable and should not be counted as pytest tests.