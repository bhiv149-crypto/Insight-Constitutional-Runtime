# Insight Constitutional Runtime

**Status**: LIVE VERIFIED — Replay lineage valid (HTTP 200); `/qcg/verify` halted at Trust stage (`INVALID_SIGNATURE`)

---

## What This Is

The **Insight Constitutional Runtime** integrates three Insight Stack intelligence participants
(`InsightFlow`, `InsightBridge`, `InsightCore`) into the **BHIV Constitutional Platform** as
reusable, schema-compliant runtime participants.

The runtime uses a thin adapter architecture — it delegates platform-level concerns
(registration, discovery, invocation, replay, telemetry) to canonical Platform services
via dedicated adapters in `src/platform/`.

**Repository contains:**
- Three executable intelligence participants (InsightFlow, InsightBridge, InsightCore)
- Thin platform adapter layer (`src/platform/`)
- Live platform integration evidence (`evidence_packet/`)
- Replay lineage verification against the canonical QCG authority
- Local Marine Quantum Runtime integration via InsightBridge

**Repository does NOT contain:**
- The Platform Runtime itself (external — `bhiv-qcg.onrender.com`)
- The Platform SDK source (external — `tantra-platform-sdk`)
- Canonical Telemetry Backend (external — stub only; contract not published)
- Production Quantum Runtime deployment (local mode only)

---

## Quick Start

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
pip install tantra-platform-sdk==1.0.0

# Verify SDK
python -c "from tantra_platform_sdk import PlatformCapabilitySDK; print('SDK OK')"

# Run tests
pytest -v
# Recorded baseline: 27 passed, 3 warnings (live tests require QCG connectivity; a rerun may fail on QCG timeout or registration state)

# Start local server (optional)
python insight_execution_service.py
# Runs on http://localhost:8003
```

---

## Architecture

```
┌──────────────────────────────────────────────┐
│  Insight Execution Service (This Repository) │
│  - InsightFlow, InsightBridge, InsightCore   │
│  - Thin platform adapters (src/platform/)    │
│  - Local Marine Quantum (InsightBridge only) │
└───────────┬──────────────────────────────────┘
            │
    (PlatformCapabilitySDK / tantra-platform-sdk)
            │
    ┌───────▼──────────────────────┐
    │  BHIV QCG Platform           │
    │  (External Service)          │
    │  - Registry / Discovery      │
    │  - Replay Lineage Authority  │
    │  - Trust Verification (*)    │
    └──────────────────────────────┘

(*) /qcg/verify halted at Trust stage — platform ECDSA issue
```

---

## Three Participants

| Service ID | Name | Version | Role | Status |
|---|---|---|---|---|
| `insightflow.runtime.intelligence.v1` | InsightFlow | 1.0.2 | Workflow orchestration | ACTIVE |
| `insightbridge.runtime.intelligence.v1` | InsightBridge | 1.0.2 | Cross-domain messaging + Quantum gateway | ACTIVE |
| `insightcore.runtime.intelligence.v1` | InsightCore | 1.0.2 | Deterministic state validation | ACTIVE |

Live health:
```
GET https://insight-constitutional-runtime.onrender.com/api/v1/health/{service_id}
→ { status: UP, version: 1.0.2, state: ACTIVE }
```

---

## Test Status

| Test Suite | Count | Environment | Status |
|-----------|-------|-------------|--------|
| `test_execution_contract.py` | 12 | Local | ✓ Always pass |
| `test_insightbridge_quantum.py` | 4 | Local | ✓ Always pass |
| `test_quantum_adapter.py` | 6 | Local | ✓ Always pass |
| `test_live_platform.py` | 5 | Live (QCG) | ✓ Pass when QCG reachable; may timeout on cold start |
| **Total** | **27** | — | **27 passed, 3 warnings (stable run)** |

**Run**: `pytest -v`

**3 warnings** (NOT failures):
- `asyncio_default_fixture_loop_scope` unset (pytest-asyncio deprecation)
- `import python_multipart` (Starlette pending deprecation)
- `on_event is deprecated` (FastAPI lifespan deprecation)

---

## Live Integration Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Runtime Health** | VERIFIED-LIVE | All 3 participants UP/ACTIVE |
| **Platform Registration** | VERIFIED-LIVE | All 3 registered; `ALREADY_REGISTERED` = idempotent (not a failure) |
| **Platform Discovery** | VERIFIED-LIVE | All 3 discoverable via SDK |
| **SDK Invocation** | VERIFIED-LIVE | 3/3 SUCCESS via `PlatformCapabilitySDK` |
| **Replay Lineage** | VERIFIED-LIVE | `GET /qcg/replay/lineage/{id}` → HTTP 200, VALID verdict |
| **Trust Verification** | PARTIALLY-VERIFIED | `POST /qcg/verify` → HTTP 422 (Trust stage ECDSA failure) |
| **Telemetry** | VERIFIED-LOCAL | `TraceStore` stub — no live backend configured |
| **Quantum** | VERIFIED-LOCAL | Marine Quantum Runtime — local subprocess only |

---

## Known Limitations

### 1. InsightFlow Live Service — Naming Inconsistency
`GET https://insight-flow-f5j4.onrender.com/health` returns `{ "service": "InsightBridge" }`.
The endpoint is reachable and healthy, but the self-reported service name does not match the URL.
This is an open finding — not resolved by available evidence.

