# Engineering Handover Guide — Insight Constitutional Runtime

**Task ID:** `BHIV-QC-GANESH-01`  
**Repository:** `Insight Constitutional Runtime`  
**Owner:** Ganesh Vishwakarma — Insight Stack  
**Project:** BHIV / TANTRA Constitutional Runtime — Quantum
Convergence  
**Document Status:** FINAL HANDOVER — BOUNDED LIVE VERIFICATION  
**Last Updated:** 2026-08-21  
**Certification Level:** Operational integration verified; production
certification not claimed

------------------------------------------------------------------------

## 1. Executive Summary

The **Insight Constitutional Runtime** is an externally deployed FastAPI
runtime that integrates three Insight Stack participants into the BHIV
Constitutional Platform:

- `insightflow.runtime.intelligence.v1`
- `insightbridge.runtime.intelligence.v1`
- `insightcore.runtime.intelligence.v1`

The core platform integration lifecycle has been implemented and
exercised:

**Registration → Capability Registration → Discovery → Version
Negotiation → Invocation → Health → Replay Lineage → Evidence
Generation**

The live evidence supports working registration, discovery, version
compatibility, SDK invocation, participant health, and canonical
replay-lineage retrieval.

The runtime also contains a **local Quantum integration** through
`MarineQuantumAdapter`, connected to InsightBridge. Local Quantum
health, capability discovery, invocation, deterministic output
verification, and malformed-input handling have been exercised
successfully.

Several capabilities remain externally blocked or intentionally bounded:

- `/qcg/verify` reaches the Replay stage successfully but halts at Trust
  because of an `INVALID_SIGNATURE` ECDSA verification failure.
- Canonical Platform telemetry is not live; the current provider is a
  local `TraceStore` stub.
- Quantum execution is local only; no production/cloud Quantum endpoint
  is deployed.
- `/enforce` was discovered, but its request/response contract is
  incomplete and therefore is not claimed as integrated.
- Production certification and full ecosystem convergence are **not
  claimed**.

This handover deliberately distinguishes **live**, **local**, **stub**,
and **external/pending** capabilities.

------------------------------------------------------------------------

## 2. Project Identity and Ownership

| Property                 | Value                                                 |
|--------------------------|-------------------------------------------------------|
| Repository               | Insight Constitutional Runtime                        |
| Assignment               | `BHIV-QC-GANESH-01`                                   |
| Owner                    | Ganesh Vishwakarma — Insight Stack                    |
| Platform                 | BHIV Constitutional Platform                          |
| Platform URL             | `https://bhiv-qcg.onrender.com`                       |
| Runtime Deployment       | `https://insight-constitutional-runtime.onrender.com` |
| Framework                | FastAPI                                               |
| Main Entry Point         | `insight_execution_service.py`                        |
| Quantum Adapter          | `MarineQuantumAdapter`                                |
| Quantum Mode             | Local subprocess                                      |
| Production Certification | Not claimed                                           |

------------------------------------------------------------------------

## 3. Scope and Ownership Boundaries

### This Repository Owns

- Participant business/execution logic
- Insight execution lifecycle
- Runtime API
- Platform adapter layer
- Platform registration/discovery integration
- SDK invocation integration
- Replay lineage lookup
- Health integration
- Local Quantum delegation through InsightBridge
- Repository-side evidence generation

### This Repository Does Not Own

- BHIV Constitutional Platform runtime
- Platform registry service
- Canonical Replay Authority
- Canonical Trust/certification infrastructure
- PlatformCapabilitySDK source
- Canonical telemetry storage/backend
- Production Quantum cloud infrastructure
- Platform governance and certification approval

These boundaries explain why the remaining blockers cannot all be
resolved from this repository alone.

------------------------------------------------------------------------

## 4. Architecture

