# Engineering Handover Guide — Insight Constitutional Runtime

**Status**: LIVE VERIFIED — Replay lineage is valid; `/qcg/verify` remains halted at Trust due to `INVALID_SIGNATURE`  
**Audience**: Incoming maintainers, system integrators, security reviewers  
**Access**: Clone repository, read this guide, confirm the current Replay evidence and platform constraints

---

## 1. Project Purpose & Scope

The **Insight Constitutional Runtime** integrates the Insight Stack (`InsightFlow`, `InsightBridge`, `InsightCore`) into the **BHIV Constitutional Platform** as reusable, schema-compliant runtime participants. The runtime operates as an external service with thin platform adapters, consuming canonical Platform services for registration, discovery, health monitoring, and SDK-based invocation.

**What This Runtime Does:**
- Execute intelligence workflows through three specialized participants
- Register with the platform's capability registry
- Support dynamic service discovery via PlatformCapabilitySDK
- Emit evidence and maintain execution lineage
- Respond to SDK invocation requests from the platform

**What This Runtime Does NOT Do:**
- Implement the Platform Runtime itself
- Own the Platform Registry or service catalog (external platform service)
- Own the Canonical Replay Authority or certification endpoints (external QCG)
- Own the PlatformCapabilitySDK (external dependency: tantra-platform-sdk)
- Implement or export telemetry (stub only, awaiting platform contract)

---

## 2. Ownership Boundaries

| Component | Owner | Status |
|-----------|-------|--------|
| Insight Execution Service | This Repository | FastAPI service on `/api/v1/execute` |
| InsightFlow, InsightBridge, InsightCore Participants | This Repository | Intelligence workflow implementations |
| Platform Adapters (src/platform/) | This Repository | Thin wrappers over platform services |
| PlatformCapabilitySDK | External (tantra-platform-sdk 1.0.0) | Must be installed separately |
| Platform Registry | External (bhiv-qcg.onrender.com) | Service registration, discovery, health |
| Canonical Replay Authority | External (QCG) | Replay lineage retrieval (HTTP 200, VALID) |
| Canonical Telemetry | External (QCG) | Evidence export (awaiting contract) |

---

## 3. Service Identity & Live Status

All three participants are registered and active on the BHIV platform (verified 2026-08-17):

| Service ID | Display Name | Version | Status | Registration |
|---|---|---|---|---|
| `insightflow.runtime.intelligence.v1` | InsightFlow | 1.0.2 | ACTIVE | LIVE |
| `insightbridge.runtime.intelligence.v1` | InsightBridge | 1.0.2 | ACTIVE | LIVE |
| `insightcore.runtime.intelligence.v1` | InsightCore | 1.0.2 | ACTIVE | LIVE |

**Discovery Endpoint**: `GET https://bhiv-qcg.onrender.com/registry/platform/v1/services` (HTTP 200)  
**Execution Endpoint**: `POST https://insight-constitutional-runtime.onrender.com/api/v1/execute`

---

