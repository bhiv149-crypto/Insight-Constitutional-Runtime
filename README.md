# Insight Constitutional Runtime

**Status**: Replay is live-verified; `/qcg/verify` remains halted at Trust due to `INVALID_SIGNATURE`

## Quick Summary

The **Insight Constitutional Runtime** integrates three intelligence participants (`InsightFlow`, `InsightBridge`, `InsightCore`) into the **BHIV Constitutional Platform** as reusable runtime participants. The runtime uses a thin adapter architecture to delegate platform-level operations (registration, discovery, invocation) to the canonical Platform SDK without duplicating platform infrastructure.

**What This Repo Contains**:
- ✓ Three executable intelligence participants
- ✓ Thin platform adapter layer
- ✓ Live platform integration evidence
- ✓ Replay lineage verification against the canonical QCG authority
- ✓ Full audit and evidence trail

**What This Repo Does NOT Contain**:
- ✗ The Platform Runtime itself (external service)
- ✗ Canonical Replay Authority (external service)
- ✗ Canonical Telemetry Backend (external service)
- ✗ Platform SDK source code (external dependency)

---

## Quick Start

### Prerequisites
- Python 3.10+
- Network access to `https://bhiv-qcg.onrender.com`

### Setup (5 minutes)
```bash
# Clone and navigate
git clone <repo-url>
cd Insight_Constitutional_Runtime

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install tantra-platform-sdk==1.0.0

# Run tests to verify setup
pytest -v

# Expected: 17/17 PASSED ✓
```

### Run Local Server
```bash
python insight_execution_service.py
# Runs on http://localhost:8000
# Health check: curl http://localhost:8000/api/v1/health
```

---

## Test Status

| Test Suite | Count | Status | Evidence |
|-----------|-------|--------|----------|
| Execution Contract (local) | 12 | ✓ 12/12 PASSED | `tests/test_execution_contract.py` |
| Live Platform (remote) | 5 | ✓ 5/5 PASSED | `tests/test_live_platform.py` |
| **Total** | **17** | **✓ 17/17 PASSED** | Run: `pytest -v` |

**Latest Execution**: 2026-08-17 — ~7.2 seconds

---

## Live Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Runtime Execution** | ✓ VERIFIED | InsightFlow, InsightBridge, InsightCore all executing |
| **Service Registration** | ✓ LIVE | All three services registered with platform |
| **Service Discovery** | ✓ LIVE VERIFIED | SDK successfully discovers all services |
| **SDK Invocation** | ✓ LIVE VERIFIED | Direct SDK execution working end-to-end |
| **Evidence Chain** | ✓ VERIFIED | SDK generates hash-linked evidence |
| **Replay Lineage** | ✓ LIVE VERIFIED | `/qcg/replay/lineage/{invocation_id}` returns HTTP 200 with VALID verdict |
| **Verify (Trust)** | ⚠ HALTED | `/qcg/verify` returns HTTP 422 with `INVALID_SIGNATURE` at the Trust stage |
| **Current Status** | ⚠ PARTIAL | Replay is verified; full `/verify` convergence is still blocked by the platform Trust signature issue |

---

## Known Limitations

### 1. Verify Endpoint Returns HTTP 422 (Trust Stage Halt)
The `/qcg/verify` endpoint currently returns HTTP 422 with `INVALID_SIGNATURE` at the Trust stage. The latest evidence shows Replay is already `VALID` before the Trust stage halts the overall request.

**Impact**: Direct contract verification is halted by platform-side ECDSA trust validation, while replay lineage is independently verified and returns HTTP 200 with VALID verdict.

**Current evidence**: Replay is live-verified; the overall `/verify` flow remains blocked by the Trust signature issue rather than by Replay failure.

### 2. Replay Registry is Local-Only (By Design)
The `replay_registry.json` file stores replay evidence locally for testing. In production, the canonical replay lineage is maintained by the QCG platform via `/qcg/replay/lineage/{id}` endpoint.

### 3. Telemetry Export Stubbed
The telemetry adapter returns local dictionaries. Live export to the platform's canonical telemetry backend is not yet configured (awaiting platform contract publication).

---

## Service Identity

All three participants are live and active on the platform:

