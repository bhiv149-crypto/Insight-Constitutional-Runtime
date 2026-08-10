# Insight Constitutional Runtime

## Overview
The **Insight Constitutional Runtime** transforms the Insight Stack (`InsightFlow`, `InsightBridge`, `InsightCore`) into reusable, schema-compliant Constitutional Runtime Participants within the Intelligence Layer of the **BHIV Constitutional Runtime** ecosystem.

Instead of duplicating core platform infrastructure, the Insight Runtime operates on a thin adapter architecture, consuming canonical Platform Runtime services—including Runtime Registration, Capability Discovery, Replay Enforcement, Health Monitoring, and OpenTelemetry Tracing.

## Assignment Scope & Objectives
**Objective:** Move InsightFlow, InsightBridge, and InsightCore from internally validated integration into true live, plug-and-play TANTRA runtime participation using Kanishk's Platform Runtime.

**Insight Stack Ownership:**
- Live registration, Discovery, Capability invocation
- Trace/evidence generation, Replay participation
- Health, Observability, Runtime identity
- Participant contracts, Integration evidence, Handover documentation

## Repository Layout
| Directory / File | Description | Ownership Boundary |
|---|---|---|
| `src/common/` | Base participant classes and shared models | Insight Stack |
| `src/participants/` | Participant implementations (`InsightFlow`, `InsightBridge`, `InsightCore`) | Insight Stack |
| `src/platform/` | Thin platform adapters | Platform Boundary |
| `src/integration/` | Lifecycle orchestration service and runtime validation | Integration Layer |
| `contracts/` | Declarative constitutional contracts for each participant | Governance |
| `evidence_packet/` | Engineering validation reports, identity cards, and audit evidence | Reviewers |
| `docs/` | Architectural specifications, handover guides, and integration proofs | Documentation |
| `tests/` | Repository integration readiness test suite | Quality Assurance |

## Runtime Participants
| Participant ID | Display Name | Key Capabilities |
|---|---|---|
| `insightflow.runtime.intelligence.v1` | **InsightFlow** | Workflow orchestration, trace generation, evidence emission |
| `insightbridge.runtime.intelligence.v1` | **InsightBridge** | Cross-domain messaging, gateway protocol translation |
| `insightcore.runtime.intelligence.v1` | **InsightCore** | Deterministic state validation, replay enforcement |

## Execution Flow
The execution flow proves integration in the following steps:
`Registration -> Discovery -> Negotiation -> Invocation -> Evidence -> Replay -> Health -> Telemetry -> Failure paths -> Final convergence`

## Setup & Testing Instructions

### Prerequisites
* Python 3.10+
* Required packages per `requirements.txt`

### Running Integration Readiness Tests
Execute the repository test suite to verify module integrity:
```bash
pytest -q
```
**Expected Result:** 12 passed

### Running Live Platform Integration
To execute full end-to-end integration against the live platform:
```bash
python tests/test_live_integration.py
```
*(Note: Requires `INSIGHT_SERVICE_URL` environment variable pointing to the deployed Insight service URL.)*

## Documentation Map
* `docs/FINAL_STATUS.md`: Production readiness declaration and completion matrix.
* `REVIEW_PACKET.md`: Final review packet for grading.
* `SUBMISSION_SUMMARY.md`: Executive submission summary.
* `docs/RUNTIME_INTEGRATION_PROOF.md`: Technical proof of live server integration.
* `docs/HANDOVER.md`: Engineering handover guidelines and operational runbooks.
* `docs/REVIEW_INDEX.md`: Master reviewer navigation page mapping requirements to evidence.

## Project Status
**OVERALL: LIVE RUNTIME CONVERGENCE VERIFIED**
All required 10 proofs have been captured. The repository is internally validated and fully ready for production inspection. Final platform-wide production certification remains dependent on external platform/governance requirements.