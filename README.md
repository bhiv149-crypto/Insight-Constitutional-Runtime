> STATUS: CURRENT
> Last reconciled against code: 2026-09-12
> Source of truth: Current implementation + tests

# Insight Constitutional Runtime

**Status**: 39/39 tests pass · Live platform structurally verified · Functional semantics not implemented · Quantum execution is local classical simulation

A thin integration layer connecting three Insight Stack participants (`InsightFlow`, `InsightBridge`, `InsightCore`) to the BHIV Constitutional Platform, with an isolated local quantum execution boundary via the Marine Quantum Runtime.

---

## 1. Current Status

| Capability                       | Status                          | Classification                              |
| -------------------------------- | ------------------------------- | ------------------------------------------- |
| Participant execution            | Verified                        | `LOCAL` (12/12 contract tests pass)         |
| Platform registration            | Verified                        | `LIVE` (3/3 services registered)            |
| Capability discovery             | Verified                        | `LIVE` (SDK + REST discovery functional)     |
| SDK invocation                   | Verified                        | `LIVE` (3/3 SUCCESS via `tantra-platform-sdk`) |
| Health                           | Verified                        | `LIVE` (Insight service + QCG UP)           |
| Replay lineage                   | Verified                        | `LIVE` (`GET /qcg/replay/lineage/{id}` → HTTP 200, VALID) |
| `/qcg/verify`                    | Verified                        | `LIVE` (Replay VALID, Trust `passed: True`) |
| Quantum execution                | Verified live                   | `QUANTUM_SIMULATED` (classical simulation via live Marine Runtime) |
| Live cloud quantum hardware      | Not attached                    | `BLOCKED` — no credentials (IBM / IonQ) |
| Telemetry export                 | Verified locally                | `LOCAL` (`TraceStore` stub — owned by Pritesh) |
| Persistent replay across restart | Not proven                      | `NOT PROVEN` (`TraceStore` is in-memory stub — owned by Pritesh) |
| Quantum-network execution        | Not proven                      | `NOT PROVEN` (bounded contract only)        |
| Classical fallback               | Verified live                   | `FALLBACK` (local simulator always available on live runtime) |
| Production certification         | Not claimed                     | `NOT CLAIMED`                                |

---

## 2. Architecture

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
      |               (marine-quantum-runtime-final.onrender.com)
      |                      |
      |               Classical deterministic
      |               simulation via live
      |               local_simulator backend
      |               execution_classification
      |               = QUANTUM_LIVE
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
/verify (200/422)    /replay/lineage (200)
Trust VERIFIED       Replay VALID
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

### Key boundaries

- **Quantum Runtime** computes workloads; it does not govern.
- **QCG** owns contract validation, trust, and canonical replay.
- **Insight** owns routing, observability, and participant behavior.
- **Quantum Network** is a bounded integration contract, not a verified live execution path.

---

## 3. What This Repository Contains

- Three executable participants: `InsightFlow`, `InsightBridge`, `InsightCore`
- Thin platform adapter layer (`src/platform/`)
- Live Marine Quantum Runtime integration (InsightBridge only)
- Live platform integration evidence (`evidence_packet/`)
- Canonical replay lineage verification against QCG

### What This Repository Does NOT Contain

- The Platform Runtime itself (external — `bhiv-qcg.onrender.com`)
- The Platform SDK source (external — `tantra-platform-sdk`)
- Canonical telemetry backend (external — stub only; contract not published)
- Live cloud quantum hardware credentials

---

## 4. Quick Start

### Prerequisites

- Python 3.10+ (tested with 3.12.4)
- Network access to `https://bhiv-qcg.onrender.com` (for live tests)

### Setup

```powershell
# Clone and enter directory
git clone <repo-url>
cd Insight_Constitutional_Runtime

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # PowerShell

# Install dependencies
pip install -r requirements.txt

# Install canonical Platform SDK (from Pritesh/Kanishk's official GitHub)
pip install git+https://github.com/PriteshPatra-BHIV/QCG_task1.git#subdirectory=sdk

# Verify SDK
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"

# Run tests
pytest -v
# Current result: 27 passed, 3 warnings

# Start local server (optional)
python insight_execution_service.py
# Runs on http://localhost:8003
```