| Service ID | Name | Version | Status | Endpoint |
|---|---|---|---|---|
| `insightflow.runtime.intelligence.v1` | InsightFlow Runtime Intelligence | 1.0.2 | ACTIVE | https://insight-constitutional-runtime.onrender.com/api/v1/execute |
| `insightbridge.runtime.intelligence.v1` | InsightBridge Runtime Intelligence | 1.0.2 | ACTIVE | https://insight-constitutional-runtime.onrender.com/api/v1/execute |
| `insightcore.runtime.intelligence.v1` | InsightCore Runtime Intelligence | 1.0.2 | ACTIVE | https://insight-constitutional-runtime.onrender.com/api/v1/execute |

Discover live: `GET https://bhiv-qcg.onrender.com/registry/platform/v1/services`

---

## Documentation

For complete setup, operations, troubleshooting, and integration details, see **[HANDOVER_NEW.md](HANDOVER_NEW.md)** ← Start here for detailed handover information.

Other documentation:
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — System design and component architecture
- [docs/INTEGRATION.md](docs/INTEGRATION.md) — Platform integration protocols and endpoints
- [docs/FINAL_STATUS.md](docs/FINAL_STATUS.md) — Detailed status snapshot
- [contracts/](contracts/) — Constitutional contracts for each participant
- [evidence_packet/](evidence_packet/) — Audit trail and verification evidence

---

## Common Commands

```bash
# Run all tests
pytest -v

# Run only local tests (no platform dependency)
pytest tests/test_execution_contract.py -v

# Run only live platform tests (requires https://bhiv-qcg.onrender.com connectivity)
pytest tests/test_live_platform.py -v

# Start local server
python insight_execution_service.py

# Server health check
curl http://localhost:8000/api/v1/health
```

---

## Key Endpoints

### Local Runtime (when running `python insight_execution_service.py`)
```
POST   http://localhost:8000/api/v1/execute           (Invoke a service)
GET    http://localhost:8000/api/v1/health            (Runtime health)
GET    http://localhost:8000/api/v1/services          (List services)
GET    http://localhost:8000/docs                     (Swagger UI)
```

### Live Platform (https://bhiv-qcg.onrender.com)
```
GET    /registry/platform/v1/services                 (Discover services)
GET    /registry/platform/v1/health                   (Platform health)
POST   /qcg/verify                                    (Verify invocation)
GET    /qcg/replay/lineage/{invocation_id}            (Get replay lineage)
GET    /external/docs                                 (Swagger)
```

---

## Architecture Summary

```
┌─ Insight Execution Service ──────────────────┐
│  (This Repository)                           │
│  - InsightFlow, InsightBridge, InsightCore  │
│  - Thin platform adapters                   │
│  - Local + live-integrated                  │
└───────────┬──────────────────────────────────┘
            │
    (PlatformCapabilitySDK)
            │
    ┌───────▼──────────────┐
    │ BHIV QCG Platform    │
    │ (External Service)   │
    │ - Registry           │
    │ - Discovery          │
    │ - Replay             │
    │ - Telemetry          │
    └──────────────────────┘
```

---

## Support & Troubleshooting

**Issue**: Tests fail with "SDK not installed"  
**Solution**: `pip install tantra-platform-sdk==1.0.0`

**Issue**: Live tests timeout  
**Solution**: Verify network access to `https://bhiv-qcg.onrender.com` — timeouts are transient and usually resolve on retry

**Issue**: Need detailed setup instructions?  
**Read**: [HANDOVER_NEW.md](HANDOVER_NEW.md) — Complete guide for new engineers

---

## Last Updated
**Date**: 2026-08-17  
**Test Status**: ✓ 17/17 PASSED  
**Live Platform**: ✓ VERIFIED  
**Documentation**: ✓ CURRENT

## Live Deployment

**Insight Execution Service**
- URL: `https://insight-constitutional-runtime.onrender.com`
- Provider: Render
- Platform: Render Web Service
- Version: 1.0.0
- Health: `GET /api/v1/health` → UP
- OpenAPI: `GET /openapi.json`

## Live API Endpoints

