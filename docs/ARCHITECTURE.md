# System Architecture Specification

## Overview

The **Insight Constitutional Runtime Architecture** defines how the Insight Stack operates as reusable, schema-compliant Constitutional Runtime Participants within the Intelligence Layer of the **BHIV Constitutional Platform**.

The architecture adheres strictly to a **thin adapter design pattern**. The Insight Runtime delegates platform-level capabilities—such as service discovery, registration, health monitoring, and evidence generation—to the underlying BHIV Platform via dedicated adapters, avoiding any duplication of core platform infrastructure. Replay and telemetry are currently blocked or stubbed.

---

## Architectural Principles

1. **Strict Ownership Boundaries**: Insight Runtime owns participant business intelligence, execution lifecycle, and contract declarations. The BHIV Platform owns service registration, capability discovery, replay deduplication, telemetry storage, and trust verification.
2. **Thin Adapter Delegation**: Participant interactions with the platform pass exclusively through thin adapter wrappers located in `src/platform/`.
3. **Evidence & Determinism**: Every participant execution emits local evidence. Canonical replay reconstruction is NOT yet verified.
4. **Resilient Network Protocol**: All REST communication with live platform endpoints (`https://bhiv-qcg.onrender.com`) incorporates fallback handlers to handle cloud network latency cleanly. QCG exhibits transient timeouts.

---

## Component Architecture

```mermaid
graph TD
    subgraph Intelligence Layer - Insight Runtime
        IF["InsightFlow Participant<br/>(Workflow Orchestration)"]
        IB["InsightBridge Participant<br/>(Cross-Domain Messaging)"]
        IC["InsightCore Participant<br/>(Deterministic State Validation)"]
    end

    subgraph Integration & Adapter Layer
        PIS[PlatformIntegrationService]
        
        subgraph Platform Adapters (src/platform/)
            PA[PlatformRuntimeAdapter]
            SDK[PlatformSDKAdapter]
            RA[PlatformRegistryAdapter]
            DA[PlatformDiscoveryAdapter]
            REP[PlatformReplayAdapter]
            HA[PlatformHealthAdapter]
            TA[PlatformTelemetryAdapter]
        end
    end

    subgraph BHIV Platform Infrastructure
        SDK_CORE[PlatformCapabilitySDK]
        REG_SRV["Platform Registry<br/>(POST /v1/register)"]
        CAP_SRV["Capability Registry<br/>(POST /register)"]
        DISC_SRV["Discovery Service<br/>(GET /v1/services)"]
        REPLAY_SRV[CanonicalReplayAuthority — BLOCKED: 404 / submit() missing]
        OTEL_SRV[OpenTelemetry Trace Store]
    end

    IF & IB & IC --> PIS
    PIS --> PA
    PA --> SDK & RA & DA & REP & HA & TA
    SDK --> SDK_CORE
    RA --> REG_SRV & CAP_SRV
    DA --> DISC_SRV
    REP --> REPLAY_SRV
    TA --> OTEL_SRV
```

---

## Participant Specifications

| Attribute | InsightFlow | InsightBridge | InsightCore |
|---|---|---|---|
| **Runtime Identity** | `insightflow.runtime.intelligence.v1` | `insightbridge.runtime.intelligence.v1` | `insightcore.runtime.intelligence.v1` |
| **Classification** | Domain Service | Domain Service | Domain Service |
| **Capability Category** | Intelligence | Intelligence | Intelligence |
| **Primary Function** | Workflow orchestration & trace generation | Cross-domain messaging & gateway protocol translation | Deterministic state validation & replay enforcement |
| **Dependencies** | `PlatformCapabilitySDK`, `PlatformDiscovery`, `PlatformRegistry`, `RuntimeCore` | `PlatformCapabilitySDK`, `PlatformDiscovery`, `RuntimeCore`, `QuantumCommunicationGateway` | `PlatformCapabilitySDK`, `PlatformDiscovery`, `RuntimeCore`, `ReplayRegistry` |

---

## Responsibility Matrix

| Feature / Concern | Insight Runtime Ownership | BHIV Platform Ownership |
|---|---|---|
| **Participant Execution** | **OWNED** (Executes intelligence logic) | Not Owned |
| **Service Registration** | Delegates via `PlatformRegistryAdapter` | **OWNED** (Persists `PlatformServiceRecord`) |
| **Capability Discovery** | Delegates via `PlatformDiscoveryAdapter` | **OWNED** (Maintains active capability catalog) |
| **Replay Deduplication** | Delegates via `PlatformReplayAdapter` | **OWNED** (Validates sequence via canonical QCG replay — BLOCKED: endpoint returns 404, adapter missing submit()) |
| **Telemetry & Observability**| Delegates via `PlatformTelemetryAdapter` | **OWNED** (Exports & stores trace spans — ⚪ NOT EXPOSED: local stub TraceStore only) |
| **Health Monitoring** | Returns internal participant state | **OWNED** (Aggregates platform health endpoints) |

---

## Runtime Interaction Sequence

```mermaid
sequenceDiagram
    autonumber
    participant IF as InsightFlow Participant
    participant Adapt as PlatformRuntimeAdapter
    participant SDK as PlatformCapabilitySDK
    participant Plat as BHIV Platform Service

    IF->>Adapt: register(record, manifest)
    Adapt->>Plat: POST /registry/platform/v1/register
    Plat-->>Adapt: 200 OK (Registration Receipt)

    IF->>Adapt: discover_services(filters)
    Adapt->>Plat: GET /registry/capabilities/capabilities
    Plat-->>Adapt: 200 OK ([Service Catalog])

    IF->>Adapt: invoke_capability(service_id, operation, payload)
    Adapt->>SDK: execute_capability(service_id, operation, payload)
    SDK->>Plat: POST /qcg/verify (or direct execution endpoint)
    Plat-->>SDK: 200 OK (Execution Result with invocation_id)
    SDK-->>Adapt: InvocationResult
    Adapt-->>IF: Invocation Result + Local Evidence
    Note: Telemetry ack is local stub only
```

---

## Validation Status

* **Internal Readiness Test**: `17 PASSED` in module/import checks. `12 PASSED` in execution contract tests.
* **Live Integration Execution**: Verified against `https://bhiv-qcg.onrender.com` for registration, discovery, health, and invocation. QCG exhibits transient network instability.
* **Replay Status**: NOT VERIFIED — canonical lineage endpoint returns 404; `PlatformReplayAdapter.submit()` missing.
* **Telemetry Status**: LOCAL STUB ONLY — `TraceStore` returns local dictionaries; no live backend configured.
* **Shared Platform Services Notice**: Full hardware-level governance certification depends on the availability of the shared BHIV Constitutional Runtime services.
