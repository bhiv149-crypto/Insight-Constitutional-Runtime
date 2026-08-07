# Engineering Handover Guide

## Purpose

The **Engineering Handover Guide** provides incoming maintainers, system integrators, and security reviewers with complete technical context, operational procedures, repository maps, and deployment instructions for the **Insight Constitutional Runtime**.

---

## Repository Directory & Component Structure

```
Insight_Constitutional_Runtime/
├── src/
│   ├── common/                      # Core models and BaseParticipant class
│   │   ├── base_participant.py
│   │   ├── models.py
│   │   └── constants.py
│   ├── participants/                # Intelligence Layer Participants
│   │   ├── insightflow/             # Workflow orchestration logic
│   │   ├── insightbridge/           # Cross-domain gateway logic
│   │   └── insightcore/             # Deterministic state validation logic
│   ├── platform/                    # Thin platform adapters
│   │   ├── live_platform_client.py  # REST client targeting https://bhiv-qcg.onrender.com
│   │   ├── sdk_adapter.py           # PlatformCapabilitySDK wrapper
│   │   ├── registry_adapter.py      # PlatformRegistry wrapper
│   │   ├── discovery_adapter.py     # PlatformDiscovery wrapper
│   │   ├── replay_adapter.py        # CanonicalReplayAuthority wrapper
│   │   ├── health_adapter.py        # Health endpoint wrapper
│   │   └── telemetry_adapter.py     # OpenTelemetry trace wrapper
│   └── integration/                 # Integration orchestration framework
│       ├── platform_integration_service.py
│       └── registration_builder.py
├── contracts/                       # Declarative constitutional contracts
├── runtime_identity/                # Formal participant identity cards
├── dependency_mapping/              # Platform dependency declarations
├── evidence_packet/                 # Audit proofs, validation reports, certification
├── docs/                            # Specifications, integration proofs, handover guide
└── tests/                           # Repository readiness test suite (17/17 passed)
```

---

## Component Ownership & Responsibility

| Directory / Layer | Primary Responsibility | Maintenance Notes |
|---|---|---|
| `src/participants/` | Business intelligence for `InsightFlow`, `InsightBridge`, and `InsightCore`. | Owned strictly by the Insight Stack team. |
| `src/platform/` | Thin adapter wrappers interface with Platform APIs over REST. | Must conform 100% to upstream BHIV platform contract schemas. |
| `src/integration/` | End-to-end integration harness and REST client payload builder. | Maintains `LivePlatformClient` and orchestrates integration phases. |
| `contracts/` | Declarative contract specifications. | Read-only governance specifications. |
| `tests/` | Internal readiness test suite. | Run `python tests/test_integration_readiness.py` before any release. |

---

## Operational Runbook & Deployment Notes

### 1. Internal Validation
Run the internal readiness check suite:
```bash
python tests/test_integration_readiness.py
```
*Verify that all 17 checks report `[PASS]`.*

### 2. Executing Live Platform Integration
To run full registration, discovery, replay, and telemetry verification against the live server:
```bash
python -c "from src.integration.platform_integration_service import PlatformIntegrationService; print(PlatformIntegrationService().integrate())"
```

### 3. Monitoring Live Endpoints
* **Platform Registry Health**: `GET https://bhiv-qcg.onrender.com/registry/platform/v1/health`
* **Capability Catalog**: `GET https://bhiv-qcg.onrender.com/registry/capabilities/capabilities`

---

## Future Maintenance Roadmap

1. **Production Hardware Certification**: Full hardware-level governance certification depends on the availability of the shared BHIV Constitutional Runtime services.
2. **Schema Synchronization**: Periodically verify that `LivePlatformClient` payload structures match any updated upstream BHIV platform contract releases.
3. **OpenTelemetry Exporter Integration**: Connect `PlatformTelemetryAdapter` to production OpenTelemetry collector instances when deployed in cluster environments.

---

## Handover Checklist

- [x] All 17 internal readiness tests passing (`python tests/test_integration_readiness.py`).
- [x] Live platform registration verified (`POST /v1/register` and `POST /register`).
- [x] Live capability discovery verified (3 services discovered).
- [x] Upstream repository `bhiv-QCG-main` remains 100% unmodified.
- [x] Zero code modifications in `src/` during documentation refinement phase.