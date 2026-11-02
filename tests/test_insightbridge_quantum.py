"""
Tests for InsightBridge Participant Quantum Delegation
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.participants.insightflow.participant import InsightFlowParticipant
from src.participants.insightcore.participant import InsightCoreParticipant


def test_insightbridge_standard_execution_untouched():
    """Ensure ordinary InsightBridge behavior is 100% unchanged."""
    participant = InsightBridgeParticipant()
    payload = {"key": "test_value", "operation": "execute"}
    res = participant.execute(payload)

    assert res["participant"] == "InsightBridge"
    assert res["status"] == "executed"
    assert res["payload"] == payload
    assert "quantum_route" not in res


def test_insightflow_and_insightcore_unaffected():
    """Ensure InsightFlow and InsightCore have no quantum coupling."""
    flow = InsightFlowParticipant()
    core = InsightCoreParticipant()

    flow_res = flow.execute({"data": 123})
    core_res = core.execute({"data": 456})

    assert flow_res["status"] == "executed"
    assert core_res["status"] == "executed"
    assert not hasattr(flow, "quantum_adapter")
    assert not hasattr(core, "quantum_adapter")


def test_insightbridge_quantum_forwarding():
    """Ensure InsightBridge delegates quantum payloads to live Marine Quantum Runtime."""
    participant = InsightBridgeParticipant()
    payload = {
        "route": "quantum",
        "target_capability": "quantum_pipeline",
        "salinity": 35.2,
        "temperature_celsius": 18.5,
        "pH": 7.8,
        "material_oxidation_potential": 0.44,
        "dissolved_oxygen_mgl": 6.5,
        "current_density_mAcm2": 0.12,
    }
    
    # Execution will attempt a real HTTP request to marine-quantum-runtime-final.onrender.com
    res = participant.execute(payload)

    assert res["participant"] == "InsightBridge"
    assert res["status"] == "accepted"
    assert res["quantum_route"] == "DELEGATED_QUANTUM"
    assert res["quantum_capability"] == "quantum_pipeline"
    assert "quantum_result" in res

    q_res = res["quantum_result"]
    assert q_res["status"] in ("SUCCESS", "FAILED", "UNAVAILABLE"), f"Unexpected status: {q_res['status']}"
    if q_res["status"] == "SUCCESS":
        assert q_res["capability_id"] == "quantum_pipeline"
        assert "invocation_id" in q_res
        assert "deterministic_hash" in q_res


def test_insightbridge_health():
    """Ensure InsightBridge health reports participant state and quantum gateway status without mocks."""
    participant = InsightBridgeParticipant()
    health = participant.health()

    assert health["participant"] == "InsightBridge"
    assert health["state"] in ("DRAFT", "ACTIVE")
    assert "quantum_gateway" in health
    assert health["quantum_gateway"]["attached"] is True
    assert health["quantum_gateway"]["runtime"] == "Marine Quantum Runtime"
    
    # Gateway health is dynamic, so we just ensure it exists
    assert "gateway_health" in health



def test_cryptographic_provenance_anchoring_blk_arc_003():
    """Verify cryptographic provenance anchoring emits SHA-256 execution_digest and nonce."""
    from src.platform.quantum_adapter import MarineQuantumAdapter, compute_execution_digest

    payload = {"gate_sequence": [{"gate": "h", "qubits": [0]}], "shots": 100}
    expected_digest = compute_execution_digest(payload["gate_sequence"])
    assert len(expected_digest) == 64

    adapter = MarineQuantumAdapter(mode="remote_cluster")
    res = adapter.execute_circuit(payload)
    assert res["status"] == "UNAVAILABLE"
    assert res["execution_digest"] == expected_digest
    assert "provenance_nonce" in res
    assert len(res["provenance_nonce"]) == 32



def test_provenance_digest_key_order_independence():
    """Verify compute_execution_digest is independent of dictionary key insertion order."""
    from src.platform.quantum_adapter import compute_execution_digest

    payload1 = {"shots": 1024, "domain": "VANA", "parameters": {"gamma": 0.5, "beta": 0.8}}
    payload2 = {"domain": "VANA", "parameters": {"beta": 0.8, "gamma": 0.5}, "shots": 1024}
    digest1 = compute_execution_digest(payload1)
    digest2 = compute_execution_digest(payload2)

    assert digest1 == digest2
    assert len(digest1) == 64


def test_provenance_digest_gate_sequence_order_sensitivity():
    """Verify compute_execution_digest is strictly sensitive to gate execution sequence order."""
    from src.platform.quantum_adapter import compute_execution_digest

    seq_ab = [{"gate": "h", "qubit": 0}, {"gate": "cx", "qubits": [0, 1]}]
    seq_ba = [{"gate": "cx", "qubits": [0, 1]}, {"gate": "h", "qubit": 0}]
    digest_ab = compute_execution_digest(seq_ab)
    digest_ba = compute_execution_digest(seq_ba)

    assert digest_ab != digest_ba


def test_provenance_digest_different_payloads():
    """Verify distinct execution payloads produce distinct SHA-256 digests."""
    from src.platform.quantum_adapter import compute_execution_digest

    d1 = compute_execution_digest({"salinity": 35.0})
    d2 = compute_execution_digest({"salinity": 35.1})
    assert d1 != d2


def test_provenance_digest_empty_payloads():
    """Verify empty dict, empty list, and None produce valid distinct digests."""
    from src.platform.quantum_adapter import compute_execution_digest

    d_dict = compute_execution_digest({})
    d_list = compute_execution_digest([])
    d_none = compute_execution_digest(None)

    assert len(d_dict) == 64
    assert len(d_list) == 64
    assert len(d_none) == 64
    assert d_dict != d_list
    assert d_dict != d_none


def test_provenance_digest_unsupported_value_handling():
    """Verify NaN and unsupported types fall back safely to deterministic invalid digests."""
    from src.platform.quantum_adapter import compute_execution_digest

    d_nan1 = compute_execution_digest({"value": float("nan")})
    d_nan2 = compute_execution_digest({"value": float("nan")})
    assert len(d_nan1) == 64
    assert d_nan1 == d_nan2  # Deterministic handling

    d_obj = compute_execution_digest({"obj": object()})
    assert len(d_obj) == 64


def test_provenance_digest_reproducibility():
    """Verify compute_execution_digest is 100% reproducible over repeated evaluations."""
    from src.platform.quantum_adapter import compute_execution_digest

    payload = {"circuit_id": "test-circ-001", "shots": 500, "gates": [{"gate": "x", "qubit": 1}]}
    digests = {compute_execution_digest(payload) for _ in range(100)}
    assert len(digests) == 1
