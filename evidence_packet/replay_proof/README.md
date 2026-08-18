# Replay Validation Proof

## Purpose

This proof packet documents the current live Replay evidence for the BHIV QCG canonical flow. The goal is to separate Replay validity from the separate Trust-stage failure in `/qcg/verify`.

## Test command

```bash
pytest tests\test_live_platform.py::test_sdk_invocation_verify_and_replay -v
```

**Current baseline**: PASS

## Live endpoint and flow

The proof uses the live QCG path:

- `POST https://bhiv-qcg.onrender.com/qcg/verify`
- `GET https://bhiv-qcg.onrender.com/qcg/replay/lineage/{invocation_id}`

The canonical flow is:

1. SDK invocation produces an `invocation_id`
2. Same `invocation_id` is submitted to `/qcg/verify`
3. Replay stage is recorded as `VALID`
4. Trust stage fails with `INVALID_SIGNATURE`
5. `/qcg/replay/lineage/{invocation_id}` returns HTTP 200 with a VALID replay verdict

## Invocation identity

The replay proof is keyed to the SDK-generated `invocation_id` returned during the live invocation. The exact runtime values are captured in the proof artifacts and should be read from the evidence files rather than copied into this note as mutable placeholders.

## Verify result

The current verified platform behavior is:

- `/qcg/verify` returns HTTP 422
- `detail.stages.replay.is_valid == true`
- `detail.stages.replay.status == "VALID"`
- `detail.stages.trust.passed == false`
- `detail.halt_reason` includes `HALT:INVALID_SIGNATURE`

This is a Trust-stage halt, not a Replay failure.

## Replay result

The canonical replay lineage lookup returns HTTP 200. The replay record is a valid lineage object with the same message identity and a VALID verdict.

## Lineage evidence

The lineage proof includes the canonical fields associated with the live request, including:

- `message_id`
- `verdict.status == "VALID"`
- `lineage_record.decision == "VALID"`
- `lineage_record.origin_component == "CanonicalReplayAuthority"`
- `lineage_record.verification_hash`
- `lineage_record.trace_reference`
- `lineage_record.replay_id`

The exact values are retained in the live evidence artifacts:

- [evidence_packet/replay_evidence/verify_replay_valid_422_trust.json](../replay_evidence/verify_replay_valid_422_trust.json)
- [evidence_packet/replay_evidence/replay_validation.json](../replay_evidence/replay_validation.json)

## Current limitation

The overall constitutional verification pipeline is not yet fully converged because the Trust stage still fails ECDSA signature verification. Replay evidence remains valid, but the final `/verify` status remains `HALTED` until the platform-side Trust issue is resolved.

This means the repository should document:

- Replay = VERIFIED
- `/verify` = HALTED at Trust
- Production certification = PENDING
- Quantum Runtime E2E = PENDING unless separately validated