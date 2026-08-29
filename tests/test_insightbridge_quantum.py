"""
Tests for InsightBridge Participant Quantum Delegation
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from unittest.mock import patch
from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.participants.insightflow.participant import InsightFlowParticipant
from src.participants.insightcore.participant import InsightCoreParticipant


def test_insightbridge_standard_execution_untouched():
    """Ensure ordinary InsightBridge behavior is 100% unchanged."""
    participant = InsightBridgeParticipant()
    payload = {"key": "test_value", "operation": "execute"}
    res = participant.execute(payload)

    assert res["participant"] == "InsightBridge"
    assert res["status"] == "accepted"
    assert res["payload"] == payload
    assert "quantum_route" not in res


def test_insightflow_and_insightcore_unaffected():
    """Ensure InsightFlow and InsightCore have no quantum coupling."""
    flow = InsightFlowParticipant()
    core = InsightCoreParticipant()

    flow_res = flow.execute({"data": 123})
    core_res = core.execute({"data": 456})

    assert flow_res["status"] == "accepted"
    assert core_res["status"] == "accepted"
    assert not hasattr(flow, "quantum_adapter")
    assert not hasattr(core, "quantum_adapter")


@patch('src.platform.quantum_adapter.requests.post')
def test_insightbridge_quantum_forwarding(mock_post):
    """Ensure InsightBridge delegates quantum payloads to local Marine Quantum Runtime."""
    mock_post.return_value.json.return_value = {
        "status": "SUCCESS",
        "capability_id": "quantum_pipeline",
        "invocation_id": "mock-id-123",
        "deterministic_hash": "mock-hash-456",
    }
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
    res = participant.execute(payload)

    assert res["participant"] == "InsightBridge"
    assert res["status"] == "accepted"
    assert res["quantum_route"] == "DELEGATED_LOCAL_QUANTUM"
    assert res["quantum_capability"] == "quantum_pipeline"
    assert "quantum_result" in res

    q_res = res["quantum_result"]
    assert q_res["status"] == "SUCCESS"
    assert q_res["capability_id"] == "quantum_pipeline"
    assert "invocation_id" in q_res
    assert "deterministic_hash" in q_res


@patch('src.platform.quantum_adapter.requests.get')
def test_insightbridge_health(mock_get):
    """Ensure InsightBridge health reports participant state and quantum gateway status."""
    mock_get.return_value.json.return_value = {"status": "HEALTHY", "heartbeat": "ALIVE"}
    participant = InsightBridgeParticipant()
    health = participant.health()

    assert health["participant"] == "InsightBridge"
    assert health["state"] in ("DRAFT", "ACTIVE")
    assert "quantum_gateway" in health
    assert health["quantum_gateway"]["attached"] is True
    assert health["quantum_gateway"]["runtime"] == "Marine Quantum Runtime"