``` text
┌───────────────────────────────────────────────────────────────┐
│             Insight Constitutional Runtime                   │
│                                                               │
│  FastAPI — insight_execution_service.py                      │
│                                                               │
│  POST /api/v1/execute                                        │
│  GET  /api/v1/health                                         │
│  GET  /api/v1/health/{service_id}                            │
│  GET  /api/v1/services                                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Insight Runtime Participants                            │  │
│  │                                                         │  │
│  │ InsightFlow       v1.0.2                                │  │
│  │ InsightBridge     v1.0.2 + Quantum Gateway              │  │
│  │ InsightCore       v1.0.2                                │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │                                    │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │ Platform Adapters                                       │  │
│  │ SDK / Registry / Discovery / Replay / Health             │  │
│  │ Telemetry / Quantum / InsightFlow / InsightBridge        │  │
│  └───────────────────────┬─────────────────────────────────┘  │
└──────────────────────────┼────────────────────────────────────┘
                           │
             ┌─────────────┴──────────────┐
             ▼                            ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│ tantra-platform-sdk      │   │ BHIV QCG Platform             │
│ 1.0.0                    │   │ bhiv-qcg.onrender.com          │
└──────────────────────────┘   │ Registry / Discovery          │
                               │ Replay / Verify / Trust        │
                               └──────────────────────────────┘
```

------------------------------------------------------------------------

## 5. Participant Status

| Participant   | Version | Role                                           | Platform Status | External Service     | Quantum       |
|---------------|--------:|------------------------------------------------|-----------------|----------------------|---------------|
| InsightFlow   |   1.0.2 | Workflow orchestration and trace generation    | `VERIFIED-LIVE` | Live/reachable       | None          |
| InsightBridge |   1.0.2 | Messaging, trace propagation, event forwarding | `VERIFIED-LIVE` | Live/reachable       | Local gateway |
| InsightCore   |   1.0.2 | Deterministic state validation/intelligence    | `VERIFIED-LIVE` | No dedicated service | None          |

### InsightFlow

**Runtime identity:** `insightflow.runtime.intelligence.v1`

Configured live service:

`https://insight-flow-f5j4.onrender.com`

The endpoint is reachable and healthy. However, its health payload
reports `"service": "InsightBridge"` rather than `"InsightFlow"`.

This is retained as an **open naming inconsistency**. It is not treated
as resolved merely because the endpoint is healthy.

### InsightBridge

**Runtime identity:** `insightbridge.runtime.intelligence.v1`

Configured live service:

`https://insightbridge-phase-4-2-integration-demo.onrender.com`

Recorded health:

- `status: healthy`
- `version: 4.2`

InsightBridge is the only participant connected to the Quantum gateway.

### InsightCore

**Runtime identity:** `insightcore.runtime.intelligence.v1`

InsightCore is integrated directly through the platform integration
service. No dedicated external InsightCore service or adapter is
established in the current architecture.

**Classification:** Platform integration `VERIFIED-LIVE`; external
InsightCore service
`NOT-ESTABLISHED / NOT-REQUIRED BY CURRENT ARCHITECTURE`.

------------------------------------------------------------------------

## 6. Platform Integration Lifecycle

``` text
Registration
    ↓
Capability Registration
    ↓
Discovery
    ↓
Version Negotiation
    ↓
SDK Invocation
    ↓
Health
    ↓
Replay Lineage
    ↓
Telemetry Adapter
    ↓
Failure Paths
    ↓
Evidence Generation
```

### Registration

`POST /registry/platform/v1/register`

Observed outcomes include:

- `REGISTERED`
- `ALREADY_REGISTERED`

`ALREADY_REGISTERED` is expected idempotent behavior and is not a
registration failure.

**Evidence:** `evidence_packet/api_samples/runtime_registration.json`

### Capability Registration

`POST /registry/capabilities/register`

The three participant capabilities have been registered.

**Evidence:** `evidence_packet/api_samples/capability_registration.json`

### Discovery

`GET /registry/platform/v1/services`

The registered Insight participants are discoverable through the
platform registry.

**Evidence:** `evidence_packet/api_samples/discovered_services.json`

### Version Negotiation

`tantra-platform-sdk==1.0.0` performs version compatibility negotiation.

Recorded integration evidence indicates all three participants were
compatible.

**Classification:** `VERIFIED-LIVE`

**Evidence:** `evidence_packet/registry_proof/version_negotiation.json`

