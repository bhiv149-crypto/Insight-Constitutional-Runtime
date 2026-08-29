# Handover Guide: Insight Constitutional Runtime

## 1. Executive Summary

The Insight Constitutional Runtime integrates three Insight Stack participants into the BHIV Constitutional Platform. The repository is in a **verified, test-passing state** (27/27 tests pass, 3 warnings). Quantum execution is verified locally through the Marine Quantum Runtime and is classified as `QUANTUM_LOCAL`. The underlying mechanism is a classical deterministic simulation — no quantum hardware or live cloud quantum provider is operational.

**Current verified state**: Live platform integration works; quantum execution is local classical simulation; replay lineage is independently verified; Trust-stage verification halts with `INVALID_SIGNATURE` (platform-level ECDSA issue).

---

## 2. Current Verified State

| Capability                       | Classification | Evidence Location | Limitation |
|----------------------------------|----------------|-------------------|------------|
| Participant execution            | `LOCAL`        | `tests/test_execution_contract.py` | 12/12 pass; no quantum involved |
| Platform registration            | `LIVE`         | `evidence_packet/api_samples/runtime_registration.json` | `ALREADY_REGISTERED` is idempotent |
| Capability discovery             | `LIVE`         | `evidence_packet/api_samples/discovered_services.json` | Transient QCG cold-start timeouts possible |
| SDK invocation                   | `LIVE`         | `evidence_packet/invocation_proof/invocation_results.json` | Requires QCG reachability |
| Health                           | `LIVE`         | `evidence_packet/registry_proof/health_check.json` | Application liveness only |
| Replay lineage                   | `LIVE`         | `evidence_packet/replay_evidence/replay_validation.json` | Verified for available invocation IDs |
| `/qcg/verify`                    | `PARTIAL`      | `evidence_packet/replay_evidence/verify_replay_valid_422_trust.json` | Trust stage returns HTTP 422 `INVALID_SIGNATURE` |
| Quantum execution                | `LOCAL`        | `evidence_packet/quantum_evidence/quantum_pipeline_invocation.json` | Classical deterministic simulation; no quantum hardware |
| Telemetry                        | `LOCAL`        | `evidence_packet/telemetry/traces.json` | `TraceStore` stub; no live backend |
| Persistent replay across restart | `NOT PROVEN`   | N/A               | `TraceStore` and `CanonicalReplayAuthority` are in-memory stubs |
| Quantum-network execution        | `NOT PROVEN`   | N/A               | Bounded contract only; no live execution path |
| Classical fallback               | `FALLBACK`     | `marine_quantum_runtime/src/quantum/providers/local_simulator_provider.py` | Always available; stdlib-only |
| Production certification         | `NOT CLAIMED`  | N/A               | Depends on external platform/governance requirements |

---

## 3. What Was Completed

### Insight Runtime Integration
- [x] Three participants implemented: InsightFlow, InsightBridge, InsightCore
- [x] Platform registration (3/3 services registered with QCG)
- [x] Capability discovery via SDK and REST
- [x] SDK-based capability invocation (3/3 SUCCESS)
- [x] Health monitoring (Insight service + QCG UP)
- [x] Version negotiation
- [x] Failure-path behavior (SERVICE_NOT_FOUND, VERSION_REJECTED, invalid operation)
- [x] Evidence generation and persistence

### Quantum Runtime Integration
- [x] `MarineQuantumAdapter` implemented (`src/platform/quantum_adapter.py`)
- [x] InsightBridge delegates quantum payloads to local Marine Quantum Runtime
- [x] Quantum capability discovery (`quantum_pipeline`, `signal`)
- [x] Quantum invocation with deterministic output
- [x] Malformed payload rejection via typed attachment validation
- [x] Quantum provider abstraction (`QuantumExecutionProvider` interface)
- [x] Local fallback provider (`local_simulator`) — always available, stdlib-only

### Replay and Verification
- [x] Replay lineage retrieval verified (`GET /qcg/replay/lineage/{id}` → HTTP 200, VALID)
- [x] `/qcg/verify` negative-path evidence captured (HTTP 422, `INVALID_SIGNATURE` at Trust stage)
- [x] Local in-memory replay deduplication via `CanonicalReplayAuthority`

### Documentation
- [x] Architecture documented
- [x] Integration guide documented
- [x] Handover guide documented
- [x] Evidence packet populated with classifications

---

## 4. What Is Not Completed

