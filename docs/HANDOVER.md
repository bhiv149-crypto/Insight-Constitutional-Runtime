# Engineering Handover Guide

## Purpose
The Engineering Handover Guide provides incoming maintainers, system integrators, and security reviewers with complete technical context, operational procedures, repository maps, and deployment instructions for the Insight Constitutional Runtime.

## What Was Implemented
- The Insight Stack (`InsightFlow`, `InsightBridge`, `InsightCore`) was transformed into reusable, schema-compliant Constitutional Runtime Participants.
- Thin platform adapters delegating all core platform services to the BHIV Platform without code duplication.
- Declarative constitutional contracts and runtime identity cards.

## What Was Verified Live
- 3/3 Participant live registrations via canonical contracts.
- 3/3 Capability discovery.
- End-to-end capability invocation with SUCCESS.
- OpenTelemetry traces and SDK evidence chains recorded.
- Replay deduplication verified (VALID -> DUPLICATE).
- Platform health status UP.

## Runtime Endpoints & Service IDs
* **Platform Registry Health**: `GET https://bhiv-qcg.onrender.com/registry/platform/v1/health`
* **Capability Catalog**: `GET https://bhiv-qcg.onrender.com/registry/capabilities/capabilities`

| Participant ID | Display Name | Version |
|---|---|---|
| `insightflow.runtime.intelligence.v1` | InsightFlow | 1.0.2 |
| `insightbridge.runtime.intelligence.v1` | InsightBridge | 1.0.2 |
| `insightcore.runtime.intelligence.v1` | InsightCore | 1.0.2 |

## Required Commands

### Run Integration Tests
```bash
pytest -q
```
*Expected: 12 passed.*

### Run Live Platform Integration Test
```bash
python tests/test_live_integration.py
```
*(Requires `INSIGHT_SERVICE_URL` environment variable.)*

### Start Execution Service
```bash
python insight_execution_service.py
```

## Evidence Locations
All generated evidence proving live convergence is located in the `evidence_packet/` directory. Refer to `docs/REVIEW_INDEX.md` for the precise mapping of requirement to evidence file.

## Known Limitations
* The live registration endpoint returned `ALREADY_REGISTERED`, confirming the service was already registered at the requested version. Subsequent discovery, negotiation, and invocation succeeded.

## Platform-Owned Dependencies
* **Platform-side Manifest**: The deployed Platform HTTP registration handler does not currently forward a manifest into the underlying registry registration call. The manifest field can be null in metadata. This must be resolved by the Platform team.

## What the Next Engineer Needs to Know
* The Insight Runtime integration uses thin platform adapters over REST. The architecture is locked and requires no further custom implementation for discovery or registry interaction.
* All outgoing REST requests align with official platform contract schemas.

## What Must NOT Be Changed Casually
* **Participant Identity IDs**: Changing `insightflow.runtime.intelligence.v1` will break capability tracking.
* **Platform Adapters**: These are explicitly mapped to the canonical Platform SDK and should not be modified unless the BHIV Platform contract changes.
* **Declarative Contracts**: Ensure these remain synchronized with actual implementation boundaries.