### SDK Invocation

The SDK invocation path includes circuit-breaker handling, version
negotiation, HTTP invocation/retries, and evidence-chain recording.

All three participants have been exercised through the integration
workflow.

**Classification:** `VERIFIED-LIVE`

**Evidence:** `evidence_packet/invocation_proof/invocation_results.json`

------------------------------------------------------------------------

## 7. Replay and Constitutional Verification

Replay and complete constitutional verification are separate claims.

### Canonical Replay Lineage

Endpoint:

`GET /qcg/replay/lineage/{invocation_id}`

Recorded live behavior:

- HTTP `200`
- `verdict.status = VALID`
- lineage record available
- sequence and verification metadata available

**Classification:** `VERIFIED-LIVE`

### `/qcg/verify` Trust Failure

Recorded live behavior:

``` text
HTTP 422
flow_status = HALTED

Replay:
    status = VALID

Trust:
    passed = false
    reason = ECDSA signature verification failed
```

Interpretation:

1.  Replay validation succeeds.
2.  The request reaches the Trust stage.
3.  ECDSA signature verification fails.
4.  The platform halts the verification flow.

Therefore:

**`/qcg/verify` = PARTIALLY-VERIFIED**

This is not represented as a replay failure and the HTTP 422 result must
not be hidden or suppressed.

**Evidence:**
`evidence_packet/replay_evidence/verify_replay_valid_422_trust.json`

------------------------------------------------------------------------

## 8. Quantum Integration

### Architecture

``` text
InsightBridgeParticipant
        ↓
MarineQuantumAdapter
        ↓
Marine Quantum Runtime
        ↓
Local subprocess
```

### Verified Local Behavior

The following have been exercised locally:

- Runtime health
- Capability discovery
- `quantum_pipeline`
- `signal`
- `distributed_qapp`
- `operational_monitor`
- Quantum invocation
- Deterministic hash verification
- InsightBridge delegation
- Invalid/boundary input handling

A controlled invalid-input case using `salinity=999.0` was used for
failure-path validation.

### Boundary

| Capability                         | Classification   |
|------------------------------------|------------------|
| Quantum adapter implementation     | `IMPLEMENTED`    |
| Quantum local health               | `VERIFIED-LOCAL` |
| Quantum local discovery            | `VERIFIED-LOCAL` |
| Quantum local invocation           | `VERIFIED-LOCAL` |
| InsightBridge → Quantum delegation | `VERIFIED-LOCAL` |
| Cloud Quantum execution            | `NOT-DEPLOYED`   |
| Production Quantum certification   | `NOT-CLAIMED`    |

**Evidence:** `evidence_packet/quantum_evidence/`

------------------------------------------------------------------------

## 9. Telemetry and Observability

The runtime contains a `PlatformTelemetryAdapter`, but the current
provider is:

`TraceStore`

from:

`src/platform/stubs.py`

The adapter reports Platform ownership and does not own an independent
production telemetry store.

### Current Status

The current provider is a **local stub**.

There is no evidence in the current runtime configuration of a
production:

- OTLP collector
- Jaeger backend
- Zipkin backend
- canonical Platform telemetry endpoint
- canonical production trace store

Telemetry methods currently return local dictionary-based results.

Therefore:

- Telemetry adapter: `IMPLEMENTED`
- Current provider: `STUB-DERIVED`
- Canonical live telemetry: `NOT-ESTABLISHED`
- Live OpenTelemetry export: `NOT-ESTABLISHED`

### Separate InsightBridge Ingestion

The live InsightBridge service’s `POST /ingest` endpoint has separately
been exercised successfully with:

`request_id = live-integration-test-001`

This proves that specific live ingestion endpoint accepted the test
request.

It does **not** prove that canonical BHIV Platform telemetry storage or
OpenTelemetry export is live.

------------------------------------------------------------------------

## 10. Live Deployment