Verified from deployed OpenAPI (`https://insight-constitutional-runtime.onrender.com/openapi.json`):

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/execute` | Execute participant capability |
| `GET` | `/api/v1/health` | Aggregate health of all participants |
| `GET` | `/api/v1/health/{service_id}` | Per-service health |
| `GET` | `/api/v1/services` | List hosted services |
| `GET` | `/` | Service root info |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/openapi.json` | OpenAPI specification |

## Platform SDK Integration

The canonical `tantra-platform-sdk` (version 1.0.0) is installed and used via `PlatformSDKAdapter`.

Key SDK behaviour observed:
- `PlatformCapabilitySDK` is initialized with `discovery_urls=["https://bhiv-qcg.onrender.com/registry"]`
- `invoke_capability()` generates a UUID `invocation_id`, performs circuit-breaker check, version negotiation, manifest validation, authenticated HTTP invocation with retries, and evidence collection
- `InvocationResult` includes: `invocation_id`, `service_id`, `operation`, `status`, `response`, `duration_ms`, `trust_method`, `evidence`, `error`, `retry_count`, `timestamp`
- `SDKEvidenceChain` maintains hash-linked records with `evidence_hash` and `previous_evidence_hash`
- `evidence.verify_chain()` returns `True` for intact chains
- `head_hash` is a string property (not callable)

## QCG Discovery / Registration

### Registration
```powershell
# Runtime registration
Invoke-RestMethod -Uri "https://bhiv-qcg.onrender.com/registry/platform/v1/register" `
  -Method POST -ContentType "application/json" `
  -Body '{"service_id":"insightflow.runtime.intelligence.v1","version":"1.0.2",...}'
# → 200 OK, {"status":"REGISTERED",...}
```

### Discovery
```powershell
# List services
Invoke-RestMethod -Uri "https://bhiv-qcg.onrender.com/registry/platform/v1/services" `
  -Method GET
# → 200 OK, {"services":[...]}
```

### Capability Discovery
```powershell
# Discover specific capability
Invoke-RestMethod -Uri "https://bhiv-qcg.onrender.com/registry/capabilities/discover/insightflow" `
  -Method GET
# → 200 OK, manifest data
```

## Invocation Flow

### Direct Invocation
```powershell
$body = @{
  service_id = "insightflow.runtime.intelligence.v1"
  operation = "execute"
  payload = @{ test = $true }
  version = "1.0.2"
  invocation_id = [guid]::NewGuid().ToString()
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/execute" `
  -Method POST -ContentType "application/json" -Body $body
