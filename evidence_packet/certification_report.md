# Insight Stack — Production Certification Report

**Version**: 1.0.2  
**Release**: Live Runtime Convergence — 2026-08-14  
**Assessed By**: Ganesh Vishwakarma — Insight Stack

---

## Certification Status: INTEGRATED — REPLAY LINEAGE VERIFIED; TRUST AND TELEMETRY LIMITED

---

## Criteria Assessment

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | All participants register with canonical Platform Registry | ✅ PASS | `api_samples/runtime_registration.json` |
| 2 | All participants discoverable through Platform Discovery | ✅ PASS | `api_samples/discovered_services.json` |
| 3 | Capability invocation via PlatformCapabilitySDK | ✅ PASS | `invocation_proof/invocation_results.json` |
| 4 | Version negotiation through canonical SDK | ✅ PASS | `registry_proof/version_negotiation.json` |
| 5 | Replay lineage retrieval | 🟢 VERIFIED-LIVE | `replay_evidence/replay_validation.json` |
| 6 | Health and telemetry reporting | 🟢 Health: LIVE VERIFIED; ⚪ Telemetry: NOT EXPOSED | `registry_proof/health_check.json`, `telemetry/traces.json` (STUB-DERIVED) |
| 7 | Evidence chain integrity | ✅ PASS | `invocation_proof/sdk_evidence_chain.json` |
| 8 | Failure-path behaviour (graceful degradation) | ✅ PASS | `invocation_proof/failure_cases.json` |
| 9 | No custom runtime interfaces | ✅ PASS | Code review — all Platform operations delegate to adapters |
| 10 | No parallel registries or runtimes | ✅ PASS | Code review — stubs are development-only, not live registries |
| 11 | Public deployment capability | ✅ PASS | `render.yaml` configured, Render deployment ready |
| 12 | Plug-and-play discovery by fresh capabilities | ✅ PASS | Standard PlatformCapabilitySDK flow |

---

## Architecture Compliance

- **Registration**: Uses canonical `POST /registry/platform/v1/register` and `POST /registry/capabilities/register`
- **Discovery**: Uses canonical `GET /registry/platform/v1/services`
- **Invocation**: Uses `PlatformCapabilitySDK.invoke_capability()` with full pipeline (circuit breaker, retries, evidence)
- **Execution**: FastAPI service on canonical `POST /api/v1/execute` endpoint
- **Health**: Standard `GET /api/v1/health` and `GET /api/v1/health/{service_id}`
- **No localhost dependencies**: `RegistrationBuilder` enforces public URL requirement

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Render free tier cold starts clear registry | Low | Re-registration on each convergence run |
| Evidence chain is session-scoped | Low | Platform-level evidence persistence is Kanishk's responsibility |
| Version negotiation soft-fails on unregistered services | Low | Invocations proceed with requested version; failure paths tested |
| Trust-stage signature verification returns HTTP 422 | High | QCG owner must resolve `INVALID_SIGNATURE` |
| Telemetry backend not configured | High | Telemetry owner must publish canonical ingestion contract |
| Canonical replay submission contract | Pending | Lineage retrieval is proven; public submission contract is not established |

---

## Recommendation

**APPROVED FOR LIVE INTEGRATION — REPLAY LINEAGE VERIFIED; TRUST AND TELEMETRY NOT FULLY ESTABLISHED**

The Insight Stack meets criteria for live runtime participation in registration, discovery, version negotiation, invocation, execution, health, and replay lineage retrieval. `/qcg/verify` remains limited by Trust-stage `INVALID_SIGNATURE`, and live Platform telemetry storage is not established. Production certification is not claimed.