| Service                          | URL                                                             | Classification                   |
|----------------------------------|-----------------------------------------------------------------|----------------------------------|
| Insight Constitutional Runtime   | `https://insight-constitutional-runtime.onrender.com`           | `VERIFIED-LIVE`                  |
| BHIV QCG Platform                | `https://bhiv-qcg.onrender.com`                                 | `VERIFIED-LIVE`                  |
| InsightFlow configured service   | `https://insight-flow-f5j4.onrender.com`                        | `VERIFIED-LIVE` + naming finding |
| InsightBridge configured service | `https://insightbridge-phase-4-2-integration-demo.onrender.com` | `VERIFIED-LIVE`                  |

### Live Health Checks

``` powershell
Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/health"

Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/health/insightflow.runtime.intelligence.v1"

Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/health/insightbridge.runtime.intelligence.v1"

Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/health/insightcore.runtime.intelligence.v1"
```

Recorded participant health:

``` text
status: UP
version: 1.0.2
state: ACTIVE
```

------------------------------------------------------------------------

## 11. Test Verification

The recorded successful verification snapshot is:

**27 passed, 3 warnings**

Warnings recorded:

- `pytest-asyncio` default fixture loop scope
- Starlette multipart import deprecation
- FastAPI `on_event` lifecycle deprecation

These are framework/deprecation warnings, not test failures.

### Important Reproducibility Note

A later documentation-audit run did not reproduce the earlier successful
27-pass snapshot because the live QCG environment was not consistently
available/registered and live tests encountered external
failures/timeouts.

Therefore the handover uses the following precise wording:

> **27 passed / 3 warnings is the recorded successful verification
> snapshot. Live-platform tests remain environment-dependent and must be
> rerun against an available, correctly registered QCG environment.**

This avoids presenting a historical successful run as a permanent
guarantee.

### Test Breakdown

| Test File                       | Tests | Environment | Purpose                          |
|---------------------------------|------:|-------------|----------------------------------|
| `test_execution_contract.py`    |    12 | Local       | Participant execution contracts  |
| `test_insightbridge_quantum.py` |     4 | Local       | InsightBridge Quantum delegation |
| `test_quantum_adapter.py`       |     6 | Local       | MarineQuantumAdapter             |
| `test_live_platform.py`         |     5 | Live        | Platform integration             |

------------------------------------------------------------------------

## 12. Live Convergence Status

| Stage                      | Result                       |
|----------------------------|------------------------------|
| Registration               | `VERIFIED-LIVE`              |
| Capability registration    | `VERIFIED-LIVE`              |
| Discovery                  | `VERIFIED-LIVE`              |
| Version negotiation        | `VERIFIED-LIVE`              |
| SDK invocation             | `VERIFIED-LIVE`              |
| Participant health         | `VERIFIED-LIVE`              |
| Replay lineage             | `VERIFIED-LIVE`              |
| `/qcg/verify` Replay stage | `VALID`                      |
| `/qcg/verify` Trust stage  | `HALTED / INVALID_SIGNATURE` |
| Canonical telemetry        | `NOT-ESTABLISHED`            |
| Quantum local execution    | `VERIFIED-LOCAL`             |
| Quantum cloud execution    | `NOT-DEPLOYED`               |
| Production certification   | `NOT-CLAIMED`                |

------------------------------------------------------------------------

## 13. Evidence Packet

The authoritative repository-side evidence location is:

``` text
evidence_packet/
```

Key areas:

``` text
evidence_packet/
├── api_samples/
├── code_packet/
├── deployment_proof/
├── invocation_proof/
├── observability_proof/
├── production_readiness/
├── quantum_evidence/
├── registry_proof/
├── replay_evidence/
├── replay_proof/
├── runtime_logs/
├── screenshots/
├── telemetry/
├── certification_report.md
├── executive_assessment.md
├── integration_map.md
├── integration_summary.json
├── review_packet.md
└── runtime_identity_cards.md
```

The evidence packet should be treated as the primary audit/evidence
location. A duplicate legacy evidence directory should not be treated as
an independent source of truth.

------------------------------------------------------------------------

## 14. Evidence Map

