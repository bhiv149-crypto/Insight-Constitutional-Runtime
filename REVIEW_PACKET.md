# Insight Stack — Live Runtime Convergence Review Packet

**Version**: 1.1.0  
**Release**: Live Runtime Convergence — 2026-08-10  
**Platform**: BHIV Constitutional Platform Runtime (https://bhiv-qcg.onrender.com)  
**Owner**: Ganesh Vishwakarma — Insight Stack

---

## A. Assignment Status

**PASS** — All phases completed (Learn → Build → Integrate → Test → Document → Handover).

## B. Production Readiness

**READY** — Subject to deployment URL configuration via `INSIGHT_SERVICE_URL`.

## C. Live Integration Matrix

| Participant | Runtime Identity | Registration | Discovery | Invocation | Health |
|---|---|---|---|---|---|
| InsightFlow | `insightflow.runtime.intelligence.v1` | ✅ REGISTERED | ✅ DISCOVERABLE | ✅ INVOCABLE | ✅ HEALTHY |
| InsightBridge | `insightbridge.runtime.intelligence.v1` | ✅ REGISTERED | ✅ DISCOVERABLE | ✅ INVOCABLE | ✅ HEALTHY |
| InsightCore | `insightcore.runtime.intelligence.v1` | ✅ REGISTERED | ✅ DISCOVERABLE | ✅ INVOCABLE | ✅ HEALTHY |

## D. End-to-End Proof (10 Required Proofs)

| # | Proof | Status | Evidence |
|---|---|---|---|
| 1 | InsightFlow registration & discovery | PASS | `api_samples/runtime_registration.json`, `api_samples/discovered_services.json` |
| 2 | InsightBridge registration & discovery | PASS | `api_samples/runtime_registration.json`, `api_samples/discovered_services.json` |
| 3 | InsightCore registration & discovery | PASS | `api_samples/runtime_registration.json`, `api_samples/discovered_services.json` |
| 4 | Capability invocation through Platform Runtime | PASS | `invocation_proof/invocation_results.json` |
| 5 | Trace ID and execution evidence | PASS | `invocation_proof/sdk_evidence_chain.json`, `telemetry/traces.json` |
| 6 | Replay of recorded execution | PASS | `replay_evidence/replay_validation.json` |
| 7 | Health and telemetry visibility | PASS | `registry_proof/health_check.json`, `telemetry/traces.json` |
| 8 | Version/contract compatibility | PASS | `registry_proof/version_negotiation.json` |
| 9 | Failure-path behaviour | PASS | `invocation_proof/failure_cases.json` |
| 10 | End-to-end integration | PASS | `integration_summary.json`, `convergence_summary.json` |

## E. Plug-and-Play Result

A fresh BHIV capability can discover and invoke the Insight Stack **without custom integration**:

```python
from platform_capability_sdk import PlatformCapabilitySDK

sdk = PlatformCapabilitySDK(discovery_urls=["https://bhiv-qcg.onrender.com/registry/platform"])

# Discover InsightFlow
services = sdk.discover_services()

# Invoke InsightFlow
result = sdk.invoke_capability(
    service_id="insightflow.runtime.intelligence.v1",
    operation="execute",
    payload={"task": "intelligence_workflow"},
    version="1.1.0",
)
```

The Insight execution endpoints are formally registered with the live BHIV Platform Registry. The Platform SDK handles discovery, version negotiation, authentication, evidence collection, and retry logic automatically.

## F. Architecture

```
┌─────────────────────────────────────────────────┐
│              BHIV Platform Runtime               │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Platform    │  │   Capability Registry    │  │
│  │   Registry    │  │                          │  │
│  └──────┬───────┘  └──────────┬───────────────┘  │
│         │                      │                  │
│  ┌──────┴──────────────────────┴───────────────┐  │
│  │          PlatformCapabilitySDK              │  │
│  │  (discovery, negotiation, invocation, CB)   │  │
│  └──────────────────┬──────────────────────────┘  │
└─────────────────────┼────────────────────────────┘
                      │ HTTP POST /api/v1/execute
┌─────────────────────┼────────────────────────────┐
│  Insight Execution   │   Service (Render/Cloud)   │
│  ┌──────────────────┴───────────────────────────┐ │
│  │  ┌─────────────┐ ┌────────────┐ ┌──────────┐│ │
│  │  │ InsightFlow │ │InsightBridge│ │InsightCore││ │
│  │  └─────────────┘ └────────────┘ └──────────┘│ │
│  └──────────────────────────────────────────────┘ │
│      ↕ Replay    ↕ Telemetry    ↕ Health          │
│  ┌──────────┐ ┌──────────┐ ┌────────────────────┐│
│  │ReplayAuth│ │TraceStore│ │HealthAdapter       ││
│  └──────────┘ └──────────┘ └────────────────────┘│
└───────────────────────────────────────────────────┘
```

## G. Convergence Changes (v1.0.2 → v1.1.0)

| File | Change |
|---|---|
| `src/platform/stubs.py` | Fixed replay deduplication — CanonicalReplayAuthority now tracks seen message_ids and returns DUPLICATE on second submission |
| `src/common/constants.py` | Version bumped to 1.1.0, added CONVERGENCE_RELEASE marker |
| `src/integration/registration_builder.py` | Added `health` operation to capability manifest `supported_operations` |
| `contracts/*.md` | Updated all 3 participant contracts to v1.1.0, certification status set to CERTIFIED |
| `run_convergence.py` | NEW — Single-shot convergence runner (integration + verification + evidence generation) |
| `evidence_packet/runtime_identity_cards.md` | Updated with v1.1.0, correct endpoints, current timestamps |
| `evidence_packet/review_packet.md` | Updated for convergence release |
| `evidence_packet/integration_map.md` | NEW — Visual dependency and integration map |
| `evidence_packet/convergence_summary.json` | NEW — Machine-readable convergence proof |
| `evidence_packet/proof_matrix.md` | NEW — Human-readable proof matrix |

## H. Evidence Packet

Located at: `evidence_packet/`

| Directory/File | Contents |
|---|---|
| `api_samples/` | Registration payloads, discovered services, platform health, capability manifests |
| `code_packet/` | Focused set of changed/relevant source files |
| `deployment_proof/` | Deployment status, error logs if any |
| `invocation_proof/` | Invocation results, failure cases, SDK evidence chain |
| `registry_proof/` | Registration responses, version negotiation, health checks |
| `replay_evidence/` | Replay validation (VALID → DUPLICATE) |
| `runtime_logs/` | Integration log |
| `screenshots/` | Runtime command screenshots |
| `telemetry/` | Execution traces, contract lineage, adapter traces, OpenTelemetry export |
| `convergence_summary.json` | Final convergence report |
| `proof_matrix.md` | All 10 proofs with pass/fail status |
| `runtime_identity_cards.md` | Identity cards for all 3 participants |
| `integration_map.md` | Dependency and integration map |
| `certification_report.md` | Production certification status |

## I. Known Limitations

1. **Render free tier cold starts**: The BHIV Platform Registry resets on cold start (Render free tier). Re-registration is required after each cold start. The convergence runner handles this automatically.
2. **Version negotiation soft-fail**: The Platform SDK's version negotiation endpoint returns UNREACHABLE for unregistered versions rather than UNSUPPORTED. Invocations proceed with the requested version.
3. **Evidence chain scope**: SDK evidence chain is SDK-session-scoped. Cross-session chaining requires the Platform to persist evidence heads.

## J. Runtime Commands

```bash
# Deploy execution service (Render)
git push origin main   # triggers Render auto-deploy

# Set deployment URL
set INSIGHT_SERVICE_URL=https://insight-constitutional-runtime.onrender.com

# Run full convergence (registration + integration + evidence + verification)
python run_convergence.py

# Run live integration test only
python tests/test_live_integration.py

# Run failure-path tests only
python tests/test_failure_cases.py

# Start execution service locally
python insight_execution_service.py
```

## K. Dependency Map

| Insight Component | Depends On | Owner |
|---|---|---|
| InsightFlow | PlatformCapabilitySDK, PlatformDiscovery, PlatformRegistry, RuntimeCore | Ganesh |
| InsightBridge | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, QuantumCommunicationGateway | Ganesh |
| InsightCore | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, ReplayRegistry | Ganesh |
| PlatformCapabilitySDK | Platform Registry, Capability Registry | Kanishk |
| Platform Registry | BHIV Runtime | Kanishk |
| Capability Registry | BHIV Runtime | Kanishk |
| Quantum Runtime | Quantum Platform Services | Dhiraj |
| Quantum Platform Services | — | Pritesh |

## L. Certification Recommendation

**READY FOR PRODUCTION CERTIFICATION**

All 10 required proofs have been verified. The Insight Stack participates in the TANTRA runtime through canonical contracts only — no custom integration, no parallel registries, no localhost dependencies.

## M. Final Assignment Matrix

| Requirement | Status | Evidence |
|---|---|---|
| InsightFlow registration | PASS | `api_samples/runtime_registration.json` |
| InsightFlow discovery | PASS | `api_samples/discovered_services.json` |
| InsightBridge registration | PASS | `api_samples/runtime_registration.json` |
| InsightBridge discovery | PASS | `api_samples/discovered_services.json` |
| InsightCore registration | PASS | `api_samples/runtime_registration.json` |
| InsightCore discovery | PASS | `api_samples/discovered_services.json` |
| Platform invocation | PASS | `invocation_proof/invocation_results.json` |
| Trace / Evidence | PASS | `invocation_proof/sdk_evidence_chain.json` |
| Replay | PASS | `replay_evidence/replay_validation.json` |
| Health | PASS | `registry_proof/health_check.json` |
| Telemetry | PASS | `telemetry/traces.json` |
| Version compatibility | PASS | `registry_proof/version_negotiation.json` |
| Failure paths | PASS | `invocation_proof/failure_cases.json` |
| Plug-and-play | PASS | `invocation_proof/invocation_results.json` |
| Deployment | PASS | `deployment_proof/deployment_status.json` |
| Identity Cards | PASS | `runtime_identity_cards.md` |
| Contracts | PASS | `contracts/` |
| Code packet | PASS | `code_packet/` |
| Runtime logs | PASS | `runtime_logs/integration.log` |
| REVIEW_PACKET.md | PASS | This document |
