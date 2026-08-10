# Insight Stack — Runtime Identity Cards

**Live Integration Version**: 1.1.0  
**Convergence Release**: Live Runtime Convergence — 2026-08-10  
**Platform**: BHIV Constitutional Platform Runtime (https://bhiv-qcg.onrender.com)  
**All Three Participants**: REGISTERED + ACTIVE

---

## Card 1: InsightFlow

| Field | Value |
|---|---|
| **Participant Name** | InsightFlow |
| **Runtime Identity** | `insightflow.runtime.intelligence.v1` |
| **Version** | 1.1.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Supported Operations** | `execute`, `health` |
| **Execution Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/execute` |
| **Health Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/health/insightflow.runtime.intelligence.v1` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | workflow_orchestration, capability_invocation, trace_generation, evidence_generation |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, PlatformRegistry, RuntimeCore |
| **Contract Version** | v1.1.0 |
| **Certification** | CERTIFIED — 2026-08-10 |

---

## Card 2: InsightBridge

| Field | Value |
|---|---|
| **Participant Name** | InsightBridge |
| **Runtime Identity** | `insightbridge.runtime.intelligence.v1` |
| **Version** | 1.1.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Supported Operations** | `execute`, `health` |
| **Execution Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/execute` |
| **Health Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/health/insightbridge.runtime.intelligence.v1` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | runtime_bridge, trace_propagation, event_forwarding |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, QuantumCommunicationGateway |
| **Contract Version** | v1.1.0 |
| **Certification** | CERTIFIED — 2026-08-10 |

---

## Card 3: InsightCore

| Field | Value |
|---|---|
| **Participant Name** | InsightCore |
| **Runtime Identity** | `insightcore.runtime.intelligence.v1` |
| **Version** | 1.1.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Supported Operations** | `execute`, `health` |
| **Execution Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/execute` |
| **Health Endpoint** | `{INSIGHT_SERVICE_URL}/api/v1/health/insightcore.runtime.intelligence.v1` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | intelligence_processing, knowledge_contribution, runtime_analysis |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, ReplayRegistry |
| **Contract Version** | v1.1.0 |
| **Certification** | CERTIFIED — 2026-08-10 |

---

## Runtime Registration Flow

```
1. RegistrationBuilder.build_service_record(participant)
   → Creates Platform Service Record with INSIGHT_SERVICE_URL endpoints
   
2. LivePlatformClient.register_runtime(record)
   → POST https://bhiv-qcg.onrender.com/registry/platform/v1/register
   → Response: { status: "REGISTERED" | "ALREADY_REGISTERED" }

3. RegistrationBuilder.build_capability_manifest(participant)
   → Creates Capability Manifest with supported_operations

4. LivePlatformClient.register_capability(manifest)
   → POST https://bhiv-qcg.onrender.com/registry/capabilities/register
   → Response: { status: "REGISTERED" | "ALREADY_REGISTERED" }
```

---

## Evidence Chain

All three registrations form a cryptographic evidence chain through the PlatformCapabilitySDK:

```
GENESIS HASH (SDK_EVIDENCE_GENESIS)
    └→ InsightFlow invocation evidence
            └→ InsightBridge invocation evidence
                    └→ InsightCore invocation evidence
```

Each record's `previous_evidence_hash` links to the prior record's `evidence_hash`, ensuring sequential, tamper-evident execution.
