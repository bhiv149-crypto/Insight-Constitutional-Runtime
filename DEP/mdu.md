# Module Dependency Unit (MDU) Mapping

## Overview

The **Module Dependency Unit (MDU)** specification maps external platform capabilities required by each Insight Runtime participant.

---

## MDU Mapping Table

| Participant | Required MDU | Adapter Implementation | Platform Endpoint / API | Status |
|---|---|---|---|---|
| **InsightFlow** | `PlatformCapabilitySDK` | `PlatformSDKAdapter` | Platform Core Interfaces | **VERIFIED** |
| **InsightFlow** | `PlatformDiscovery` | `PlatformDiscoveryAdapter` | `GET /registry/capabilities/capabilities` | **VERIFIED** |
| **InsightFlow** | `PlatformRegistry` | `PlatformRegistryAdapter` | `POST /registry/platform/v1/register` | **VERIFIED** |
| **InsightBridge** | `PlatformCapabilitySDK` | `PlatformSDKAdapter` | Platform Core Interfaces | **VERIFIED** |
| **InsightBridge** | `QuantumCommunicationGateway` | `PlatformSDKAdapter` | Gateway REST API | **VERIFIED** |
| **InsightCore** | `ReplayRegistry` | `PlatformReplayAdapter` | `CanonicalReplayAuthority` | **VERIFIED** |
| **All Participants** | `HeartbeatManager` | `PlatformHealthAdapter` | `GET /registry/platform/v1/health` | **VERIFIED** |
| **All Participants** | `ObservabilityService` | `PlatformTelemetryAdapter` | OpenTelemetry Exporter | **VERIFIED** |

---

## Dependency Verification Statement

All MDUs are consumed exclusively through thin platform adapters in `src/platform/`. Validation depends on the availability of the shared BHIV Constitutional Runtime services.