### 2. `/qcg/verify` — Trust Stage Halted (HTTP 422)
`POST /qcg/verify` halts with `INVALID_SIGNATURE` at the Trust stage.
Replay stage passes (`VALID`). This is a platform-level ECDSA issue, not a runtime bug.
Replay lineage (`GET /qcg/replay/lineage/{id}`) works independently.

### 3. Telemetry — Local Stub Only
`PlatformTelemetryAdapter` uses `TraceStore` from `src/platform/stubs.py`.
All telemetry returns local dictionaries. No live backend configured.
Live InsightBridge `/ingest` endpoint is separately verified and is distinct from Platform telemetry.

### 4. Quantum — Local Mode Only
Marine Quantum Runtime runs as a local subprocess.
No production cloud Quantum deployment exists.

### 5. `/enforce` — Partial Contract
The OpenAPI at `https://insight-flow-f5j4.onrender.com/openapi.json` exposes `/enforce` (requires Bearer auth).
Request/response schema is empty in the spec. Full enforcement integration NOT verified.

### 6. InsightCore — No External Adapter
InsightCore is fully integrated via Platform. No dedicated `insightcore_adapter.py` or external InsightCore service exists. This is by design for the current architecture.

### 7. QCG Transient Network Timeouts
Live tests may fail with `ReadTimeout` when QCG is cold-starting. This is transient — retry resolves it.

---

## Key Endpoints

### Live Runtime (deployed on Render)
```
POST  https://insight-constitutional-runtime.onrender.com/api/v1/execute
GET   https://insight-constitutional-runtime.onrender.com/api/v1/health
GET   https://insight-constitutional-runtime.onrender.com/api/v1/health/{service_id}
GET   https://insight-constitutional-runtime.onrender.com/api/v1/services
GET   https://insight-constitutional-runtime.onrender.com/openapi.json
```

### BHIV QCG Platform
```
GET   https://bhiv-qcg.onrender.com/registry/platform/v1/services
POST  https://bhiv-qcg.onrender.com/registry/platform/v1/register
POST  https://bhiv-qcg.onrender.com/qcg/verify
GET   https://bhiv-qcg.onrender.com/qcg/replay/lineage/{invocation_id}
```

### Local Development
```
POST  http://localhost:8003/api/v1/execute
GET   http://localhost:8003/api/v1/health
GET   http://localhost:8003/docs
```

---

## Documentation Map

| Document | Purpose |
|----------|---------|
| **`HANDOVER.md`** | Complete operational handover — start here |
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

## Evidence Location

| Evidence Type | Location | Classification |
|---------------|----------|----------------|
| Registration | `evidence_packet/api_samples/` | VERIFIED-LIVE |
| Discovery | `evidence_packet/api_samples/discovered_services.json` | VERIFIED-LIVE |
| Invocation | `evidence_packet/invocation_proof/` | VERIFIED-LIVE |
| Replay | `evidence_packet/replay_evidence/` | VERIFIED-LIVE |
| Quantum | `evidence_packet/quantum_evidence/` | VERIFIED-LOCAL |
| Telemetry | `evidence_packet/telemetry/` | STUB-DERIVED |
| Deployment | `evidence_packet/deployment_proof/` | VERIFIED-LIVE |

---

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| `ModuleNotFoundError: tantra_platform_sdk` | SDK not installed | `pip install tantra-platform-sdk==1.0.0` |
| Live tests timeout | QCG cold start / Render latency | Retry — transient instability; resolves on retry |
| `ALREADY_REGISTERED` on registration | Service already registered at that version | Not an error — idempotent. Discovery and invocation proceed normally |
| Live tests show `SERVICE_NOT_FOUND` | Services not registered in QCG on this cold start | Re-register via `PlatformIntegrationService` then retry |

---

## Final Status

**27 passed, 3 warnings** (stable local + live run)

🟢 **VERIFIED-LIVE**: Registration, discovery, SDK invocation, health, replay lineage.
🟡 **VERIFIED-LOCAL**: Quantum (Marine, local subprocess), SDK evidence chain (session-scoped).
⚠ **PARTIALLY-VERIFIED**: `/qcg/verify` — Replay VALID, Trust HALTED (HTTP 422, ECDSA).
⚪ **NOT ESTABLISHED**: Live telemetry export, production Quantum, `/enforce` contract.

Full ecosystem convergence and Production Certification are **not yet claimed**.

---

**Last Updated**: 2026-08-19
**See** [HANDOVER.md](HANDOVER.md) for complete operational details.

## Status Vocabulary

`VERIFIED-LIVE` means observed against a reachable external endpoint or live integration
run. `VERIFIED-LOCAL` means proven by local code, tests, or a local subprocess. `PENDING-CONTRACT`
means required external request/response information is unavailable. These terms are used
throughout the documentation to keep local, live, mocked, and unestablished behavior distinct.

The current boundary is precise: registration, discovery, invocation, health, failure paths,
and replay lineage retrieval are live-verified; Platform telemetry is local `TraceStore`,
Quantum is local Marine runtime, `/qcg/verify` halts at Trust with HTTP 422, and `/enforce`
has no verified payload or response schema. Production certification is not claimed.
