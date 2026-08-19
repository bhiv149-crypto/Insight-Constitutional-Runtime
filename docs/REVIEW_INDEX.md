# Evidence Index

> Current status supersedes older packet language that described replay as historical or
> blocked. See the reconciliation note at the end of this file.

## Purpose
This document maps each assignment requirement to its precise evidence location within the repository.

| Requirement | Evidence |
|---|---|
| InsightFlow registration | `evidence_packet/api_samples/` |
| InsightBridge registration | `evidence_packet/api_samples/` |
| InsightCore registration | `evidence_packet/api_samples/` |
| Discovery | `evidence_packet/api_samples/discovered_services.json` |
| Invocation | `evidence_packet/invocation_proof/` |
| Evidence chain | `evidence_packet/invocation_proof/sdk_evidence_chain.json` |
| Replay | `evidence_packet/replay_evidence/` (`VERIFIED-LIVE` lineage retrieval; local duplicate path separately `VERIFIED-LOCAL`) |
| Health | `evidence_packet/registry_proof/` |
| Telemetry | `evidence_packet/telemetry/` (🟣 HISTORICAL / STUB-DERIVED — live telemetry NOT exposed) |
| Version compatibility | `evidence_packet/registry_proof/version_negotiation.json` |
| Failure cases | `evidence_packet/invocation_proof/failure_cases.json` |
| Deployment | `evidence_packet/deployment_proof/` |
| Runtime identities | `evidence_packet/runtime_identity_cards.md` |
| Contracts | `contracts/` |
| End-to-end convergence | `evidence_packet/integration_summary.json` |
| Audit report | `docs/AUDIT_REPORT.md` |

## Reconciliation Note

`GET /qcg/replay/lineage/{invocation_id}` is recorded as HTTP 200 with a `VALID` verdict.
`POST /qcg/verify` reaches Replay but halts at Trust with HTTP 422 and `INVALID_SIGNATURE`.
The local `CanonicalReplayAuthority` duplicate result is not canonical QCG replay.
Telemetry remains a local `TraceStore`; live InsightBridge `/ingest` is a separate
verified observation. The current pytest result is 27 passed with 3 warnings, not 17/17.