### Blocked / Not Proven
- [ ] **Persistent replay across restart** — `TraceStore` is a local in-memory stub. Evidence does not survive process restart. Owner: Platform Runtime (external).
- [ ] **Live cloud quantum provider** — No live quantum provider is configured or proven. Aer requires `qiskit-aer` installation; IBM/IonQ require SDK + credentials + network egress. Owner: Ganesh (runtime) / External (credentials).
- [ ] **Live telemetry export** — `PlatformTelemetryAdapter` uses local `TraceStore` stub. No live telemetry backend configured. Owner: Platform Runtime (external).
- [ ] **Trust-stage verification** — `/qcg/verify` returns HTTP 422 with `INVALID_SIGNATURE`. This is a platform-level ECDSA issue, not a runtime bug. Owner: QCG Platform (external / Pritesh).
- [ ] **Quantum-network execution** — No quantum-network implementation exists. Only a bounded integration contract is defined. Owner: Collective / requires assignment.
- [ ] **Production certification** — Not claimed. Depends on external platform/governance requirements.

### Future Work
- [ ] Install `qiskit-aer` to enable real local quantum circuit simulation via `AerProvider`
- [ ] Attach live quantum provider (IBM Quantum / IonQ) when credentials and network egress are available
- [ ] Replace `TraceStore` stub with canonical Platform telemetry implementation when contract is published
- [ ] Implement persistent replay authority that survives process restart
- [ ] Resolve QCG ECDSA signature verification failure at Trust stage

---

## 5. Runtime Architecture

### Execution Flow

```text
BHIV Workload
      |
      v
Capability Discovery
      |
      v
Suitability / Routing
      |
      +----------------------+
      |                      |
      v                      v
Classical Path        Quantum Path
      |                      |
      |               Marine Quantum Runtime
      |               (localhost:8000)
      |                      |
      |               Classical deterministic
      |               simulation (seed-based)
      |               execution_classification
      |               = QUANTUM_LOCAL
      |                      |
      +----------+-----------+
                 |
                 v
        Normalized Result
                 |
                 v
          QCG Boundary
       Validation / Replay
                 |
      +----------+-----------+
      |                      |
      v                      v
/verify (422)        /replay/lineage (200)
Trust HALTED         Replay VALID
      |                      |
      +----------+-----------+
                 |
                 v
       Insight Observability
                 |
                 v
       Quantum-Network Integration
       (bounded contract;
        not verified live)
                 |
                 v
          Provenance
```

### Component Ownership

| Component       | Owner           | Responsibility                              |
|-----------------|-----------------|---------------------------------------------|
| InsightFlow     | Insight Stack   | Workflow orchestration participant           |
| InsightBridge   | Insight Stack   | Cross-domain messaging + Quantum gateway     |
| InsightCore     | Insight Stack   | Deterministic state validation participant   |
| Marine Quantum Runtime | Dhiraj Chavan | Local quantum execution (classical simulation) |
| QCG Platform    | Platform / Pritesh | Registry, discovery, replay, trust boundary |
| Platform SDK    | Platform        | `tantra-platform-sdk` canonical interface    |
| Telemetry       | Platform Runtime | TraceStore and observability backend        |
| Quantum Network | Collective      | Quantum communication coordination           |

---

## 6. Reproduction Procedure

### Environment Setup

```powershell
cd "C:\Ganesh_149\Bhiv QCG works\master file\Insight_Constitutional_Runtime"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install tantra-platform-sdk==1.0.0

# Verify SDK installation
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"
```

### Start Marine Quantum Runtime (required for quantum adapter tests)

```powershell
cd "C:\Ganesh_149\Bhiv QCG works\marine_quantum_runtime"
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

Verify it is running:
```powershell
python -c "import requests; print(requests.get('http://localhost:8000/health', timeout=5).json())"
# Expected: {"status":"ok","runtime":"marine-quantum-runtime","version":"1.0.0"}
```

### Run Tests

```powershell
# Full test suite (27 tests)
cd "C:\Ganesh_149\Bhiv QCG works\master file\Insight_Constitutional_Runtime"
pytest -v
# Expected: 27 passed, 3 warnings

# Individual test suites
pytest tests/test_execution_contract.py -v       # 12/12 local participant tests
pytest tests/test_insightbridge_quantum.py -v    # 4/4 quantum delegation tests (mocked HTTP)
pytest tests/test_quantum_adapter.py -v          # 6/6 real HTTP tests (requires localhost:8000)
pytest tests/test_live_platform.py -v            # 5/5 live QCG integration tests

