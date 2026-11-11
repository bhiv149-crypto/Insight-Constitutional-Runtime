"""
test_insightbridge_bioquantum.py — Tests for BIOQUANTUM ICR Orchestration & Provenance Client
=============================================================================================

Programme: BHQ-INFRA-001 (Cross-Workstream Integration: WS-A -> WS-D -> WS-C)
Owner: Ganesh Vishwakarma (WS-A Lead & Systems Integrator)
"""

import sys
from pathlib import Path
import pytest

ICR_ROOT = Path(__file__).resolve().parents[1]
if str(ICR_ROOT) not in sys.path:
    sys.path.insert(0, str(ICR_ROOT))

from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.platform.qcg_provenance_client import (
    QCGProvenanceClient,
    QuantumExecutionInstance,
    QuantumWorkloadIdentity,
    ProvenanceSigningRequest,
)


class TestInsightBridgeBioQuantum:
    """Tests for ICR orchestration and provenance client integration with BIOQUANTUM."""

    def test_qcg_provenance_client_signing_request_preparation(self):
        workload = QuantumWorkloadIdentity(
            workload_id="workload-bio-20261107-001",
            domain="BIOQUANTUM",
            problem_id="bio-physarum-4node-6qubit-golden",
            algorithm="qaoa",
            qubits_required=6,
            shots=1024,
        )

        instance = QuantumExecutionInstance(
            execution_instance_id="exec-bio-001",
            workload_identity=workload,
            backend_target="aer_simulator",
            execution_status="SUCCESS",
            measurement_counts={"100100": 48, "010101": 11, "010010": 5},
            measurement_probabilities={"100100": 0.046875, "010101": 0.010742, "010010": 0.004883},
            best_candidate="100100",
            execution_time_ms=34.52,
            trace_id="trace-bio-test-1234",
        )

        client = QCGProvenanceClient()
        signing_req, canonical_str = client.prepare_signing_request(instance)

        assert isinstance(signing_req, ProvenanceSigningRequest)
        assert signing_req.execution_instance_id == "exec-bio-001"
        assert signing_req.canonical_payload["domain"] == "BIOQUANTUM"
        assert len(signing_req.canonical_digest) == 64
        # Verify hex SHA-256
        int(signing_req.canonical_digest, 16)
        assert '"domain":"BIOQUANTUM"' in canonical_str

    def test_insightbridge_participant_quantum_route_acceptance(self):
        bridge = InsightBridgeParticipant()
        payload = {
            "route": "quantum",
            "target_capability": "quantum_pipeline",
            "quantum_payload": {
                "domain": "BIOQUANTUM",
                "problem_id": "bio-physarum-4node-6qubit-golden",
                "n_qubits": 6,
            },
        }

        # Execute through participant
        res = bridge.execute(payload)
        assert res["participant"] == "InsightBridge"
        assert res["status"] == "accepted"
        assert res["quantum_route"] == "DELEGATED_QUANTUM"
        assert res["quantum_capability"] == "quantum_pipeline"