## 4. Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│  Insight Execution Service                             │
│  (FastAPI)                                             │
│                                                        │
│  POST /api/v1/execute    (Capability execution)        │
│  GET  /api/v1/health     (Health check)                │
│  GET  /api/v1/services   (Service catalog)             │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Participants                                    │  │
│  │  - InsightFlow.v1.0.2                            │  │
│  │  - InsightBridge.v1.0.2                          │  │
│  │  - InsightCore.v1.0.2                            │  │
│  └──────────────────┬───────────────────────────────┘  │
│                     │                                  │
│  ┌──────────────────▼───────────────────────────────┐  │
│  │  Platform Adapters (src/platform/)               │  │
│  │  - SDKAdapter, DiscoveryAdapter                  │  │
│  │  - RegistryAdapter, ReplayAdapter                │  │
│  │  - HealthAdapter, TelemetryAdapter               │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼──────────────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
 PlatformCapabilitySDK        BHIV QCG Platform
 (tantra-platform-sdk)        (https://bhiv-qcg.onrender.com)
        │                            │
        └────────────┬───────────────┘
                     │
       ┌─────────────▼─────────────┐
       │  Platform Endpoints:      │
       │  /registry/platform/v1/.. │
       │  /qcg/verify              │
       │  /qcg/replay/lineage/{id} │
       │  /qcg/health              │
       └───────────────────────────┘
```

---

## 5. Repository Structure

```
.
├── insight_execution_service.py    Main FastAPI application
├── requirements.txt                Python dependencies
├── render.yaml                     Render deployment config
│
├── src/
│   ├── common/                     Shared interfaces
│   │   ├── base_participant.py
│   │   ├── constants.py            Service IDs and versions
│   │   ├── exceptions.py
│   │   └── models.py               Request/response schemas
│   │
│   ├── participants/               Runtime implementations
│   │   ├── insightflow_participant.py
│   │   ├── insightbridge_participant.py
│   │   └── insightcore_participant.py
│   │
│   ├── config/
│   │   └── platform_config.py      Platform URLs and SDK config
│   │
│   └── platform/                   Platform adapters
│       ├── sdk_adapter.py          PlatformCapabilitySDK wrapper
│       ├── discovery_adapter.py    Service discovery
│       ├── registry_adapter.py     Service registration
│       ├── replay_adapter.py       Replay lineage
│       ├── health_adapter.py       Health monitoring
│       ├── telemetry_adapter.py    Evidence/trace export (stubbed)
│       └── runtime_config.py       SDK configuration
│
├── contracts/                      Constitutional contracts
├── runtime_identity/               Runtime identity cards
│
├── docs/
│   ├── ARCHITECTURE.md             System design
│   ├── INTEGRATION.md              Platform integration details
│   ├── HANDOVER.md                 THIS FILE
│   ├── FINAL_STATUS.md             Current status snapshot
│   └── CHANGELOG.md                Version history
│
├── tests/
│   ├── test_execution_contract.py  (12 tests) Local execution
│   ├── test_live_platform.py       (5 tests) Live platform
│   ├── replay_registry.json        Local replay registry
│   └── ...
│
└── evidence_packet/                Generated evidence and audit materials
```

---

## 6. Environment Setup (5 Minutes)

### Prerequisites
- Python 3.10+ (tested with 3.12.4)
- pip or conda
- Network access to `https://bhiv-qcg.onrender.com`

### Setup Steps

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd Insight_Constitutional_Runtime

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install external SDK (CRITICAL)
pip install tantra-platform-sdk==1.0.0

# 5. Verify SDK loaded
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('✓ SDK OK')"

# 6. Run tests
pytest -v
# Expected: 17/17 PASSED

# 7. Start runtime (optional)
python insight_execution_service.py
# Runs on http://localhost:8000
```

---

## 7. Configuration Details

**Main Config**: `src/config/platform_config.py`

```python
# Platform discovery root
DISCOVERY_URLS = ["https://bhiv-qcg.onrender.com/registry"]

# Service registry
REGISTRY_HOST = "bhiv-qcg.onrender.com"
REGISTRY_PORT = 443

# Replay registry (local development only)
REPLAY_REGISTRY_PATH = "replay_registry.json"
REPLAY_TTL_SECONDS = 300.0

# Trust provider (from SDK)
TRUST_PROVIDER = create_trust_provider("CLASSICAL")
```

**SDK Configuration:**
- DISCOVERY_URLS is the base URL. SDK appends `/platform/v1/services` to get: `https://bhiv-qcg.onrender.com/registry/platform/v1/services`
- This is verified live and returns all registered services including the 3 Insight participants

---

## 8. Test Inventory & Verification

### All Tests Pass: 17/17 ✓

**Execution Contract Tests** (12 tests — local, no platform dependency)
```bash
pytest tests/test_execution_contract.py -v
```
- test_1_insightflow_success ✓
- test_2_insightbridge_success ✓
- test_3_insightcore_success ✓
- test_4 through test_12: Error handling, validation, schema compliance ✓

**Live Platform Tests** (5 tests — requires bhiv-qcg.onrender.com)
```bash
pytest tests/test_live_platform.py -v
```
- test_server_health ✓
- test_list_services ✓
- test_sdk_discovers_insight_runtime ✓
- test_sdk_invocation ✓
- test_sdk_invocation_verify_and_replay ✓ (Correctly expects HTTP 422 on `/verify` but HTTP 200 on replay)

**Run All:**
```bash
pytest -v
# Expected: 17/17 PASSED in ~7-10 seconds
```

---

## 9. Platform Integration Flow

### Step 1: Service Discovery (Via SDK)
```
discover_services() 
  → SDK calls /registry/platform/v1/services 
  → HTTP 200 
  → Returns all 3 Insight services ACTIVE
```

### Step 2: Service Invocation (Via SDK)
```
invoke_capability(service_id, operation, payload, version)
  → SDK creates invocation_id (UUID) 
  → SDK creates evidence object (hash chain)
  → POST /api/v1/execute on runtime
  → HTTP 200 SUCCESS
  → SDK returns InvocationResult with evidence
```

### Step 3: Verification (QCG Platform)
```
POST /qcg/verify
  → Replay stage: VALID
  → Keshav Analysis: COMPLETED
  → Trust stage: FAILED (HTTP 422, INVALID_SIGNATURE)
  → Overall flow: HALTED at Trust

** IMPORTANT: **
- Replay is valid even while the overall `/verify` request halts at Trust.
- The HTTP 422 is evidence of a Trust/ECDSA signature failure, not a Replay failure.
- This is a platform-side verification condition, not a runtime Replay regression.
```

### Step 4: Replay Lineage (QCG Platform)
```
GET /qcg/replay/lineage/{invocation_id}
  → HTTP 200 OK
  → Returns VALID verdict with complete lineage record
  → The canonical lineage record is preserved by QCG replay authority
```

---

## 10. Known Limitations & Root Causes

### 1. Verify Endpoint Returns HTTP 422 (Platform Issue)
- **Symptom**: POST `/qcg/verify` returns HTTP 422 with `INVALID_SIGNATURE`
- **Root Cause**: QCG platform's ECDSA trust provider cannot verify signatures
- **Impact**: Trust verification fails; replay still works independently
- **Workaround**: Use `/qcg/replay/lineage/{id}` which returns HTTP 200
- **Responsibility**: QCG/Platform team (cryptography validation issue)
- **Test Evidence**: `test_sdk_invocation_verify_and_replay` correctly documents this

### 2. Replay Registry is Local-Only (By Design)
- **Behavior**: `replay_registry.json` is a local development convenience
- **Truth Source**: `/qcg/replay/lineage/{id}` is the canonical replay authority
- **Impact**: Minimal (development-only; production should use QCG replay)

### 3. Telemetry Export is Stubbed (Awaiting Platform Contract)
- **Behavior**: TelemetryAdapter returns local dictionaries
- **Status**: Intentional; canonical backend not yet published
- **When Ready**: Remove stub, wire up live export to QCG

### 4. Platform API Transient Timeouts
- **Cause**: Cloud network latency on deployed QCG service
- **Workaround**: Tests include timeout=30 and retry logic; most resolve on retry
- **Responsibility**: QCG/Platform hosting team

---

## 11. Critical "Do Not" Rules

**These MUST never be bypassed or changed:**

1. ✋ **Do NOT fake/suppress HTTP 422 signature failure** — Document it, don't hide it
2. ✋ **Do NOT modify participant execution logic** — Participants must retain operational integrity
3. ✋ **Do NOT change service IDs** — Changing breaks capability tracking and federation
4. ✋ **Do NOT modify platform adapters** — They're mapped to official platform contracts
5. ✋ **Do NOT weaken test assertions** — Tests are the verification evidence
6. ✋ **Do NOT install untrusted SDK versions** — Always use tantra-platform-sdk==1.0.0 from official pypi
7. ✋ **Do NOT bypass evidence collection** — Evidence is the audit trail

---

## 12. Deployment Instructions

### Local Development
```bash
python insight_execution_service.py
# Runs on http://localhost:8000
# Health check: GET http://localhost:8000/api/v1/health
```

### Deploy to Render (Current Production)
```bash
# Changes auto-deploy via render.yaml:
git add .
git commit -m "Update: ..."
git push
# Render builds and deploys automatically

# Monitor: https://dashboard.render.com/
# Live: https://insight-constitutional-runtime.onrender.com
```

### Rebuild from Zero
```bash
# Complete setup for new environment
git clone <repo-url>
cd Insight_Constitutional_Runtime

python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install tantra-platform-sdk==1.0.0

# Verify
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"

# Test
pytest tests/test_execution_contract.py -v

# Run
python insight_execution_service.py
```

---

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'tantra_platform_sdk'`
```bash
pip install tantra-platform-sdk==1.0.0
python -c "from tantra_platform_sdk import PlatformCapabilitySDK"
```

### Local Tests Pass, Live Tests Fail
- Check network connectivity: `curl https://bhiv-qcg.onrender.com/qcg/health`
- Run with verbose output: `pytest tests/test_live_platform.py -vv --tb=long`
- Timeouts are transient; tests retry automatically

### `AssertionError` in Live Tests
- Verify actual platform behavior: `curl -X POST https://bhiv-qcg.onrender.com/qcg/verify -d '{"invocation_id":"test"}'`
- Do NOT modify tests to hide failures; update tests to document actual platform behavior

### Service Already Registered Message
- This is NOT an error — it means the service was previously registered
- Subsequent discovery and invocation will work normally
- Response confirms service is active

### Replay Registry Empty
- Normal if runtime hasn't executed invocations yet
- Run: `pytest tests/test_live_platform.py::test_sdk_invocation`
- `replay_registry.json` will be populated after execution

---

## 14. Current Status (2026-08-17)

| Component | Status | Evidence |
|-----------|--------|----------|
| **Runtime Participants** | LIVE VERIFIED | 3/3 executing successfully |
| **Local Execution** | VERIFIED | 12/12 contract tests ✓ |
| **Platform Discovery** | LIVE VERIFIED | SDK discovers all 3 services ✓ |
| **SDK Invocation** | LIVE VERIFIED | End-to-end execution works ✓ |
| **Replay Lineage** | LIVE VERIFIED | HTTP 200 with VALID verdict ✓ |
| **Verify Endpoint** | BLOCKED | HTTP 422 (platform signature issue) |
| **Platform Health** | UP | QCG responding to health checks ✓ |
| **All Tests** | 17/17 PASSING | Execution contract (12) + Live (5) ✓ |
| **Deployment** | LIVE | https://insight-constitutional-runtime.onrender.com |
| **Documentation** | CURRENT | All paths and endpoints verified |

---

## 15. What Requires External Platform Changes

1. **ECDSA Signature Verification** (QCG Team)
   - Resolve trust stage verification failure
   - Impact: `/qcg/verify` endpoint success

2. **Canonical Telemetry Backend** (Platform Team)
   - Publish telemetry ingestion contract
   - Impact: Enable live trace export

3. **Manifest Forwarding** (Platform Team)
   - Update registration handler
   - Impact: Preserve manifest metadata

---

## 16. For New Engineers

**Next Steps:**
1. Read this guide (sections 1-5)
2. Run `python -m venv venv && source venv/bin/activate`
3. Run `pip install -r requirements.txt && pip install tantra-platform-sdk==1.0.0`
4. Run `pytest -v` and verify 17/17 PASSED
5. Start runtime: `python insight_execution_service.py`
6. Explore: Read `docs/ARCHITECTURE.md`, `docs/INTEGRATION.md`, `contracts/`

**Resources:**
- `docs/ARCHITECTURE.md` — System design
- `docs/INTEGRATION.md` — Platform contracts
- `tests/test_live_platform.py` — Integration examples
- `evidence_packet/` — Complete audit trail
- `docs/REVIEW_INDEX.md` — Evidence mapping

---

**Last Updated**: 2026-08-17  
**Status**: ✓ All 17 tests passing  
**Ready for Handover**: ✓