# → 200 OK, InvocationResult envelope
```

### SDK Invocation
```powershell
python -c "
from src.platform.sdk_adapter import PlatformSDKAdapter
sdk = PlatformSDKAdapter()
result = sdk.invoke_capability(
    service_id='insightflow.runtime.intelligence.v1',
    operation='execute',
    payload={'test': 'sdk'},
    version='1.0.2'
)
print(result.to_dict())
"
# → InvocationResult with invocation_id, evidence, etc.
```

## `invocation_id` Semantics

- The canonical identifier for a single execution attempt is `invocation_id`.
- It is generated by `PlatformCapabilitySDK.invoke_capability()` as a UUID.
- It is returned in the `InvocationResult` and echoed in the execution service response.
- It is recorded in SDK evidence chain records.
- It is NOT the same as `trace_id` (which is a locally generated telemetry identifier).
- It is NOT the same as `message_id` (which is used by the local replay stub).

## Evidence Flow

| Evidence Type | Source | Status |
|---|---|---|
| Registration evidence | QCG Platform Registry | 🟢 LIVE — `evidence_id`, `evidence_hash`, `previous_evidence_hash` returned |
| Execution evidence | Insight execution service | 🟢 LIVE — `request_hash`, `response_hash`, `invocation_id` in every response |
| SDK evidence chain | `tantra-platform-sdk` | 🟡 LOCAL VERIFIED — hash chain intact per SDK session; not cross-session persistent |
| Replay evidence | `CanonicalReplayAuthority` stub | 🟣 HISTORICAL — local in-memory deduplication only |
| Telemetry evidence | `TraceStore` stub | 🟣 HISTORICAL — local dictionaries only |

## Replay Status

**🔴 NOT VERIFIED / BLOCKED**

- `PlatformReplayAdapter` (`src/platform/replay_adapter.py`) has `lookup()`, `validate()`, `get_sequence()`, `get_verdict()` but NO `submit()` method.
- The canonical QCG replay lineage endpoint `GET /qcg/replay/lineage/{trace_id}` returns HTTP 404 for all tested IDs.
- The integration service (`_validate_replay()`) and `test_failure_cases.py` call `replay.submit()`, which raises `AttributeError`.
- Existing `evidence_packet/replay_evidence/replay_validation.json` was generated by the **local stub** `CanonicalReplayAuthority`, not the canonical QCG replay authority.

**What must exist before Replay Certification can be claimed:**
1. QCG owner exposes a canonical replay submission endpoint (POST) and lineage lookup endpoint (GET).
2. `PlatformReplayAdapter.submit()` is implemented to call the canonical endpoint.
3. `test_failure_cases.py` and `test_live_integration.py` are updated and pass against the live canonical replay authority.
4. Replay reconstruction from a live `invocation_id` is **NOT** verified end-to-end — canonical lineage endpoint returns 404 and adapter is incomplete.

## Telemetry Status

**⚪ NOT EXPOSED / LOCAL STUB ONLY**

- `src/platform/imports.py` unconditionally imports `TraceStore` from `src/platform/stubs.py`.
- `PlatformTelemetryAdapter` uses this stub `TraceStore` by default.
- `TraceStore.record_execution_trace()`, `export_opentelemetry()`, etc. return local dictionaries. They do not connect to any external system.
- No OTLP collector, Jaeger, Zipkin, or other telemetry backend is configured in environment variables or code.
- The evidence file `evidence_packet/telemetry/traces.json` shows `"status": "RECORDED"` and `"exported": true` — these are **local stub return values**, not live telemetry exports.

**What must exist before Telemetry can be claimed as live:**
1. A canonical telemetry backend owner and ingestion contract are published.
2. A participant-facing telemetry endpoint or SDK method is available.
3. `PlatformTelemetryAdapter` is updated to call the canonical backend.
4. Live trace export is verified end-to-end.

## Quantum Runtime Status

**🟡 IN PROCESS / EXTERNAL DEPENDENCY**

- Insight-side work: Participant contracts list `QuantumCommunicationGateway` (InsightBridge) and `Quantum Runtime` as dependencies.
- Platform-side work: Quantum Platform Services coordination pending with Pritesh. Quantum Runtime execution pending with Dhiraj.
- No live Quantum Runtime E2E execution has been verified in this repository.
- Quantum integration remains an external dependency.

## Current Limitations

| Limitation | Severity | Owner | Status |
|---|---|---|---|
| Replay lineage endpoint returns 404 | High | QCG / Replay owner | 🔴 BLOCKED |
| `PlatformReplayAdapter.submit()` missing | High | Insight / QCG contract | 🔴 BLOCKED |
| Telemetry backend not configured | High | Telemetry owner (TBD) | ⚪ NOT EXPOSED |
| QCG transient network timeouts | Medium | Platform (Render) | 🟡 FLAKY |
| Manifest forwarding in registration | Low | Platform team | 🟡 IN PROCESS |

## Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| `fastapi` | >=0.110.0 | Execution service framework |
| `uvicorn[standard]` | >=0.30.0 | ASGI server |
| `requests` | >=2.31.0 | HTTP client for platform communication |
| `pydantic` | >=2.0.0 | Request/response models |
| `tantra-platform-sdk` | 1.0.0 | Canonical Platform Capability SDK |

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `INSIGHT_SERVICE_URL` | Yes (for registration) | Public URL of the deployed Insight execution service |
| `PORT` | No | Server bind port (default: 8003) |
| `HOST` | No | Server bind interface (default: 0.0.0.0) |

## Installation

```powershell
# Install dependencies
pip install -r requirements.txt
```

## Local Development

```powershell
# Start execution service locally
python insight_execution_service.py
# Service binds to http://0.0.0.0:8003 by default
```

## Running Tests

```powershell
# Run pytest suite (execution contract + live platform tests)
python -m pytest tests/ -v

# Run integration readiness checks (imports/modules)
python tests/test_integration_readiness.py

# Run runtime validation
python tests/test_runtime_validation.py

