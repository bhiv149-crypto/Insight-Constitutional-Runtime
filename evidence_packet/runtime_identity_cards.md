# Insight Stack — Runtime Identity Cards

**Live Integration Verified**: 2026-08-08T10:10:05Z UTC  
**Platform**: BHIV Constitutional Platform Runtime (https://bhiv-qcg.onrender.com)  
**All Three Participants**: REGISTERED (HTTP 200) + ACTIVE

---

## Card 1: InsightFlow

| Field | Value |
|---|---|
| **Participant Name** | InsightFlow |
| **Runtime Identity** | `insightflow.runtime.intelligence.v1` |
| **Version** | 1.0.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Registration Hash** | `66cdc114ed87f10a00a5cebc1869ed353366975fe287cebe50c2abbd928e590c` |
| **Evidence Hash** | `6a5335e1cf032f6174b9099ecf33e6dde11d58edb99f867e78ef34e690ac5c8e` |
| **Previous Evidence Hash** | `9a9b162a21fc3e957ea53d4d174eac82f527616cd7e5205671b92c9d1de4d6ab` |
| **Registration Timestamp** | 2026-08-08T10:10:08.821518+00:00 |
| **Execution Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/services/insightflow.runtime.intelligence.v1` |
| **Health Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/health` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | workflow_orchestration, capability_invocation, trace_generation, evidence_generation |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, PlatformRegistry, RuntimeCore |

---

## Card 2: InsightBridge

| Field | Value |
|---|---|
| **Participant Name** | InsightBridge |
| **Runtime Identity** | `insightbridge.runtime.intelligence.v1` |
| **Version** | 1.0.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Registration Hash** | `c54e8da5fe421973fefc0ea1e4a1f6e725a40f41aba8ee1c8562e52b0c749cbc` |
| **Evidence Hash** | `456e36d0f0cd671b2ee571de33b449a347f3b68aa439b264be3a19aff40aea9b` |
| **Previous Evidence Hash** | `6a5335e1cf032f6174b9099ecf33e6dde11d58edb99f867e78ef34e690ac5c8e` |
| **Registration Timestamp** | 2026-08-08T10:10:09.092180+00:00 |
| **Execution Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/services/insightbridge.runtime.intelligence.v1` |
| **Health Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/health` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | protocol_translation, bridge_orchestration, quantum_interface, evidence_propagation |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, QuantumCommunicationGateway |

---

## Card 3: InsightCore

| Field | Value |
|---|---|
| **Participant Name** | InsightCore |
| **Runtime Identity** | `insightcore.runtime.intelligence.v1` |
| **Version** | 1.0.0 |
| **Layer** | Intelligence Layer |
| **Runtime Type** | Constitutional Runtime Participant |
| **Status** | ACTIVE |
| **Service Classification** | DOMAIN_SERVICE |
| **Capability Category** | INTELLIGENCE |
| **Registration Hash** | `ddd83fafedf27b13ac26fbb98064e2e9b66182f726461ff8882b3e30cdc20e28` |
| **Evidence Hash** | `ede9b5b9cc9ecc8cf89b48677789805201ca167151689b384117ddefb7d83b76` |
| **Previous Evidence Hash** | `456e36d0f0cd671b2ee571de33b449a347f3b68aa439b264be3a19aff40aea9b` |
| **Registration Timestamp** | 2026-08-08T10:10:09.833006+00:00 |
| **Execution Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/services/insightcore.runtime.intelligence.v1` |
| **Health Endpoint** | `https://bhiv-qcg.onrender.com/registry/platform/v1/health` |
| **Owner Team** | Insight Stack |
| **Owner Contact** | insight-runtime@bhiv.internal |
| **Capabilities** | core_intelligence, contract_resolution, replay_management, constitutional_enforcement |
| **Platform Dependencies** | PlatformCapabilitySDK, PlatformDiscovery, RuntimeCore, ReplayRegistry |

---

## Evidence Chain Integrity

The three registrations form a cryptographic chain:

```
GENESIS HASH (platform)
    └─> InsightFlow evidence_hash:  6a5335e1...
            └─> InsightBridge evidence_hash: 456e36d0...
                    └─> InsightCore evidence_hash: ede9b5b9...
```

Each participant's `previous_evidence_hash` matches the prior participant's `evidence_hash`, confirming sequential, tamper-evident registration.