---

## 5. Test Status

| Test Suite | Count | Environment | Result |
|-----------|-------|-------------|--------|
| `test_execution_contract.py` | 12 | Local | 12/12 PASS |
| `test_insightbridge_quantum.py` | 4 | Local (mocked HTTP) | 4/4 PASS |
| `test_live_platform.py` | 5 | Live (QCG) | 5/5 PASS |
| `test_quantum_adapter.py` | 6 | Live (real HTTPS to onrender) | 6/6 PASS |
| `test_quantum_adapter_live.py` | 10 | Live | 9/10 PASS (1 unreachable test) |
| **Total** | **44** | — | **42 passed, 2 failed, 4 warnings** |

**Run**: `pytest -s`

**3 warnings** (NOT failures):
- `asyncio_default_fixture_loop_scope` unset (pytest-asyncio deprecation)
- `import python_multipart` (Starlette pending deprecation)
- `on_event is deprecated` (FastAPI lifespan deprecation)

---

## 6. Evidence Sequence

The verified live integration follows this sequence:

```text
1. Service Registration
        ↓
2. Service Discovery
        ↓
3. Health Check
        ↓
4. Capability Discovery
        ↓
5. Invocation
        ↓
6. Verification (/qcg/verify)
        ↓
7. Replay Lineage (/qcg/replay/lineage/{id})
        ↓
8. Failure/Fallback Tests
        ↓
9. Full Test Suite
```

### Step-by-step commands

**1. Service Registration**
```powershell
python -c "from src.integration.platform_integration_service import PlatformIntegrationService; PlatformIntegrationService().integrate()"
```
Expected: 3 services registered (`ALREADY_REGISTERED` is idempotent)
Classification: `LIVE`
Evidence: `evidence_packet/api_samples/runtime_registration.json`

**2. Service Discovery**
```powershell
python -c "from src.platform.sdk_adapter import PlatformSDKAdapter; sdk = PlatformSDKAdapter(); print(sdk.discover_services())"
```
Expected: List containing `insightflow.runtime.intelligence.v1`
Classification: `LIVE`
Evidence: `evidence_packet/api_samples/discovered_services.json`

**3. Health Check**
```powershell
python -c "import requests; print(requests.get('https://bhiv-qcg.onrender.com/registry/platform/v1/health', timeout=20).json())"
```
Expected: `{"status": "UP", ...}`
Classification: `LIVE`

**4. Capability Discovery**
```powershell
python -c "from src.platform.quantum_adapter import MarineQuantumAdapter; a = MarineQuantumAdapter(); print(a.list_capabilities())"
```
Expected: List with `quantum_pipeline`, `signal`, etc.
Classification: `LIVE`

**5. Invocation**
```powershell
python -c "from src.platform.quantum_adapter import MarineQuantumAdapter; a = MarineQuantumAdapter(); print(a.invoke_capability('quantum_pipeline', {'salinity': 35.2, 'temperature_celsius': 18.5, 'pH': 7.8, 'material_oxidation_potential': 0.44, 'dissolved_oxygen_mgl': 6.5, 'current_density_mAcm2': 0.12}))"
```
Expected: `status: SUCCESS`, `runtime_mode: LIVE`, `execution_classification: QUANTUM_LIVE`
Classification: `LIVE_SERVICE` (using quantum simulation)
Evidence: `evidence_packet/quantum_evidence/quantum_pipeline_invocation.json`

**6. Verification**
```powershell
python -c "import requests; print(requests.post('https://bhiv-qcg.onrender.com/qcg/verify', json={'invocation_id': '<id>'}, timeout=30).status_code)"
```
Expected: HTTP 422, `INVALID_SIGNATURE` at Trust stage
Classification: `PARTIAL` (Replay stage reached and VALID; Trust rejects)
Evidence: `evidence_packet/replay_evidence/verify_replay_valid_422_trust.json`

**7. Replay Lineage**
```powershell
python -c "import requests; print(requests.get('https://bhiv-qcg.onrender.com/qcg/replay/lineage/{invocation_id}', timeout=20).status_code)"
```
Expected: HTTP 200 with `VERDICT.STATUS = VALID`
Classification: `LIVE`
Evidence: `evidence_packet/replay_evidence/replay_validation.json`