# Collect tests without running
pytest --collect-only -q
```

### What Each Command Proves

| Command | Proves |
|---------|--------|
| `pytest -v` | Full local + live integration test suite passes |
| `pytest tests/test_execution_contract.py -v` | Three participants execute correctly; contract validation works |
| `pytest tests/test_insightbridge_quantum.py -v` | InsightBridge delegates quantum payloads; standard execution unchanged |
| `pytest tests/test_quantum_adapter.py -v` | Marine Quantum Runtime HTTP adapter works (requires runtime running) |
| `pytest tests/test_live_platform.py -v` | Live QCG platform integration works (requires network) |
| `python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"` | Canonical Platform SDK is installed |

---

## 7. Registration Procedure

### Canonical Registration

Registration is performed by `PlatformIntegrationService` via `LivePlatformClient`:

```powershell
python -c "from src.integration.platform_integration_service import PlatformIntegrationService; PlatformIntegrationService().integrate()"
```

This performs:
1. Runtime registration for all 3 participants (`POST /registry/platform/v1/register`)
2. Capability registration (`POST /registry/capabilities/register`)
3. Service discovery (`GET /registry/platform/v1/services`)
4. Version negotiation via SDK
5. Capability invocation
6. Health checks
7. Replay validation
8. Telemetry recording
9. Failure-path exercise
10. Evidence generation

### Expected Registration Response

```json
{
  "status": "REGISTERED" | "ALREADY_REGISTERED",
  "service_id": "insightflow.runtime.intelligence.v1",
  "version": "1.0.2"
}
```

`ALREADY_REGISTERED` is idempotent and not an error.

### Verify Registration

```powershell
python -c "import requests; print(requests.get('https://bhiv-qcg.onrender.com/registry/platform/v1/services', timeout=20).json())"
```

Expected: Response contains all three Insight services.

### Registration Receipt

Stored in: `evidence_packet/api_samples/runtime_registration.json`

---

## 8. Verification + Replay Procedure

### Sequence

```text
1. Invoke capability via SDK or direct execution
        ↓
2. Capture invocation_id
        ↓
3. POST /qcg/verify with invocation_id
        ↓
4. Observe Trust-stage INVALID_SIGNATURE (HTTP 422)
        ↓
5. Do NOT call this verification success
        ↓
6. GET /qcg/replay/lineage/{invocation_id}
        ↓
7. Inspect canonical replay lineage (HTTP 200, VALID)
```

### Commands

**1. Invoke**
```powershell
python -c "
from src.platform.sdk_adapter import PlatformSDKAdapter
sdk = PlatformSDKAdapter()
result = sdk.invoke_capability(
    service_id='insightflow.runtime.intelligence.v1',
    operation='execute',
    payload={'test_id': 'handover-verify'},
    version='1.0.2'
)
print('invocation_id:', result.invocation_id)
print('status:', result.status)
"
```
Expected: `status: SUCCESS`, `invocation_id` returned.

**2. Verify**
```powershell
python -c "
import requests
r = requests.post(
    'https://bhiv-qcg.onrender.com/qcg/verify',
    json={'invocation_id': '<invocation_id>'},
    timeout=30
)
print('status:', r.status_code)
print(r.json()['detail']['stages']['replay'])
print(r.json()['detail']['stages']['trust'])
"
```
Expected: HTTP 422; Replay stage `VALID`; Trust stage `passed: false`, `halt_signal: HALT:INVALID_SIGNATURE`.

**3. Replay Lineage**
```powershell
python -c "
import requests
r = requests.get(
    'https://bhiv-qcg.onrender.com/qcg/replay/lineage/{invocation_id}',
    timeout=20
)
print('status:', r.status_code)
print('verdict:', r.json()['verdict']['status'])
print('replay_id:', r.json()['verdict']['lineage_record']['replay_id'])
"
```
Expected: HTTP 200; `verdict.status: VALID`; `lineage_record` present.

### Interpretation

- `/qcg/verify` is a **verified negative Trust-path result**. The request reaches the Replay stage successfully, but Trust rejects the verification due to ECDSA signature failure.
- `/qcg/replay/lineage/{invocation_id}` is **independently verified**. The canonical replay authority recorded the execution and returns a VALID lineage record.
- The Trust-stage failure does **not** invalidate the separately verified replay objective.

---

## 9. Evidence Map