| Evidence                 | Location                                                             | Classification                    |
|--------------------------|----------------------------------------------------------------------|-----------------------------------|
| Runtime registration     | `evidence_packet/api_samples/runtime_registration.json`              | `VERIFIED-LIVE`                   |
| Capability registration  | `evidence_packet/api_samples/capability_registration.json`           | `VERIFIED-LIVE`                   |
| Service discovery        | `evidence_packet/api_samples/discovered_services.json`               | `VERIFIED-LIVE`                   |
| SDK invocation           | `evidence_packet/invocation_proof/invocation_results.json`           | `VERIFIED-LIVE`                   |
| SDK evidence chain       | `evidence_packet/invocation_proof/sdk_evidence_chain.json`           | `VERIFIED-LOCAL / session-scoped` |
| Failure cases            | `evidence_packet/invocation_proof/failure_cases.json`                | `VERIFIED-LIVE`                   |
| Replay lineage           | `evidence_packet/replay_evidence/replay_validation.json`             | `VERIFIED-LIVE`                   |
| Verify + Replay behavior | `evidence_packet/replay_evidence/verify_replay_valid_422_trust.json` | `VERIFIED-LIVE`                   |
| Version negotiation      | `evidence_packet/registry_proof/version_negotiation.json`            | `VERIFIED-LIVE`                   |
| Health checks            | `evidence_packet/registry_proof/health_check.json`                   | `VERIFIED-LIVE`                   |
| Telemetry traces         | `evidence_packet/telemetry/traces.json`                              | `STUB-DERIVED`                    |
| Deployment proof         | `evidence_packet/deployment_proof/`                                  | `VERIFIED-LIVE`                   |
| Quantum health           | `evidence_packet/quantum_evidence/quantum_local_health.json`         | `VERIFIED-LOCAL`                  |
| Quantum invocation       | `evidence_packet/quantum_evidence/quantum_pipeline_invocation.json`  | `VERIFIED-LOCAL`                  |
| Quantum failure          | `evidence_packet/quantum_evidence/quantum_failure_case.json`         | `VERIFIED-LOCAL`                  |
| Quantum provenance       | `evidence_packet/quantum_evidence/quantum_provenance_summary.json`   | `VERIFIED-LOCAL`                  |
| Runtime logs             | `evidence_packet/runtime_logs/`                                      | `VERIFIED-LOCAL`                  |
| Integration summary      | `evidence_packet/integration_summary.json`                           | `VERIFIED-LIVE`                   |

------------------------------------------------------------------------

## 15. Known Findings and Limitations

### 15.1 InsightFlow Health Identity

`https://insight-flow-f5j4.onrender.com/health` reports
`"service": "InsightBridge"`.

The endpoint is reachable and healthy, but the returned identity does
not match the configured InsightFlow identity.

**Classification:** `PARTIALLY-VERIFIED`

**Action:** Confirm with the live service owner.

### 15.2 `/enforce` Contract

The live OpenAPI exposes `/enforce` and indicates Bearer authentication.

Verified:

- Endpoint exists
- Bearer authentication is required

Not verified:

- Request body schema
- Response schema
- Successful enforcement execution

**Classification:** `PENDING-CONTRACT`

The runtime must not invent or assume an undocumented payload contract.

### 15.3 Canonical Telemetry

The telemetry adapter exists, but the current provider is a local stub.

**Classification:** `IMPLEMENTED-NOT-LIVE`

### 15.4 Quantum

Marine Quantum Runtime is local only.

**Classification:** `VERIFIED-LOCAL`

### 15.5 QCG Trust

Replay is valid, but `/qcg/verify` halts at Trust because of ECDSA
signature verification failure.

**Classification:** `PARTIALLY-VERIFIED`

### 15.6 SDK Evidence Persistence

SDK evidence-chain state is session-scoped and should not be represented
as persistent cross-session storage.

------------------------------------------------------------------------

## 16. Current Status Matrix

