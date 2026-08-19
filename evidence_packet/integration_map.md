# Insight Stack — Integration Map

**Version**: 1.0.2  
**Release**: Live Runtime Convergence — 2026-08-14

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BHIV PLATFORM RUNTIME                        │
│                  (https://bhiv-qcg.onrender.com)                │
│                                                                 │
│  ┌─────────────────────┐    ┌───────────────────────────────┐  │
│  │   Platform Registry  │    │     Capability Registry       │  │
│  │   /registry/platform │    │    /registry/capabilities     │  │
│  │                      │    │                               │  │
│  │  POST /v1/register   │    │  POST /register              │  │
│  │  GET  /v1/services   │    │  GET  /capabilities          │  │
│  │  GET  /v1/health     │    │  GET  /discover/{name}       │  │
│  └──────────┬───────────┘    └──────────────┬────────────────┘  │
│             │                                │                  │
│  ┌──────────┴────────────────────────────────┴───────────────┐  │
│  │              PlatformCapabilitySDK (Kanishk)              │  │
│  │                                                           │  │
│  │  discover_services()   negotiate_version()                │  │
│  │  invoke_capability()   validate_manifest()                │  │
│  │  check_health()        get_federation_status()            │  │
│  │                                                           │  │
│  │  Features:                                                │  │
│  │  • Circuit breaker (CLOSED → OPEN → HALF_OPEN)            │  │
│  │  • Exponential backoff + jitter retry                     │  │
│  │  • Hash-chained invocation evidence                       │  │
│  │  • Pluggable trust provider (classical/post-quantum)      │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                   HTTP POST /api/v1/execute
                   HTTP GET  /api/v1/health
                              │
┌─────────────────────────────┼──────────────────────────────────┐
│         INSIGHT EXECUTION SERVICE (Ganesh)                      │
│         (Deployed on Render / Cloud)                            │
│                              │                                  │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │                  FastAPI Application                      │  │
│  │                                                          │  │
│  │   POST /api/v1/execute    → InvocationRequest dispatch   │  │
│  │   GET  /api/v1/health     → Aggregate participant health │  │
│  │   GET  /api/v1/health/{id}→ Per-service health           │  │
│  │   GET  /api/v1/services   → List hosted services         │  │
│  └──┬──────────────┬──────────────┬─────────────────────────┘  │
│     │              │              │                              │
│  ┌──┴──────────┐ ┌┴───────────┐ ┌┴──────────┐                  │
│  │ InsightFlow │ │InsightBridge│ │InsightCore│                  │
│  │             │ │            │ │           │                  │
│  │ workflow    │ │ bridge     │ │ analysis  │                  │
│  │ orchestrate │ │ trace prop │ │ knowledge │                  │
│  │ evidence    │ │ event fwd  │ │ replay    │                  │
│  └─────────────┘ └────────────┘ └───────────┘                  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Platform Adapters (Thin Wrappers)            │  │
│  │                                                          │  │
│  │  SDKAdapter → PlatformCapabilitySDK                      │  │
│  │  RegistryAdapter → LivePlatformClient                    │  │
│  │  DiscoveryAdapter → SDK discover_services()              │  │
│  │  HealthAdapter → SDK check_health() + Registry health    │  │
│  │  ReplayAdapter → QCG Replay Lineage (HTTP 200 / VALID)                 │  │
│  │  TelemetryAdapter → TraceStore (LOCAL STUB ONLY)         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Workflow (PlatformIntegrationService)

```
PlatformIntegrationService.integrate()
    │
    ├── 1. _create_participants()
    │       → InsightFlowParticipant()
    │       → InsightBridgeParticipant()
    │       → InsightCoreParticipant()
    │
    ├── 2. _register_runtime()
    │       → RegistrationBuilder.build_service_record()
    │       → LivePlatformClient.register_runtime()
    │       → POST /registry/platform/v1/register
    │
    ├── 3. _register_capabilities()
    │       → RegistrationBuilder.build_capability_manifest()
    │       → LivePlatformClient.register_capability()
    │       → POST /registry/capabilities/register
    │
    ├── 4. _discover_services()
    │       → LivePlatformClient.list_services()
    │       → GET /registry/platform/v1/services
    │
    ├── 5. _negotiate_versions()
    │       → PlatformSDKAdapter.negotiate_version()
    │
    ├── 6. _invoke_capabilities()
    │       → PlatformSDKAdapter.invoke_capability()
    │       → SDK evidence chain records
    │
    ├── 7. _check_health()
    │       → PlatformSDKAdapter.check_health()
    │
    ├── 8. _validate_replay()
    │       → QCG /qcg/replay/lineage/{trace_id} returns HTTP 200 / VALID
    │       → Local duplicate authority is a separate VERIFIED-LOCAL path
    │
    ├── 9. _record_telemetry()
    │       → PlatformTelemetryAdapter.record_*()
    │       → ⚪ LOCAL STUB ONLY: TraceStore returns local dictionaries
    │
    ├── 10. _exercise_failure_paths()
    │        → Invoke ghost service → SERVICE_NOT_FOUND
    │        → Negotiate v999.0.0 → UNSUPPORTED
    │        → Invoke invalid_operation → FAILED/INVALID_OP
    │
    └── 11. _generate_evidence()
             → Write all JSON evidence files
             → Write production readiness report
```

---

## Team Dependency Map

| Component | Owner | Depends On | API Endpoint |
|---|---|---|---|
| **InsightFlow** | Ganesh | SDK, Registry, Discovery | `/api/v1/execute` (service_id=insightflow.runtime.intelligence.v1) |
| **InsightBridge** | Ganesh | SDK, Registry, Discovery, QCG | `/api/v1/execute` (service_id=insightbridge.runtime.intelligence.v1) |
| **InsightCore** | Ganesh | SDK, Registry, Discovery, Replay | `/api/v1/execute` (service_id=insightcore.runtime.intelligence.v1) |
| **Platform Runtime** | Kanishk | — | `https://bhiv-qcg.onrender.com/registry/platform/v1/*` |
| **Capability Registry** | Kanishk | — | `https://bhiv-qcg.onrender.com/registry/capabilities/*` |
| **PlatformCapabilitySDK** | Kanishk | Registry, Capabilities | Python SDK |
| **Quantum Platform Services** | Pritesh | — | QCG endpoints |
| **Quantum Runtime** | Dhiraj | Quantum Platform | Runtime execution |
| **Core Runtime / Governance** | Raj | — | Governance contracts |
| **Testing / Certification** | Vinayak | All above | Test harness |

---

## Known Integration Dependencies

1. **INSIGHT_SERVICE_URL** must be set to a public URL before registration
2. **BHIV Platform** must be running (cold-start may clear registry)
3. **PlatformCapabilitySDK** must be importable (bundled in project root)
4. **requests** library required for LivePlatformClient HTTP calls
5. **fastapi + uvicorn** required for execution service hosting
