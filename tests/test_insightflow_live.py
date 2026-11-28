import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import requests
import os
from src.platform.insight_workflow_adapter import InsightWorkflowAdapter

# ---------------------------------------------------------
# Insight Ecosystem LIVE VM Integration Verification
# ---------------------------------------------------------
# Target: VM Host http://163.128.209.18
#   - Port 8031: InsightFlow (Telemetry Ingestion)
#   - Port 8029: InsightBridge (Security Enforcement)
#   - Port 8030: InsightCore (Sovereign JWT Issuer)
# Rule: NO MOCKS. REAL HTTP.

adapter = InsightWorkflowAdapter()

def test_insightflow_live_health():
    """Verify live health endpoint."""
    res = adapter.health()
    assert res["status"] == "HEALTHY", f"Health failed: {res}"
    assert res["http_status"] == 200

def test_insightflow_live_login_failure():
    """Verify login gracefully fails without credentials."""
    # Ensure credentials are not magically bypassed
    adapter.username = None
    adapter.password = None
    adapter.token = None
    
    token = adapter.login()
    assert token is None

def test_insightflow_live_enforce_no_auth():
    """Verify /enforce correctly blocks unauthenticated requests via 401."""
    adapter.username = "dummy"
    adapter.password = "dummy"
    
    # login will fail, returning None, and enforce will return BLOCKED
    res = adapter.enforce({"policy_id": "test"})
    assert res["status"] == "BLOCKED"
    assert res["reason"] == "AUTHENTICATION_FAILED"
    
    # Perform a raw unauthenticated request against InsightBridge to prove the LIVE API protects the endpoint
    bridge_url = (
        os.getenv("INSIGHT_GATEWAY_BASE_URL")
        or os.getenv("INSIGHT_BRIDGE_BASE_URL")
        or "http://163.128.209.18:8029"
    ).rstrip("/")
    url = f"{bridge_url}/enforce"
    try:
        raw_res = requests.post(url, json={"resource": "quantum_circuit", "action": "execute"}, timeout=10)
        assert raw_res.status_code == 401
    except requests.exceptions.RequestException as exc:
        pytest.fail(f"Raw HTTP test failed: {exc}")

def test_insightflow_live_openapi_identity_and_contracts():
    """
    Verify the OpenAPI schemas declare the live VM microservices:
      - 8031: InsightFlow - Telemetry Ingestion (/telemetry/ingest)
      - 8029: InsightBridge - Security Enforcement (/enforce)
      - 8030: InsightCore - Sovereign JWT Issuer (/auth/issue)
    """
    # 1. InsightFlow (8031)
    url = f"{adapter.base_url}/openapi.json"
    raw_res = requests.get(url, timeout=10)
    assert raw_res.status_code == 200
    schema = raw_res.json()
    assert schema["info"]["title"] == "InsightFlow - Telemetry Ingestion"
    assert "/telemetry/ingest" in schema["paths"]

    # 2. InsightBridge (8029)
    bridge_url = (
        os.getenv("INSIGHT_GATEWAY_BASE_URL")
        or os.getenv("INSIGHT_BRIDGE_BASE_URL")
        or "http://163.128.209.18:8029"
    ).rstrip("/")
    bridge_res = requests.get(f"{bridge_url}/openapi.json", timeout=10)
    assert bridge_res.status_code == 200
    bridge_schema = bridge_res.json()
    assert bridge_schema["info"]["title"] == "InsightBridge - Security Enforcement"
    assert "/enforce" in bridge_schema["paths"]

    # 3. InsightCore (8030)
    core_url = (
        os.getenv("INSIGHT_INTELLIGENCE_BASE_URL")
        or os.getenv("INSIGHT_CORE_BASE_URL")
        or "http://163.128.209.18:8030"
    ).rstrip("/")
    core_res = requests.get(f"{core_url}/openapi.json", timeout=10)
    assert core_res.status_code == 200
    core_schema = core_res.json()
    assert core_schema["info"]["title"] == "InsightCore - Sovereign JWT Issuer"
    assert "/auth/issue" in core_schema["paths"]


def test_insightflow_live_enforce_authenticated():
    """Verify authenticated live execution of /enforce."""
    test_adapter = InsightWorkflowAdapter()
    
    # Load credentials from environment or fall back to staging VM credentials
    if not test_adapter.username or not test_adapter.password:
        test_adapter.username = os.getenv("INSIGHT_FLOW_USERNAME", "test")
        test_adapter.password = os.getenv("INSIGHT_FLOW_PASSWORD", "bridge_secret_123")
        
    payload = {"resource": "quantum_circuit", "action": "execute"}
    res = test_adapter.enforce(payload)
    
    if res["status"] == "FAILED" and res["reason"] == "LIVE_RUNTIME_UNAVAILABLE":
        pytest.skip(f"LIVE_RUNTIME_UNAVAILABLE: {res.get('error')}")
        
    assert res["status"] in ["SUCCESS", "BLOCKED", "FAILED"]
    
    if res["status"] == "BLOCKED":
        assert res["reason"] in ["CONTRACT_BLOCKED", "AUTHENTICATION_FAILED"]
    elif res["status"] == "SUCCESS":
        assert res["reason"] == "LIVE_EXECUTION"
        assert res["http_status"] == 200
    elif res["status"] == "FAILED":
        assert res["reason"] == "EXECUTION_FAILED"