| Area                     | Implementation | Runtime Status | Environment | Evidence           | Boundary                     |
|--------------------------|----------------|----------------|-------------|--------------------|------------------------------|
| InsightFlow              | Verified       | UP/ACTIVE      | Live        | Health/invocation  | Naming inconsistency         |
| InsightBridge            | Verified       | UP/ACTIVE      | Live        | Health/invocation  | None identified              |
| InsightCore              | Verified       | UP/ACTIVE      | Live        | Health/invocation  | No external service          |
| Registration             | Verified       | Registered     | Live        | Registry proof     | Platform-owned               |
| Discovery                | Verified       | Active         | Live        | Discovery proof    | Cloud latency possible       |
| Version negotiation      | Verified       | Compatible     | Live        | Registry proof     | None identified              |
| SDK invocation           | Verified       | Success        | Live        | Invocation proof   | None identified              |
| Replay lineage           | Verified       | Valid          | Live        | Replay proof       | None identified              |
| `/qcg/verify` Replay     | Verified       | Valid          | Live        | Verify evidence    | Trust remains                |
| `/qcg/verify` Trust      | Not verified   | Halted         | Live        | HTTP 422 evidence  | ECDSA failure                |
| Telemetry adapter        | Implemented    | Stub           | Local       | Telemetry evidence | Backend unavailable          |
| Quantum adapter          | Implemented    | Operational    | Local       | Quantum evidence   | No cloud deployment          |
| `/enforce`               | Discovered     | Unknown        | Partial     | OpenAPI evidence   | Contract unavailable         |
| Deployment               | Verified       | Up             | Live        | Deployment proof   | None identified              |
| Production certification | Not claimed    | —              | —           | —                  | Governance/platform approval |

------------------------------------------------------------------------

## 17. Remaining External Blockers

### Blocker 1 — QCG ECDSA Trust Verification

**Owner:** QCG / Platform team

Required:

- Resolve ECDSA signature verification failure.
- Re-run `/qcg/verify`.
- Confirm Trust stage passes.
- Capture updated evidence.

**Impact:** Complete constitutional verification convergence.

### Blocker 2 — Canonical Platform Telemetry

**Owner:** Platform team

Required:

- Publish telemetry ingestion contract.
- Provide live endpoint/provider.
- Establish OpenTelemetry export.
- Replace/connect the current stub-backed provider.
- Capture live trace evidence.

**Impact:** Live canonical observability verification.

### Blocker 3 — Manifest Forwarding

**Owner:** Platform team

The observed platform registration handler does not forward the manifest
field.

Registration itself succeeds, so this is primarily a metadata
completeness issue.

### Blocker 4 — InsightFlow Service Identity

**Owner:** InsightFlow/live service owner

Confirm why the configured InsightFlow endpoint reports
`"InsightBridge"`.

**Impact:** Service identity/documentation clarity.

### Blocker 5 — `/enforce` Contract

**Owner:** Relevant service/platform owner

Required:

- Request schema
- Response schema
- Authentication expectations
- Successful execution example

**Impact:** Responsible enforcement integration.

------------------------------------------------------------------------

## 18. Paused Work

### Quantum Cloud Deployment

Production/cloud Quantum deployment is paused.

Current evidence is limited to local Marine Quantum Runtime execution.

### Production Certification

Production certification is not claimed and remains dependent on
external platform, security, governance, and verification requirements.

------------------------------------------------------------------------

## 19. What Is Implemented

The repository currently contains:

- Three platform-integrated Insight participants
- FastAPI execution service
- Platform registration integration
- Capability registration workflow
- Discovery adapter
- SDK invocation integration
- Health adapter
- Replay adapter
- Telemetry adapter boundary
- InsightFlow live adapter
- InsightBridge live adapter
- Marine Quantum adapter
- Local Quantum verification
- Failure-path handling
- Replay lineage evidence
- Runtime/evidence generation
- Deployment configuration
- Local and live integration tests
- Evidence packet
- Handover documentation

------------------------------------------------------------------------

## 20. What Is Not Established

The following must remain explicitly unclaimed:

- Canonical production telemetry storage
- Live OpenTelemetry export
- Production/cloud Quantum execution
- Successful QCG Trust-stage verification
- Fully specified `/enforce` integration
- External InsightCore service
- Production certification
- Full ecosystem-wide constitutional convergence

------------------------------------------------------------------------

