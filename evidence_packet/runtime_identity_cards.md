# Constitutional Runtime Identity Cards Catalog

## Overview

This document compiles the formal **Runtime Identity Cards** for the three Constitutional Runtime Participants comprising the Insight Stack: `InsightFlow`, `InsightBridge`, and `InsightCore`.

Each identity card defines the participant's permanent runtime identity, constitutional scope, authority boundaries, API dependencies, emitted evidence, and operational status within the **BHIV Constitutional Platform**.

---

# 1. Runtime Identity Card — InsightFlow

## Runtime Participant Information

| Property | Value |
|---|---|
| **Participant Name** | `InsightFlow` |
| **Constitutional Layer** | Intelligence Layer / Domain Services |
| **Runtime Type** | Constitutional Runtime Participant (`PROCESS`) |
| **Permanent Runtime Identity** | `insightflow.runtime.intelligence.v1` |
| **Current Version** | `v1.0.0` |
| **Live Registration Status** | **VERIFIED** (`HTTP 200 OK` on `https://bhiv-qcg.onrender.com`) |

### Authority Owned
* Intelligence workflow orchestration
* Insight execution initiation
* Runtime capability invocation
* Runtime evidence contribution and trace span generation

### Authority Explicitly NOT Owned
* Runtime platform orchestration
* Platform Service Registry & Capability Registry management
* Quantum Runtime execution
* Replay Registry & Trust verification management

### Upstream Platform Dependencies
* `PlatformCapabilitySDK`, `PlatformDiscovery`, `PlatformRegistry`, `RuntimeCore`

---

# 2. Runtime Identity Card — InsightBridge

## Runtime Participant Information

| Property | Value |
|---|---|
| **Participant Name** | `InsightBridge` |
| **Constitutional Layer** | Intelligence Layer / Domain Services |
| **Runtime Type** | Constitutional Runtime Participant (`PROCESS`) |
| **Permanent Runtime Identity** | `insightbridge.runtime.intelligence.v1` |
| **Current Version** | `v1.0.0` |
| **Live Registration Status** | **VERIFIED** (`HTTP 200 OK` on `https://bhiv-qcg.onrender.com`) |

### Authority Owned
* Cross-domain protocol translation and messaging integration
* Capability coordination and gateway interface wrapping
* Integration evidence logging and distributed trace propagation

### Authority Explicitly NOT Owned
* Platform Registry management
* Quantum execution algorithm selection
* Replay deduplication enforcement

### Upstream Platform Dependencies
* `PlatformCapabilitySDK`, `PlatformDiscovery`, `RuntimeCore`, `QuantumCommunicationGateway`

---

# 3. Runtime Identity Card — InsightCore

## Runtime Participant Information

| Property | Value |
|---|---|
| **Participant Name** | `InsightCore` |
| **Constitutional Layer** | Intelligence Layer / Domain Services |
| **Runtime Type** | Constitutional Runtime Participant (`PROCESS`) |
| **Permanent Runtime Identity** | `insightcore.runtime.intelligence.v1` |
| **Current Version** | `v1.0.0` |
| **Live Registration Status** | **VERIFIED** (`HTTP 200 OK` on `https://bhiv-qcg.onrender.com`) |

### Authority Owned
* Primary intelligence execution logic
* State validation and deterministic execution output generation
* Replay sequence participation and evidence generation

### Authority Explicitly NOT Owned
* Platform consensus management
* Global identity issuance
* Hardware-level governance authority

### Upstream Platform Dependencies
* `PlatformCapabilitySDK`, `PlatformDiscovery`, `RuntimeCore`, `ReplayRegistry`

---

## Identity Verification Summary

```json
{
  "verified_identities": [
    "insightflow.runtime.intelligence.v1",
    "insightbridge.runtime.intelligence.v1",
    "insightcore.runtime.intelligence.v1"
  ],
  "live_platform": "https://bhiv-qcg.onrender.com",
  "registration_status": "REGISTERED",
  "readiness_checks": "17/17 PASSED"
}
```

*Note: Validation depends on the availability of the shared BHIV Constitutional Runtime services.*es
- Production certification
