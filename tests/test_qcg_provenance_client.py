

"""
tests/test_qcg_provenance_client.py — Unit Tests for WS-A QCG Provenance Integration Client

Programme: BHQ-INFRA-001 (WS-A)
Owner: Ganesh Vishwakarma
Repository: Insight_Constitutional_Runtime
"""

import hashlib
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.platform.qcg_provenance_client import (
    QuantumWorkloadIdentity,
    QuantumExecutionInstance,
    ProvenanceSigningRequest,
    ProvenanceEvidenceResponse,
    GatewayTransmissionPackage,
    ProvenanceValidationError,
    QCGProvenanceClient,
)


@pytest.fixture
def client():
    return QCGProvenanceClient()


@pytest.fixture
def sample_workload_identity():
    return QuantumWorkloadIdentity(
        workload_id="workload-vana-001",
        domain="VANA",
        problem_id="PROB-VANA-ECOGRID-001",
        algorithm="QAOA",
        qubits_required=6,
        shots=1024,
    )


@pytest.fixture
def sample_execution_instance(sample_workload_identity):
    return QuantumExecutionInstance(
        execution_instance_id="exec-vana-instance-001",
        workload_identity=sample_workload_identity,
        backend_target="aer_simulator",
        execution_status="SUCCESS",
        measurement_counts={"110011": 820, "000000": 204},
        measurement_probabilities={"110011": 0.80078, "000000": 0.19922},
        best_candidate="110011",
        execution_time_ms=45.2,
        trace_id="trace-vana-test-001",
    )


def test_identity_separation(sample_workload_identity, sample_execution_instance, client):
    """Verify strict separation of workload ID, execution instance ID, and provenance record ID."""
    req, _ = client.prepare_signing_request(sample_execution_instance)
    
    assert sample_workload_identity.workload_id == "workload-vana-001"
    assert sample_execution_instance.execution_instance_id == "exec-vana-instance-001"
    assert req.execution_instance_id != sample_workload_identity.workload_id

    # Simulated valid response from WS-D
    resp = ProvenanceEvidenceResponse(
        execution_instance_id=sample_execution_instance.execution_instance_id,
        trace_id=sample_execution_instance.trace_id,
        canonical_digest=req.canonical_digest,
        node_id="NODE-TEST-001",
        public_key_hex="3059301306072a8648ce3d020106082a8648ce3d03010703420004" + "aa" * 32,
        signature_der_hex="3045022100" + "bb" * 31 + "0220" + "cc" * 31,
        replay_sequence=1,
        merkle_root="a" * 64,
        ledger_chain_length=1,
        timestamp="2026-11-02T12:00:00Z",
    )

    pkg = client.build_gateway_package(sample_execution_instance, resp)
    assert pkg.provenance_record_id.startswith("prov-")
    assert pkg.provenance_record_id != sample_execution_instance.execution_instance_id
    assert pkg.provenance_record_id != sample_workload_identity.workload_id


def test_prepare_signing_request_deterministic(sample_execution_instance, client):
    """Verify that identical execution instances yield identical canonical digests."""
    req1, canon_str1 = client.prepare_signing_request(sample_execution_instance)
    req2, canon_str2 = client.prepare_signing_request(sample_execution_instance)

    assert req1.canonical_digest == req2.canonical_digest
    assert canon_str1 == canon_str2
    assert len(req1.canonical_digest) == 64


def test_validate_provenance_response_success(sample_execution_instance, client):
    """Verify that a well-formed WS-D response validates successfully."""
    req, _ = client.prepare_signing_request(sample_execution_instance)

    resp = ProvenanceEvidenceResponse(
        execution_instance_id=req.execution_instance_id,
        trace_id=req.trace_id,
        canonical_digest=req.canonical_digest,
        node_id="NODE-TEST-001",
        public_key_hex="3059301306072a8648ce3d020106082a8648ce3d03010703420004" + "aa" * 32,
        signature_der_hex="3045022100" + "bb" * 31 + "0220" + "cc" * 31,
        replay_sequence=42,
        merkle_root="f" * 64,
        ledger_chain_length=42,
        timestamp="2026-11-02T12:00:00Z",
    )

    assert client.validate_provenance_response(req, resp) is True


def test_validate_provenance_response_digest_mismatch(sample_execution_instance, client):
    """Verify that a digest mismatch raises ProvenanceValidationError."""
    req, _ = client.prepare_signing_request(sample_execution_instance)

    resp = ProvenanceEvidenceResponse(
        execution_instance_id=req.execution_instance_id,
        trace_id=req.trace_id,
        canonical_digest="0" * 64,  # Mutated digest
        node_id="NODE-TEST-001",
        public_key_hex="3059301306072a8648ce3d020106082a8648ce3d03010703420004" + "aa" * 32,
        signature_der_hex="3045022100" + "bb" * 31 + "0220" + "cc" * 31,
        replay_sequence=1,
        merkle_root="f" * 64,
        ledger_chain_length=1,
        timestamp="2026-11-02T12:00:00Z",
    )

    with pytest.raises(ProvenanceValidationError, match="Canonical digest mismatch"):
        client.validate_provenance_response(req, resp)


def test_validate_provenance_response_corrupt_merkle_root(sample_execution_instance, client):
    """Verify that an invalid Merkle root length raises ProvenanceValidationError."""
    req, _ = client.prepare_signing_request(sample_execution_instance)

    resp = ProvenanceEvidenceResponse(
        execution_instance_id=req.execution_instance_id,
        trace_id=req.trace_id,
        canonical_digest=req.canonical_digest,
        node_id="NODE-TEST-001",
        public_key_hex="3059301306072a8648ce3d020106082a8648ce3d03010703420004" + "aa" * 32,
        signature_der_hex="3045022100" + "bb" * 31 + "0220" + "cc" * 31,
        replay_sequence=1,
        merkle_root="short_root",
        ledger_chain_length=1,
        timestamp="2026-11-02T12:00:00Z",
    )

    with pytest.raises(ProvenanceValidationError, match="Invalid Merkle root length"):
        client.validate_provenance_response(req, resp)


def test_build_gateway_package(sample_execution_instance, client):
    """Verify that GatewayTransmissionPackage bundles canonical payload and communication message."""
    req, _ = client.prepare_signing_request(sample_execution_instance)
    resp = ProvenanceEvidenceResponse(
        execution_instance_id=req.execution_instance_id,
        trace_id=req.trace_id,
        canonical_digest=req.canonical_digest,
        node_id="NODE-TEST-001",
        public_key_hex="3059301306072a8648ce3d020106082a8648ce3d03010703420004" + "aa" * 32,
        signature_der_hex="3045022100" + "bb" * 31 + "0220" + "cc" * 31,
        replay_sequence=1,
        merkle_root="e" * 64,
        ledger_chain_length=1,
        timestamp="2026-11-02T12:00:00Z",
    )

    pkg = client.build_gateway_package(
        sample_execution_instance,
        resp,
        communication_message="VANA_DISPATCH_CONFIRMED",
        noise_factor=0.05,
    )

    assert pkg.communication_message == "VANA_DISPATCH_CONFIRMED"
    assert pkg.noise_factor == 0.05
    assert pkg.canonical_digest == req.canonical_digest
    assert pkg.canonical_payload["domain"] == "VANA"
    assert pkg.canonical_payload["best_candidate"] == "110011"
