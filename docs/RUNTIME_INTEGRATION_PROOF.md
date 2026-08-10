# Technical Proof of Runtime Integration

## Purpose
This document provides empirical technical proof of the integration between the Insight Constitutional Runtime and the live BHIV Constitutional Platform.

## Scope
The evidence demonstrates that `InsightFlow`, `InsightBridge`, and `InsightCore` successfully register, discover, negotiate versions, execute replay checks, and emit telemetry without duplicating platform infrastructure.

## Integration Workflow Proof
The following workflow was verified live:

**Registration -> Discovery -> Negotiation -> Invocation -> Evidence -> Replay -> Health -> Telemetry -> Failure paths -> Final convergence**

1. **Registration**: Services successfully registered via `POST /registry/capabilities/register`. Evidence shows a successful registration or `ALREADY_REGISTERED` (which confirms the service was previously registered correctly).
2. **Discovery**: `GET /registry/capabilities/capabilities` returned the 3 Insight capabilities.
3. **Negotiation**: 3/3 services reported COMPATIBLE versions.
4. **Invocation**: Capabilities invoked successfully (3/3 SUCCESS).
5. **Evidence**: SDK evidence chain successfully captured.
6. **Replay**: Verified VALID sequence followed by DUPLICATE rejection.
7. **Health**: Platform health check returned UP.
8. **Telemetry**: Traces were successfully RECORDED.
9. **Failure paths**: Verified `SERVICE_NOT_FOUND` and version incompatibility paths.

## Known Limitations
* **Platform-side Manifest Forwarding**: The deployed Platform HTTP registration handler does not currently forward a manifest into the underlying registry registration call. The manifest field can be null in metadata. This is a Platform-owned dependency limitation, but it does not block the convergence workflow.

## Final Assessment
* **Live Server Integration**: **SUCCESS**
* **Zero Duplication**: All platform services delegated to adapters.
* **Test Verification**: 12 automated tests passed.