## 21. Reproduction Guide

### Prerequisites

- Python 3.10+
- Tested with Python 3.12.x
- pip
- Network access to BHIV QCG Platform

### Setup

``` powershell
git clone <repo-url>
cd Insight_Constitutional_Runtime

python -m venv venv
venv\Scriptsctivate

pip install -r requirements.txt
pip install tantra-platform-sdk==1.0.0

python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"
```

### Run Tests

``` powershell
pytest -v
```

Live-platform tests depend on current external QCG availability and
registration state.

### Start Runtime Locally

``` powershell
python insight_execution_service.py
```

Default:

``` text
http://0.0.0.0:8003
```

### Environment Variables

| Variable              | Required             | Purpose                           |
|-----------------------|----------------------|-----------------------------------|
| `INSIGHT_SERVICE_URL` | Yes for registration | Public runtime URL                |
| `PORT`                | No                   | Runtime port; default `8003`      |
| `HOST`                | No                   | Bind interface; default `0.0.0.0` |

------------------------------------------------------------------------

## 22. Live Invocation Example

``` powershell
$body = @{
  service_id = "insightflow.runtime.intelligence.v1"
  operation = "execute"
  payload = @{ test = $true }
  version = "1.0.2"
  invocation_id = [guid]::NewGuid().ToString()
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/execute" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Replay Example

``` powershell
$invocation_id = "<live-invocation-id>"

Invoke-RestMethod `
  -Uri "https://bhiv-qcg.onrender.com/qcg/replay/lineage/$invocation_id"
```

Expected recorded behavior:

``` text
HTTP 200
verdict.status = VALID
lineage_record = available
```

### Telemetry Stub Example

``` powershell
python -c "
from src.platform.imports import TraceStore
ts = TraceStore()
result = ts.record_execution_trace(
    trace_id='t1',
    participant='InsightFlow',
    operation='execute'
)
print(result)
"
```

This verifies only the local telemetry stub.

### Quantum Local Example

``` powershell
python -c "
from src.platform.quantum_adapter import MarineQuantumAdapter
q = MarineQuantumAdapter()
print('Mode:', q.mode)
print('Health:', q.health())
"
```

Expected:

``` text
Mode: local
Health: HEALTHY
```

------------------------------------------------------------------------

## 23. Repository Structure

``` text
.
├── insight_execution_service.py
├── requirements.txt
├── render.yaml
├── replay_registry.json
│
├── src/
│   ├── common/
│   ├── participants/
│   │   ├── insightflow/
│   │   ├── insightbridge/
│   │   └── insightcore/
│   ├── integration/
│   ├── config/
│   └── platform/
│
├── tests/
│   ├── test_execution_contract.py
│   ├── test_insightbridge_quantum.py
│   ├── test_quantum_adapter.py
│   ├── test_live_platform.py
│   └── additional integration/readiness tests
│
├── contracts/
├── runtime_identity/
├── dependency_mapping/
├── docs/
├── evidence_packet/
└── integration_doc/
```

------------------------------------------------------------------------

## 24. Safe Change Boundaries

### Safe to Change

- Participant business logic while preserving platform contracts
- Environment configuration
- Documentation
- Regenerated evidence from valid verification runs
- Tests when they reflect an actual contract change

### Change Only With Full Contract Awareness

- Service IDs
- Runtime versions
- Platform adapter interfaces
- SDK invocation behavior
- Execution API schema
- Registry payloads
- Replay/trust handling
- Evidence classification

Changing platform-facing identifiers or contracts can invalidate
existing registration, discovery, invocation, and evidence records.

------------------------------------------------------------------------

## 25. Status Vocabulary

