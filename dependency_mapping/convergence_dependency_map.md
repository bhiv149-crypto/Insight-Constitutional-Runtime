# Insight Stack — Convergence Dependency Map

**Version**: 1.0.2  
**Release**: Live Runtime Convergence — 2026-08-14

---

## Runtime Dependency Graph

```
InsightFlow (Ganesh)
    ├── PlatformCapabilitySDK (Kanishk)
    ├── PlatformDiscovery (Kanishk)
    ├── PlatformRegistry (Kanishk)
    └── RuntimeCore (Raj)

InsightBridge (Ganesh)
    ├── PlatformCapabilitySDK (Kanishk)
    ├── PlatformDiscovery (Kanishk)
    ├── RuntimeCore (Raj)
    └── QuantumCommunicationGateway (Pritesh/Dhiraj)

InsightCore (Ganesh)
    ├── PlatformCapabilitySDK (Kanishk)
    ├── PlatformDiscovery (Kanishk)
    ├── RuntimeCore (Raj)
    └── ReplayRegistry (Kanishk)
```

---

## Package Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | ≥0.110.0 | Execution service framework |
| `uvicorn[standard]` | ≥0.30.0 | ASGI server |
| `requests` | ≥2.31.0 | HTTP client for platform communication |
| `pydantic` | ≥2.0.0 | Request/response models |

---

## API Contract Dependencies

| API | Base URL | Owner | Used By |
|---|---|---|---|
| Platform Registry | `https://bhiv-qcg.onrender.com/registry/platform` | Kanishk | LivePlatformClient |
| Capability Registry | `https://bhiv-qcg.onrender.com/registry/capabilities` | Kanishk | LivePlatformClient |
| Platform SDK | `https://bhiv-qcg.onrender.com/qcg` | Kanishk | PlatformSDKAdapter |
| Insight Execution | `{INSIGHT_SERVICE_URL}/api/v1/*` | Ganesh | Platform SDK (callback) |

---

## Team Integration Matrix

| From → To | Ganesh | Kanishk | Pritesh | Dhiraj | Raj | Vinayak |
|---|---|---|---|---|---|---|
| **Ganesh** | — | SDK, Registry, Discovery | Quantum Services | Quantum Runtime | RuntimeCore | Certification |
| **Kanishk** | Execution endpoints | — | | | | |
| **Pritesh** | | | — | | | |
| **Dhiraj** | | | | — | | |
| **Raj** | | | | | — | |
| **Vinayak** | Test results | | | | | — |

---

## Known Limitations

1. **Render cold starts**: Platform Registry clears on cold start — convergence runner re-registers automatically
2. **Session-scoped evidence**: SDK evidence chain resets per SDK instance — cross-session chaining is Platform responsibility
3. **Version negotiation**: Soft-fails to UNREACHABLE rather than UNSUPPORTED for unregistered services
4. **Quantum integration**: End-to-end Quantum Runtime integration depends on Pritesh/Dhiraj runtime availability
