# Documentation and Runtime Evidence Audit

**Audit date:** 2026-08-19  
**Scope:** Repository documentation reconciled against source, tests, live observations,
OpenAPI, configuration, and evidence artifacts. No non-Markdown file was modified.

## Executive Finding

The repository contains a FastAPI execution service hosting three participants:
InsightFlow, InsightBridge, and InsightCore. The participants share the `BaseParticipant`
contract and platform adapter layer. `PlatformIntegrationService` owns the convergence
workflow: registration, capability registration, discovery, version negotiation,
invocation, health, replay validation, telemetry recording, failure paths, and evidence
writing.

The recorded test result is **27 passed with 3 warnings**. The warnings are framework
and fixture deprecations, not failures. Script-style test files under `tests/` are not
all pytest-discoverable and must not be added to the pytest count.

## Status Matrix

| Area | Status | Evidence and limitation |
|---|---|---|
| Three participant implementations | `VERIFIED-LOCAL` | Participant modules and execution-contract tests |
| Platform registration | `VERIFIED-LIVE` | `evidence_packet/api_samples/runtime_registration.json`; `ALREADY_REGISTERED` is idempotent |
| Capability registration | `VERIFIED-LIVE` | `evidence_packet/api_samples/capability_registration.json` |
| Discovery | `VERIFIED-LIVE` | `evidence_packet/api_samples/discovered_services.json` |
| Version negotiation | `VERIFIED-LIVE` | `evidence_packet/registry_proof/version_negotiation.json` |
| SDK invocation | `VERIFIED-LIVE` | `evidence_packet/invocation_proof/invocation_results.json` |
| Failure paths | `VERIFIED-LIVE` | `evidence_packet/invocation_proof/failure_cases.json` |
| Participant health | `VERIFIED-LIVE` | `evidence_packet/registry_proof/health_check.json` and runtime health artifacts |
| Replay lineage retrieval | `VERIFIED-LIVE` | HTTP 200 with `VALID`; `evidence_packet/replay_evidence/replay_validation.json` |
| Local duplicate replay | `VERIFIED-LOCAL` | In-memory `CanonicalReplayAuthority`; not canonical submission |
| `/qcg/verify` Trust stage | `PARTIALLY-VERIFIED` | Replay stage valid; HTTP 422 `INVALID_SIGNATURE` at Trust |
| Platform telemetry | `VERIFIED-LOCAL` | `TraceStore` from `src.platform.stubs`; live storage not established |
| InsightBridge `/ingest` | `VERIFIED-LIVE` | Separate live ingestion result; not Platform telemetry storage |
| Quantum | `VERIFIED-LOCAL` | Marine subprocess; no cloud deployment established |
| `/enforce` | `PENDING-CONTRACT` | Endpoint and Bearer auth observed; payload/response schemas are not useful |
| InsightCore external service | `NOT-ESTABLISHED` | Platform participant exists; no external service or adapter contract exists |
| Deployment | `PARTIALLY-VERIFIED` | Health-based live evidence exists; deployment metadata is not independently included |

## Architecture and Ownership

Insight Runtime owns participant business behavior, local execution, and local evidence.
The Platform owns registration, discovery, invocation infrastructure, governance, and
canonical replay authority. Telemetry is delegated to the Platform boundary, but the
current provider is a local stub. Quantum execution belongs to Marine Quantum Runtime
and is reached from InsightBridge only, in local mode.

## Known Contradictions

1. `https://insight-flow-f5j4.onrender.com/health` returns healthy but reports
   `service: InsightBridge`. The identity/deployment naming cause is not established.
2. The live OpenAPI titled `InsightBridge` exposes `/enforce` with Bearer auth but no
   verified request or response contract. Successful enforcement is not established.
3. `/qcg/verify` fails at Trust with `INVALID_SIGNATURE`; this does not invalidate the
   independently observed replay lineage result.
4. The current Platform telemetry provider is `TraceStore` in `src.platform.stubs`.
   This is not evidence of production telemetry storage.
5. Older Markdown referred to replay HTTP 404, a missing `submit()` method, 17 tests,
   and files not present in this checkout. Those claims were historical/stale and have
   been removed from current-purpose documents.

## Reproduction Boundary

Use `python -m pytest tests/ -v` after installing `requirements.txt` and the external
`tantra-platform-sdk==1.0.0` dependency. Live tests require network access to
`https://bhiv-qcg.onrender.com`; Quantum tests require the local Marine runtime. The
repository documents exact endpoint checks only where the endpoint and observed result
are supported by evidence. No command is provided for `/enforce` execution because its
contract is not established.

## Certification Conclusion

The evidence supports live Platform participation and replay lineage retrieval. It does
not support production certification, production telemetry, production Quantum, Trust-stage
success, or enforcement execution. These limitations remain explicit in `HANDOVER.md` and
`docs/FINAL_STATUS.md`.
