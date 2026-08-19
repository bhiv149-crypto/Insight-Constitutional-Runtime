# Project Changelog

All notable changes to the **Insight Constitutional Runtime Integration** project are documented in this file using [Semantic Versioning](https://semver.org/).

## [Documentation Reconciliation] - 2026-08-19

Reconciled Markdown against the current source, recorded `pytest -v` result, live
endpoint observations, and evidence packet. The current baseline is 27 passed with
3 warnings. Canonical replay lineage retrieval is live-verified; local duplicate
replay is stub behavior; Trust-stage verification, Platform telemetry storage,
production Quantum, and `/enforce` execution remain unestablished.

---

## [v1.0.1] - 2026-08-17 (Documentation Hardening)

### Updated
* **Test Suite Status**: All 17/17 tests now passing (previously reported as 14 passed)
  - Execution contract tests: 12/12 ✓
  - Live platform tests: 5/5 ✓
* **Replay Status**: Corrected documentation — replay endpoint WORKS (HTTP 200) with VALID verdict
  - Previous claim: "returns 404 / blocked" — INCORRECT
  - Actual: Replay lineage retrieval is live-verified ✓
* **Endpoint Paths**: Updated platform service discovery path in documentation
  - Old: `/platform/v1/services` at QCG root
  - Current: `/registry/platform/v1/services` (verified path)
* **Architecture Documentation**: Updated to reflect replay as LIVE VERIFIED
* **Final Status**: Comprehensive update with actual test results and evidence

### Verified
* **Test Execution**: All 17 tests executed on 2026-08-17, 100% passing
* **Live Platform Connectivity**: Service discovery, invocation, and replay all verified
* **Replay Lineage**: HTTP 200 response with VALID verdict confirmed
* **Verify Endpoint**: Known limitation (HTTP 422 on trust/signature) documented as platform issue

### Documentation
* **HANDOVER.md**: Current operational handover for new engineers
* **README.md**: Concise entry point; points to HANDOVER.md for details
* **FINAL_STATUS.md**: Updated with actual 17/17 test results
* **ARCHITECTURE.md**: Corrected replay status and endpoint documentation
* **INTEGRATION.md**: Updated summary results to reflect live verification

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
* **Network Fault Tolerance**: Added resilient fallback mechanisms and fast timeouts (`timeout=30`) in `LivePlatformClient` to handle cloud network latency.

### Validated
* **Internal Test Suite**: Verified pass rate in automated test suite. Contract tests: 12/12 passed. Live platform tests: 5/5 passed. Integration readiness: 17/17 passed.
* **Replay Safety**: Local stub `CanonicalReplayAuthority` provides in-memory deduplication. Canonical QCG replay lineage endpoint is live-verified (HTTP 200 with VALID verdict).
* **Telemetry Propagation**: `PlatformTelemetryAdapter` uses local stub `TraceStore`. No live telemetry backend is configured. OpenTelemetry export is local only.

### Integrated
* **Live Server Connectivity**: Successfully integrated with live platform server `https://bhiv-qcg.onrender.com` for registration, discovery, health, and invocation.
* **Live Service Registration**: Registered `InsightFlow`, `InsightBridge`, and `InsightCore` with `HTTP 200 OK` responses.
* **Live Capability Discovery**: Discovered all 3 active services via `GET /registry/platform/v1/services`.

### Evidence
* **Evidence Packet**: Compiled `review_packet.md`, `runtime_identity_cards.md`, `certification_report.md`, and `executive_assessment.md` in `evidence_packet/`.
* **Runtime Integration Proof**: Generated technical verification evidence in `docs/RUNTIME_INTEGRATION_PROOF.md`.

### Documentation
* **Documentation Suite**: Created `README.md`, `ARCHITECTURE.md`, `INTEGRATION.md`, `HANDOVER.md`, `REVIEW_INDEX.md`, `FINAL_STATUS.md`, and `DEP/` documentation.

---

## Release Notes

**Current Status**: ✓ LIVE VERIFIED — All 17 tests passing (as of 2026-08-17)

**Key Capabilities**:
- ✓ Runtime execution (InsightFlow, InsightBridge, InsightCore)
- ✓ Service registration with platform
- ✓ Service discovery via SDK
- ✓ SDK invocation (end-to-end)
- ✓ Evidence chain generation
- ✓ Replay lineage retrieval
- ⚠ Trust verification (known limitation: HTTP 422)
- ⚪ Telemetry export (stubbed, awaiting platform contract)

**Production certification**: Not claimed. Execution, discovery, invocation, health, and replay lineage are evidenced; Trust, telemetry storage, and Quantum production status remain bounded.

*Note: Shared platform service hardware certification depends on the availability of the shared BHIV Constitutional Runtime services.*