```
evidence_packet/
├── api_samples/
│   ├── runtime_registration.json      → 3/3 service registration receipts
│   ├── capability_registration.json   → 3/3 capability registration receipts
│   ├── discovered_services.json       → Live service discovery response
│   ├── platform_health.json           → Platform health snapshot
│   └── version_negotiation.json       → Version negotiation results
├── invocation_proof/
│   ├── invocation_results.json        → SDK invocation results
│   ├── failure_cases.json             → SERVICE_NOT_FOUND, VERSION_REJECTED
│   └── sdk_evidence_chain.json        → SDK evidence chain records
├── replay_evidence/
│   ├── replay_validation.json         → Replay lineage verification
│   └── verify_replay_valid_422_trust.json → /verify negative-path evidence
├── quantum_evidence/
│   ├── quantum_local_health.json      → Marine runtime health
│   ├── quantum_pipeline_invocation.json → Quantum pipeline execution proof
│   ├── quantum_failure_case.json      → Invalid input rejection
│   └── quantum_provenance_summary.json → Provenance metadata
├── telemetry/
│   └── traces.json                    → Local TraceStore stub output
├── registry_proof/
│   ├── registration_response.json     → Combined registration evidence
│   ├── version_negotiation.json       → Version negotiation evidence
│   └── health_check.json              → Health check evidence
├── deployment_proof/
│   └── deployment_status.json         → Deployment status
├── production_readiness/
│   └── readiness_report.md            → Production readiness assessment
├── runtime_logs/
│   └── integration.log                → Full integration workflow log
└── screenshots/
    └── ...                             → Visual evidence artifacts
```

---

## 10. Test Matrix

| # | Test | Result | Classification | Evidence |
| - | ---- | ------ | -------------- | -------- |
| 1 | InsightFlow execution | PASS | LOCAL | `tests/test_execution_contract.py::test_1_insightflow_success` |
| 2 | InsightBridge execution | PASS | LOCAL | `tests/test_execution_contract.py::test_2_insightbridge_success` |
| 3 | InsightCore execution | PASS | LOCAL | `tests/test_execution_contract.py::test_3_insightcore_success` |
| 4 | Unknown service rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_4_unknown_service` |
| 5 | Unknown operation rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_5_unknown_operation` |
| 6 | Missing service_id rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_6_missing_service_id` |
| 7 | Missing operation rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_7_missing_operation` |
| 8 | Missing payload rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_8_missing_payload` |
| 9 | Missing version rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_9_missing_version` |
| 10 | Missing invocation_id rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_10_missing_invocation_id` |
| 11 | Unsupported version rejection | PASS | LOCAL | `tests/test_execution_contract.py::test_11_unsupported_version` |
| 12 | Response contract validation | PASS | LOCAL | `tests/test_execution_contract.py::test_12_response_contract` |
| 13 | InsightBridge standard execution untouched | PASS | LOCAL (mocked) | `tests/test_insightbridge_quantum.py::test_insightbridge_standard_execution_untouched` |
| 14 | InsightFlow/Core unaffected by quantum | PASS | LOCAL (mocked) | `tests/test_insightbridge_quantum.py::test_insightflow_and_insightcore_unaffected` |
| 15 | InsightBridge quantum forwarding | PASS | LOCAL (mocked) | `tests/test_insightbridge_quantum.py::test_insightbridge_quantum_forwarding` |
| 16 | InsightBridge health with quantum gateway | PASS | LOCAL (mocked) | `tests/test_insightbridge_quantum.py::test_insightbridge_health` |
| 17 | Server health | PASS | LIVE | `tests/test_live_platform.py::test_server_health` |
| 18 | Service list | PASS | LIVE | `tests/test_live_platform.py::test_list_services` |
| 19 | SDK discovers Insight runtime | PASS | LIVE | `tests/test_live_platform.py::test_sdk_discovers_insight_runtime` |
| 20 | SDK invocation | PASS | LIVE | `tests/test_live_platform.py::test_sdk_invocation` |
| 21 | SDK invocation + verify + replay | PASS | LIVE | `tests/test_live_platform.py::test_sdk_invocation_verify_and_replay` |
| 22 | Quantum adapter health | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_health` |
| 23 | Quantum adapter list capabilities | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_list_capabilities` |
| 24 | Quantum adapter discover capability | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_discover_capability` |
| 25 | Quantum adapter invocation | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_invocation_quantum_pipeline` |
| 26 | Quantum adapter malformed payload | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_malformed_payload` |
| 27 | Quantum adapter unavailable mode | PASS | LOCAL | `tests/test_quantum_adapter.py::test_quantum_adapter_unavailable_mode` |