# Run failure-path tests (replay duplicate will fail)
python tests/test_failure_cases.py
```

### Test Results (Verified 2026-08-14)

| Test Suite | Result | Notes |
|---|---|---|
| `test_execution_contract.py` | 12/12 passed | Contract validation for all 3 participants |
| `test_live_platform.py` | 2/2 passed (flaky) | Passes when QCG reachable; fails on ReadTimeout |
| `test_integration_readiness.py` | 17/17 passed | Import and module checks |
| `test_runtime_validation.py` | `runtime_ready = False` | `replay_validation = False` |
| `test_failure_cases.py` | FAILS | Replay duplicate raises `AttributeError` |
| `test_live_integration.py` | FAILS | Replay validation raises `AttributeError` |
| `test_production_startup.py` | Not run | Subprocess-based; requires free port |

## Live Verification

```powershell
# Verify Insight service health
Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/health" -Method GET

# Verify direct execution (InsightFlow)
$body = @{
  service_id = "insightflow.runtime.intelligence.v1"
  operation = "execute"
  payload = @{ test = $true }
  version = "1.0.2"
  invocation_id = [guid]::NewGuid().ToString()
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://insight-constitutional-runtime.onrender.com/api/v1/execute" `
  -Method POST -ContentType "application/json" -Body $body

# Verify QCG health
Invoke-RestMethod -Uri "https://bhiv-qcg.onrender.com/registry/platform/v1/health" -Method GET

# Verify SDK installation
python -c "import tantra_platform_sdk; print(tantra_platform_sdk.__version__)"

# Verify SDK evidence chain
python -c "
from src.platform.sdk_adapter import PlatformSDKAdapter
sdk = PlatformSDKAdapter()
print('Chain length:', len(sdk.sdk.evidence.get_all()))
print('Verify chain:', sdk.sdk.evidence.verify_chain())
"

# Verify replay lineage (expected: 404)
curl https://bhiv-qcg.onrender.com/qcg/replay/lineage/test-123
# → 404 {"detail":"Trace ID not found in replay registry"}
```

## Deployment

The Insight Execution Service is deployed on Render via `render.yaml`:

```yaml
services:
  - type: web
    name: insight-constitutional-runtime
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn insight_execution_service:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
      - key: INSIGHT_SERVICE_URL
        sync: false
```

`INSIGHT_SERVICE_URL` must be set to the public Render URL after first deploy.

## Reproducibility Commands

| Claim | Command | Expected Result |
|---|---|---|
| InsightFlow is live | `Invoke-RestMethod ... /api/v1/health` | HTTP 200, status UP |
| Direct execution works | `Invoke-RestMethod ... /api/v1/execute` | HTTP 200, status SUCCESS |
| SDK invocation works | `python -c "from src.platform.sdk_adapter import PlatformSDKAdapter; ..."` | `InvocationResult` with `invocation_id` |
| SDK evidence chain is valid | `python -c "sdk.sdk.evidence.verify_chain()"` | `True` |
| Replay is blocked | `curl /qcg/replay/lineage/{id}` | HTTP 404 |
| Telemetry is stub-only | `python -c "from src.platform.imports import TraceStore; ..."` | Local dictionary return |

## Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| `test_live_platform.py` timeout | QCG cold start or Render latency | Retry; QCG is reachable but transiently unstable |
| `PlatformReplayAdapter.submit()` AttributeError | Method not implemented | Wait for QCG owner to expose canonical replay endpoint |
| `TraceStore` returns local dicts | Stub backend only | Wait for telemetry owner to publish canonical backend |
| `ALREADY_REGISTERED` on registration | Service already registered at requested version | Idempotent — subsequent steps succeed |

## Evidence Classification

Every evidence artifact in `evidence_packet/` must be classified:

| Artifact | Classification | Notes |
|---|---|---|
| `api_samples/runtime_registration.json` | 🟢 LIVE VERIFIED | Generated by live `POST /registry/platform/v1/register` |
| `api_samples/discovered_services.json` | 🟢 LIVE VERIFIED | Generated by live SDK `discover_services()` |
| `invocation_proof/invocation_results.json` | 🟢 LIVE VERIFIED | Generated by live SDK invocation |
| `invocation_proof/sdk_evidence_chain.json` | 🟡 LOCAL VERIFIED | SDK session-scoped hash chain |
| `replay_evidence/replay_validation.json` | 🟣 HISTORICAL / STUB-DERIVED | Generated by local `CanonicalReplayAuthority`, not canonical QCG |
| `telemetry/traces.json` | 🟣 HISTORICAL / STUB-DERIVED | Generated by local `TraceStore`, not live backend |
| `deployment_proof/deployment_status.json` | 🟢 LIVE VERIFIED | Insight service health check |
| `registry_proof/*.json` | 🟢 LIVE VERIFIED | Generated by live QCG registry endpoints |

## Current Blockers

| Blocker | What | Where | Why | Owner | Evidence | Next Action |
|---|---|---|---|---|---|---|
| Replay reconstruction | Canonical lineage endpoint returns 404; adapter missing `submit()` | QCG `/qcg/replay/lineage/{id}` | Cannot verify canonical replay | QCG / Replay owner | HTTP 404, `AttributeError` in tests | Expose canonical endpoints; implement adapter method |
| Telemetry export | No live backend configured | `src/platform/stubs.py` → `TraceStore` | Cannot prove live trace export | Telemetry owner (TBD) | Local dict returns only | Publish canonical telemetry contract and endpoint |
| QCG network stability | ReadTimeout on registry endpoints | `bhiv-qcg.onrender.com` | Tests flaky | Platform (Render) | `test_live_platform.py` timeout | Retry / increase timeout |

## Next Actions

1. **Fix `PlatformReplayAdapter.submit()` and verify canonical replay lineage endpoint contract with QCG owner**
   - (a) Confirm canonical replay endpoint contract with QCG owner (Kanishk/MDU).
   - (b) Implement `submit()` in `PlatformReplayAdapter` to call the correct canonical endpoint.
   - (c) Update `test_failure_cases.py` and `test_live_integration.py` accordingly.

2. **Replace stub `TraceStore` with canonical telemetry adapter or verify canonical telemetry contract**
   - (a) Identify the canonical telemetry backend owner.
   - (b) Publish the participant-facing telemetry ingestion contract.
   - (c) Implement `PlatformTelemetryAdapter` to call the canonical backend, or document that telemetry is owner-controlled and out of Insight scope.

3. **Update all documentation to reflect verified state and remove unverifiable claims**
   - Align version strings to 1.0.2 across all files.
   - Remove references to non-existent files (`run_convergence.py`, `convergence_summary.json`, `proof_matrix.md`).
   - Correct test count claims.
   - Label stub-derived evidence as HISTORICAL.

## Documentation Index

| Document | Purpose |
|---|---|
| `README.md` | Engineering entry point (this file) |
| `docs/AUDIT_REPORT.md` | Complete engineering audit with verified evidence |
| `docs/FINAL_STATUS.md` | Updated proof matrix and current state |
| `docs/ARCHITECTURE.md` | System architecture with live/blocked status |
| `docs/INTEGRATION.md` | Live endpoint contracts and data flow |
| `docs/HANDOVER.md` | Operational runbook and commands |
| `docs/RUNTIME_INTEGRATION_PROOF.md` | Technical proof (corrected) |
| `docs/REVIEW_INDEX.md` | Evidence index with classifications |
| `docs/CHANGELOG.md` | Project changelog (corrected) |
| `contracts/*.md` | Participant contracts (corrected) |
| `runtime_identity/*.md` | Participant identity cards (corrected) |
| `evidence_packet/` | Evidence artifacts with classification |

## Final Project Status

**Insight Constitutional Runtime is live and verified as a Platform Runtime participant.**

🟢 LIVE VERIFIED: Registration, discovery, version negotiation, SDK invocation, direct execution, health.
🟡 LOCAL VERIFIED: SDK evidence chain integrity (session-scoped).
🔴 FAILED / BLOCKED: Canonical replay reconstruction (endpoint 404, adapter incomplete).
⚪ NOT EXPOSED: Live telemetry export (stub only).
🟡 EXTERNAL DEPENDENCY: Quantum Runtime E2E pending with Pritesh/Dhiraj.

Full ecosystem convergence and Production Certification are **not yet claimed**.