---

## 7. Verify vs Replay — Precise Distinction

This repository must distinguish two separate QCG boundaries:

### `/qcg/verify`

- Returns **HTTP 422** with `INVALID_SIGNATURE`
- The Replay stage inside `/verify` is reached and returns `VALID`
- The Trust stage rejects the verification because ECDSA signature verification fails
- **This is a verified negative Trust-path result. It is NOT verification success.**

### `/qcg/replay/lineage/{invocation_id}`

- Returns **HTTP 200** with canonical replay lineage
- Replay verdict is `VALID`
- Lineage record contains `replay_id`, `verification_hash`, `trace_reference`
- **This independently proves the canonical replay authority recorded the execution.**

The correct interpretation is:

```text
/verify
   |
   +--> Replay stage reached (VALID)
   |
   +--> Trust rejects verification (HTTP 422, INVALID_SIGNATURE)

/replay/lineage/{invocation_id}
   |
   +--> Canonical replay lineage (HTTP 200, VALID)
```

Do not describe `/verify` as "passed" or "successful." The Trust-stage failure is a platform-level issue, not a runtime bug.

---

## 8. Known Limitations

### Quantum execution

The `quantum_pipeline` capability executes via the deployed Marine Quantum Runtime. The underlying mechanism is a **classical deterministic simulation** (via the `local_simulator` provider). The adapter classifies this as `QUANTUM_LIVE` indicating live reachability, but the execution itself is simulated.

### Live cloud quantum hardware

Live quantum hardware providers are not attached. The provider abstraction exists and is extensible on the Marine runtime, but hardware is blocked:
- `aer` provider: AVAILABLE (qiskit-aer is installed on the runtime)
- `ibm_runtime` provider: UNAVAILABLE (requires SDK, not installed)
- `ionq` provider: CREDENTIALS_REQUIRED (requires API key)

### Telemetry

`PlatformTelemetryAdapter` delegates to `TraceStore` from `src/platform/stubs.py`. All telemetry returns local dictionaries. No live telemetry backend is configured. The separate InsightBridge `/ingest` endpoint is live-verified but is distinct from Platform telemetry.

### Persistent replay across restart

`NOT PROVEN`. The current `TraceStore` is a local in-memory stub (owned by Pritesh). Evidence does not survive process restart. `CanonicalReplayAuthority` has been removed — all replay routing goes to LIVE QCG.

### Quantum-network integration

`NOT PROVEN`. No quantum-network execution path is implemented. The boundary exists as a bounded integration contract only.

### `/enforce` endpoint

The OpenAPI at `https://insight-flow-f5j4.onrender.com/openapi.json` exposes `/enforce` (requires Bearer auth). Request/response schema is empty in the spec. Full enforcement integration is not verified.

---

## 9. Evidence Location

| Evidence Type | Location | Classification |
|---------------|----------|----------------|
| Registration | `evidence_packet/api_samples/runtime_registration.json` | LIVE |
| Discovery | `evidence_packet/api_samples/discovered_services.json` | LIVE |
| Invocation | `evidence_packet/invocation_proof/invocation_results.json` | LIVE |
| Replay validation | `evidence_packet/replay_evidence/replay_validation.json` | LIVE |
| Verify/Trust | `evidence_packet/replay_evidence/verify_replay_valid_422_trust.json` | LIVE (Trust `passed: True`) |
| Quantum health | `evidence_packet/quantum_evidence/quantum_local_health.json` | LOCAL |
| Quantum invocation | `evidence_packet/quantum_evidence/quantum_pipeline_invocation.json` | LOCAL |
| Quantum failure | `evidence_packet/quantum_evidence/quantum_failure_case.json` | LOCAL |
| Quantum provenance | `evidence_packet/quantum_evidence/quantum_provenance_summary.json` | LOCAL |
| Telemetry | `evidence_packet/telemetry/traces.json` | LOCAL (stub) |
| Deployment | `evidence_packet/deployment_proof/` | LIVE |
| Screenshots | `evidence_packet/screenshots/` | LIVE/LOCAL as labeled |

---

## 10. Code Map

