# Telemetry & Metric Specification (TMS)

## Overview

The **Telemetry & Metric Specification (TMS)** defines observability trace propagation, span recording, and execution metric collection for the **Insight Constitutional Runtime**.

---

## TMS Phase & Execution Status

| TMS Phase | Phase Description | Implementation & Adapter | Verification Status |
|---|---|---|---|
| **Phase 1** | Identity & Attribute Tagging | `models.py` / `RegistrationBuilder` | **COMPLETE** |
| **Phase 2** | Platform Adapter Metric Injection | `PlatformTelemetryAdapter` | **COMPLETE** |
| **Phase 3** | OpenTelemetry Span Generation | `PlatformTelemetryAdapter` | **COMPLETE** |
| **Phase 4** | Execution Trace Logging | `LivePlatformClient` / `PlatformIntegrationService` | **COMPLETE** |
| **Phase 5** | Production Collector Export | OpenTelemetry Cluster Collector | **VERIFIED** |
| **Phase 6** | Documentation & Handover | `docs/`, `evidence_packet/`, `DEP/` | **COMPLETE** |

---

## Telemetry Metrics & Spans Recorded

* **Registration Event Span**: `trace_id: trace-001`, `span: participant_registration`
* **Discovery Metric**: `count: 3 services`
* **Replay Sequence Trace**: `sequence: 1`, `status: VALID`

*Note: Validation depends on the availability of the shared BHIV Constitutional Runtime services.*