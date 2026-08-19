# Documentation Audit Summary

**Audit date:** 2026-08-19  
**Scope:** Markdown documentation only. Source, tests, JSON, OpenAPI, configuration,
and deployment files were inspected but not changed.

## Result

Documentation was reconciled against the current source tree, recorded test result,
live endpoint observations, and evidence packet. The current recorded pytest result is
**27 passed with 3 warnings**. The warnings are deprecation notices from
pytest-asyncio, Starlette multipart, and FastAPI lifecycle handling; they are not test
failures.

## Current Verified State

- Three participants exist and are Platform-integrated: InsightFlow, InsightBridge,
  and InsightCore, all version `1.0.2`.
- Registration, capability registration, discovery, version compatibility, SDK
  invocation, participant health, evidence capture, and failure paths are evidenced.
- Canonical replay lineage retrieval is `VERIFIED-LIVE`: HTTP 200 with a `VALID`
  verdict. Local `VALID` then `DUPLICATE` behavior belongs to the in-memory
  `CanonicalReplayAuthority` and is not canonical QCG submission.
- `/qcg/verify` reaches Replay but halts at Trust with HTTP 422 and
  `INVALID_SIGNATURE`.
- Platform telemetry is `VERIFIED-LOCAL` through `TraceStore` in
  `src.platform.stubs`; live Platform telemetry storage is not established.
- InsightBridge `/ingest` success is a separate live observation and must not be
  combined with Platform telemetry claims.
- Marine Quantum integration is `VERIFIED-LOCAL`; production or cloud Quantum is not
  established.
- InsightCore has no dedicated external adapter or external service contract; current
  Platform integration does not establish a need for one.
- The live endpoint named `insight-flow-f5j4.onrender.com` reports `service: InsightBridge`.
  This naming inconsistency remains unresolved.
- `/enforce` exists in the retrieved OpenAPI and requires Bearer authentication, but
  its request and response schemas are not useful enough to verify execution.

## Documentation Changes

Core entry, handover, architecture, integration, Quantum, status, proof, contracts,
dependency/evidence summaries, runtime identities, review indexes, and changelog
language were aligned to explicit classifications: `VERIFIED-LIVE`, `VERIFIED-LOCAL`,
`VERIFIED-MOCK`, `IMPLEMENTED-NOT-LIVE`, `PARTIALLY-VERIFIED`, `PENDING-CONTRACT`,
`PAUSED`, `NOT-IMPLEMENTED`, and `NOT-APPLICABLE`.

Older references to `HANDOVER_NEW.md`, `TEST_STATUS.md`, `convergence_summary.json`,
`proof_matrix.md`, and `run_convergence.py` are not current repository artifacts and
are no longer treated as reproduction dependencies. Historical claims are retained
only when explicitly identified as historical.

## Certification Boundary

The repository is documented as live-integrated for the evidenced Platform lifecycle,
not as production-certified. Trust-stage success, canonical telemetry storage,
production Quantum execution, and `/enforce` execution remain pending or unestablished.