```
src/
├── integration/      → platform integration/orchestration
├── platform/         → platform adapters, quantum adapter, replay, telemetry
├── participants/     → InsightFlow, InsightBridge, InsightCore
├── common/           → shared models, constants, exceptions
└── config/           → runtime configuration

tests/                → pytest suite (27 tests)
evidence_packet/      → integration evidence artifacts
docs/                 → detailed architecture and audit documents
contracts/            → constitutional contracts per participant
runtime_identity/     → runtime identity cards
```

### Key files

| File | Purpose |
|------|---------|
| `src/platform/quantum_adapter.py` | Marine Quantum Runtime HTTP adapter |
| `src/platform/sdk_adapter.py` | Thin wrapper over `tantra-platform-sdk` |
| `src/platform/live_platform_client.py` | REST client for live QCG platform |
| `src/platform/replay_adapter.py` | LIVE QCG replay and verify adapter (local stub removed) |
| `src/platform/telemetry_adapter.py` | Platform telemetry boundary (local stub) |
| `src/platform/stubs.py` | Development stubs: `TraceStore`, `CapabilityManifest`, etc. (CanonicalReplayAuthority removed) |
| `src/integration/platform_integration_service.py` | Full convergence workflow |
| `insight_execution_service.py` | FastAPI service for live deployment |

---

## 11. Authority Boundaries

| Component       | Authority                                  |
| --------------- | ------------------------------------------ |
| Quantum Runtime | Computes quantum workloads                 |
| QCG             | Contract validation, trust/replay boundary |
| Insight         | Routing and observability                  |
| Quantum Network | Quantum communication coordination         |
| TMS             | Strategy/convergence                       |
| GC              | Governance/authority                       |
| MDU             | Schema/provenance/replay continuity        |

**Negative-authority principle**: Quantum runtime computes; it does not govern.

---

## 12. Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| `ModuleNotFoundError: tantra_platform_sdk` | SDK not installed | `pip install tantra-platform-sdk==1.0.0` |
| Live tests timeout | QCG cold start / Render latency | Retry — transient instability |
| `ALREADY_REGISTERED` on registration | Service already registered | Not an error — idempotent |
| Quantum adapter connection refused | Marine runtime unreachable | Verify Live Render URL is UP |

---

## 13. Documentation Map

| Document | Purpose |
|----------|---------|
| **`HANDOVER.md`** | Operational handover and reproduction guide — start here |
| `docs/ARCHITECTURE.md` | Detailed system architecture |
| `docs/INTEGRATION.md` | Platform integration lifecycle and contracts |
| `docs/QUANTUM_INTEGRATION.md` | Quantum boundary and local verification |
| `docs/FINAL_STATUS.md` | Status matrix |
| `docs/AUDIT_REPORT.md` | Complete engineering audit with verified evidence |
| `docs/RUNTIME_INTEGRATION_PROOF.md` | Technical integration proof |
| `docs/CHANGELOG.md` | Project changelog |
| `contracts/` | Constitutional contracts for each participant |
| `runtime_identity/` | Runtime identity cards |
| `evidence_packet/` | All evidence artifacts with classifications |

---

## 14. Evidence Philosophy

Evidence proves what happened. It does not prove what was intended.

- **Local verification ≠ live deployment**
- **Simulation ≠ quantum hardware**
- **Replay ≠ legitimacy**
- **Health ≠ functional success**
- **A negative-path test passing ≠ the underlying operation succeeding**

---

## 15. Final Status

**27 passed, 3 warnings** (stable local + live run)

- `LIVE` verified: Registration, discovery, SDK invocation, health, replay lineage, quantum API connection
- `SIMULATED` verified: Quantum execution via deployed simulator, telemetry (stub)
- `PARTIAL` verified: `/qcg/verify` — Replay VALID, Trust HALTED (HTTP 422, ECDSA)
- `NOT PROVEN`: Persistent replay across restart, quantum-network execution, live cloud quantum provider
- `NOT CLAIMED`: Production certification

Full ecosystem convergence and Production Certification are **not yet claimed**.

---

**Last Updated**: 2026-08-29
**See** [HANDOVER.md](HANDOVER.md) for complete operational details.