| Classification         | Meaning                                                    |
|------------------------|------------------------------------------------------------|
| `VERIFIED-LIVE`        | Directly exercised against a live deployed service         |
| `VERIFIED-LOCAL`       | Directly exercised locally                                 |
| `VERIFIED-MOCK`        | Verified through a mock/stub environment                   |
| `IMPLEMENTED-NOT-LIVE` | Code exists but required live deployment/backend is absent |
| `PARTIALLY-VERIFIED`   | Some required stages verified; another remains unresolved  |
| `PENDING-CONTRACT`     | External contract is incomplete                            |
| `PAUSED`               | Intentionally deferred                                     |
| `NOT-IMPLEMENTED`      | Capability is not implemented                              |
| `NOT-APPLICABLE`       | Outside current architecture/scope                         |
| `NOT-CLAIMED`          | No production/certification claim is being made            |

------------------------------------------------------------------------

## 26. Final Certification Position

### Verified Live

The evidence supports:

- Runtime deployment reachability
- Three Insight participants integrated into the platform-facing runtime
- Registration
- Capability registration
- Discovery
- Version compatibility
- SDK invocation
- Participant health
- Canonical replay lineage retrieval
- Failure-path exercise
- Repository-side evidence generation

### Verified Local

The evidence supports:

- Marine Quantum Runtime health
- Quantum capability discovery
- Quantum pipeline invocation
- Deterministic Quantum verification
- InsightBridge-to-Quantum delegation
- Quantum invalid-input handling
- Local telemetry stub behavior

### Partially Verified

- `/qcg/verify`: Replay passes; Trust fails with `INVALID_SIGNATURE`
- InsightFlow external service identity: endpoint healthy, identity
  inconsistent
- `/enforce`: endpoint discovered/authenticated, contract incomplete

### Not Established

- Canonical production telemetry backend
- Live OpenTelemetry export
- Cloud/production Quantum execution
- Successful QCG Trust-stage verification
- Fully specified `/enforce` integration
- External InsightCore service

### Not Claimed

- Production certification
- Full ecosystem constitutional convergence
- Production Quantum certification
- Production-grade canonical telemetry certification

------------------------------------------------------------------------

## 27. Final Handover Statement

The **Insight Constitutional Runtime** is an **operationally integrated
BHIV Constitutional Platform participant with bounded live
verification**.

The repository has completed the implementation and verification work
within its current scope. Live evidence demonstrates working platform
registration, discovery, version compatibility, SDK invocation,
participant health, and canonical replay lineage retrieval.

The remaining gaps are explicitly bounded and primarily depend on
external platform/service owners:

1.  QCG ECDSA Trust verification
2.  Canonical Platform telemetry/OpenTelemetry backend
3.  Manifest forwarding behavior
4.  InsightFlow service identity clarification
5.  `/enforce` contract publication
6.  Optional future Quantum cloud deployment
7.  External production/certification governance

### Final Status

> **LIVE AND INTEGRATED — BOUNDED VERIFICATION COMPLETE; EXTERNAL
> CERTIFICATION BLOCKERS REMAIN.**

This statement intentionally does **not** claim full certification,
production Quantum, canonical live telemetry, or complete ecosystem-wide
constitutional convergence.

------------------------------------------------------------------------

## 28. Submission Checklist

- [x] Runtime implementation completed
- [x] Platform integration implemented
- [x] Live deployment available
- [x] Registration evidence captured
- [x] Capability registration evidence captured
- [x] Discovery evidence captured
- [x] Invocation evidence captured
- [x] Health evidence captured
- [x] Replay lineage evidence captured
- [x] Quantum local evidence captured
- [x] Failure evidence captured
- [x] Telemetry limitations documented
- [x] `/qcg/verify` Trust failure documented honestly
- [x] `/enforce` limitation documented
- [x] InsightFlow naming inconsistency documented
- [x] Production certification explicitly not claimed
- [x] Evidence packet organized as the primary evidence location
- [x] Final handover documentation prepared

------------------------------------------------------------------------

**Document Status:** FINAL  
**Last Updated:** 2026-08-21  
**Live Runtime:** `VERIFIED-LIVE`  
**Replay Lineage:** `VERIFIED-LIVE`  
**Quantum:** `VERIFIED-LOCAL`  
**Canonical Telemetry:** `NOT-ESTABLISHED`  
**QCG Trust:** `PARTIALLY-VERIFIED — INVALID_SIGNATURE`  
**Production Certification:** `NOT-CLAIMED`