---

## 11. Reproduction Commands

### Full verification sequence

```powershell
# 1. Verify SDK
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"

# 2. Verify QCG health
python -c "import requests; print(requests.get('https://bhiv-qcg.onrender.com/registry/platform/v1/health', timeout=20).json())"

# 3. Start Marine runtime (in separate terminal)
cd "C:\Ganesh_149\Bhiv QCG works\marine_quantum_runtime"
uvicorn api_server:app --host 0.0.0.0 --port 8000

# 4. Verify Marine runtime health
python -c "import requests; print(requests.get('http://localhost:8000/health', timeout=5).json())"

# 5. Run full test suite
cd "C:\Ganesh_149\Bhiv QCG works\master file\Insight_Constitutional_Runtime"
pytest -v

# 6. Run live platform tests only
pytest tests/test_live_platform.py -v

# 7. Run quantum adapter tests only
pytest tests/test_quantum_adapter.py -v

# 8. Verify Insight service health
python -c "import requests; print(requests.get('https://insight-constitutional-runtime.onrender.com/api/v1/health', timeout=20).json())"
```

---

## 12. Evidence Philosophy

Evidence proves what happened. It does not prove what was intended.

- **Local verification ≠ live deployment**
- **Simulation ≠ quantum hardware**
- **Replay ≠ legitimacy**
- **Health ≠ functional success**
- **A negative-path test passing ≠ the underlying operation succeeding**

When reviewing this repository, distinguish between:
- What the code actually does
- What the tests actually verify
- What the documentation claims
- What remains unproven

---

## 13. Continuation Guide

### If continuing this work

**Prioritized sequence:**

1. Read `README.md` for project overview and current status
2. Read `HANDOVER.md` (this document) for operational details
3. Read `docs/AUDIT_REPORT.md` for complete engineering audit
4. Read `docs/FINAL_STATUS.md` for status matrix
5. Review `REVIEW_PACKET.md` for evidence summary
6. Inspect `evidence_packet/` for actual evidence artifacts
7. Run `pytest --collect-only -q` to see all available tests
8. Run `pytest -v` to verify current test state
9. Review blockers in Section 4 of this document
10. Continue only within the assigned authority boundary

### Authority Boundaries

| Area | Owner | Notes |
|------|-------|-------|
| Insight participants (Flow, Bridge, Core) | Insight Stack | Ganesh is integration participant, not owner |
| Platform Runtime / Registry / Discovery | Platform / Kanishk | External service (`bhiv-qcg.onrender.com`) |
| Quantum Runtime (Marine) | Dhiraj Chavan | Local runtime; classical simulation |
| Quantum provider attachment | Ganesh | Requires credentials + network egress |
| Replay Authority | Pritesh | Canonical replay persistence |
| Trust/Verification | Pritesh / QCG Platform | ECDSA signature issue |
| Telemetry backend | Platform Runtime | Contract not yet published |
| Quantum Network | Collective | Requires assignment |

**Do not silently absorb another person's responsibility.** If ownership is unclear, mark it as `OWNERSHIP REQUIRES CONFIRMATION`.

---

## 14. Screenshot Map

| Screenshot | Purpose | Classification |
|------------|---------|----------------|
| `01_service_registration.png` | Registration proof | LIVE |
| `02_service_discovery.png` | Discovery proof | LIVE |
| `03_health_check.png` | Health proof | LIVE |
| `04_sdk_invocation.png` | Invocation proof | LIVE |
| `05_replay_lineage.png` | Replay lineage proof | LIVE |
| `06_verify_trust_422.png` | Verify negative-path proof | LIVE (negative path) |
| `07_quantum_execution.png` | Quantum pipeline execution | LOCAL |
| `08_full_test_suite.png` | 27/27 tests passing | LOCAL |

---

## 15. Final Status

**27 passed, 3 warnings** (stable run)

- `LIVE` verified: Registration, discovery, SDK invocation, health, replay lineage
- `LOCAL` verified: Quantum execution (classical deterministic simulation), telemetry (stub)
- `PARTIAL` verified: `/qcg/verify` — Replay VALID, Trust HALTED (HTTP 422, ECDSA)
- `NOT PROVEN`: Persistent replay across restart, quantum-network execution, live cloud quantum provider
- `NOT CLAIMED`: Production certification

**The repository is ready for handover.**

---

**Last Updated**: 2026-08-29
