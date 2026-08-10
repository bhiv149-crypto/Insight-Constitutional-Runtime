# Project Changelog

All notable changes to the **Insight Constitutional Runtime Integration** project are documented in this file using [Semantic Versioning](https://semver.org/).

---

## [v1.0.0] - 2026-08-07

### Added
* **Participant Implementations**: Created `InsightFlowParticipant`, `InsightBridgeParticipant`, and `InsightCoreParticipant` in `src/participants/`.
* **Platform Adapter Layer**: Implemented thin platform adapters in `src/platform/` (`SDK`, `Registry`, `Discovery`, `Replay`, `Health`, `Telemetry`).
* **Integration Harness**: Built `PlatformIntegrationService`, `RegistrationBuilder`, and `LivePlatformClient` in `src/integration/`.
* **Declarative Contracts**: Created participant constitutional contracts in `contracts/` and formal identity cards in `runtime_identity/`.
* **Readiness Test Suite**: Created internal validation suite in `tests/test_integration_readiness.py`.

### Changed
* **Payload Contract Alignment**: Standardized outgoing REST payloads in `LivePlatformClient` to strictly conform with official platform schemas for `POST /v1/register` and `POST /register`.
* **Network Fault Tolerance**: Added resilient fallback mechanisms and fast timeouts (`timeout=3`) in `LivePlatformClient` to handle cloud network latency.

### Validated
* **Internal Test Suite**: Verified 100% pass rate (**12 passed**) in automated test suite.
* **Replay Safety**: Verified deduplication and replay sequence validation via `CanonicalReplayAuthority`.
* **Telemetry Propagation**: Verified execution trace recording and OpenTelemetry trace continuity.

### Integrated
* **Live Server Connectivity**: Successfully integrated with live platform server `https://bhiv-qcg.onrender.com`.
* **Live Service Registration**: Registered `InsightFlow`, `InsightBridge`, and `InsightCore` with `HTTP 200 OK` responses.
* **Live Capability Discovery**: Discovered all 3 active services via `GET /registry/capabilities/capabilities`.

### Evidence
* **Evidence Packet**: Compiled `review_packet.md`, `runtime_identity_cards.md`, `certification_report.md`, and `executive_assessment.md` in `evidence_packet/`.
* **Runtime Integration Proof**: Generated technical verification evidence in `docs/RUNTIME_INTEGRATION_PROOF.md`.

### Documentation
* **Refined Documentation Suite**: Updated `README.md`, `ARCHITECTURE.md`, `INTEGRATION.md`, `HANDOVER.md`, `REVIEW_INDEX.md`, `FINAL_STATUS.md`, and `DEP/` documentation.

---

*Note: Shared platform service hardware certification depends on the availability of the shared BHIV Constitutional Runtime services.*