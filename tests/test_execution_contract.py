import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Set test execution token in environment before importing/running
TEST_EXECUTION_TOKEN = "test-execution-token-secure-123"
os.environ["INSIGHT_EXECUTION_TOKEN"] = TEST_EXECUTION_TOKEN

from insight_execution_service import app, _init_participants

# Initialize participants before tests
_init_participants()

client = TestClient(app, headers={"Authorization": f"Bearer {TEST_EXECUTION_TOKEN}"})

def test_1_insightflow_success():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-1"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["service_id"] == "insightflow.runtime.intelligence.v1"
    assert data["operation"] == "execute"
    assert data["invocation_id"] == "test-id-1"
    assert "response" in data

def test_2_insightbridge_success():
    req = {
        "service_id": "insightbridge.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-2"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["service_id"] == "insightbridge.runtime.intelligence.v1"
    assert data["operation"] == "execute"

def test_3_insightcore_success():
    req = {
        "service_id": "insightcore.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-3"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["service_id"] == "insightcore.runtime.intelligence.v1"
    assert data["operation"] == "execute"

def test_4_unknown_service():
    req = {
        "service_id": "unknown.service",
        "operation": "execute",
        "payload": {},
        "version": "1.0.2",
        "invocation_id": "test-id-4"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 404
    data = resp.json()
    assert data["status"] == "NOT_FOUND"

def test_5_unknown_operation():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "invalid_operation",
        "payload": {},
        "version": "1.0.2",
        "invocation_id": "test-id-5"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 400
    data = resp.json()
    assert data["status"] == "INVALID_OP"

def test_6_missing_service_id():
    req = {
        "operation": "execute",
        "payload": {},
        "version": "1.0.2",
        "invocation_id": "test-id-6"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 422 # Pydantic validation error

def test_7_missing_operation():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "payload": {},
        "version": "1.0.2",
        "invocation_id": "test-id-7"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 422

def test_8_missing_payload():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "version": "1.0.2",
        "invocation_id": "test-id-8"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 422

def test_9_missing_version():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {},
        "invocation_id": "test-id-9"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 422

def test_10_missing_invocation_id():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {},
        "version": "1.0.2"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 422

def test_11_unsupported_version():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {},
        "version": "2.0.0",
        "invocation_id": "test-id-11"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 400
    data = resp.json()
    assert data["status"] == "VERSION_REJECTED"

def test_12_response_contract():
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-12"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200
    data = resp.json()
    
    expected_keys = {
        "invocation_id", "service_id", "operation", "status", "response", 
        "duration_ms", "trust_method", "evidence", "error", "retry_count", "timestamp"
    }
    assert expected_keys.issubset(set(data.keys()))
    assert data["trust_method"] == "CLASSICAL"

def test_13_unauthenticated_request_rejected():
    """Verify that execution requests without authorization header are rejected with HTTP 401 or 403."""
    unauth_client = TestClient(app)
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-unauth"
    }
    resp = unauth_client.post("/api/v1/execute", json=req)
    assert resp.status_code in (401, 403)

def test_14_invalid_token_rejected():
    """Verify that execution requests with an invalid token are rejected with HTTP 401."""
    bad_client = TestClient(app, headers={"Authorization": "Bearer invalid-wrong-token-xyz"})
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": True},
        "version": "1.0.2",
        "invocation_id": "test-id-bad-auth"
    }
    resp = bad_client.post("/api/v1/execute", json=req)
    assert resp.status_code == 401
    assert "Invalid or missing authentication token" in resp.json().get("detail", "")

def test_15_circuit_execution_route():
    """Verify InsightBridge correctly dispatches quantum circuit payloads to execute_circuit."""
    req = {
        "service_id": "insightbridge.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {
            "route": "quantum",
            "quantum_capability": "quantum_execute",
            "quantum_payload": {
                "num_qubits": 2,
                "gate_sequence": [{"gate": "h", "qubits": [0]}, {"gate": "cx", "qubits": [0, 1]}],
                "shots": 100
            }
        },
        "version": "1.0.2",
        "invocation_id": "test-id-circuit-1"
    }
    resp = client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["response"]["quantum_route"] == "DELEGATED_QUANTUM"
    assert data["response"]["quantum_capability"] == "quantum_execute"
    assert "quantum_result" in data["response"]

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
