import sys
from pathlib import Path
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from insight_execution_service import app, _init_participants

# Initialize participants before tests
_init_participants()

client = TestClient(app)

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

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
