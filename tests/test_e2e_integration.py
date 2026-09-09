import pytest
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from insight_execution_service import app

from src.platform.telemetry_adapter import PlatformTelemetryAdapter
from src.platform.live_trace_store import LiveTraceStore

client = TestClient(app)

def test_enforce_endpoint_unauthorized():
    response = client.post("/enforce", json={"policy_id": "test-policy", "target": {}})
    assert response.status_code == 403 or response.status_code == 401

def test_enforce_endpoint_authorized():
    token = os.environ.get("INSIGHT_ENFORCE_TOKEN", "prod-secure-token-insight")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/enforce", json={"policy_id": "test-policy", "target": {}}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ENFORCED"

def test_invalid_invocation_schema():
    # Missing required fields
    response = client.post("/api/v1/execute", json={"service_id": "insightflow"})
    assert response.status_code == 422
    assert "Unprocessable Entity" in response.json()["error"]

def test_live_trace_store_initialization():
    store = LiveTraceStore("http://test-endpoint")
    adapter = PlatformTelemetryAdapter(trace_store=store)
    info = adapter.provider_info()
    assert info["provider"] == "LiveTraceStore"
    assert "telemetry" in info["adapter"].lower()

@pytest.mark.asyncio
async def test_global_exception_handler():
    response = client.post("/api/v1/execute", data="not json")
    assert response.status_code == 422
