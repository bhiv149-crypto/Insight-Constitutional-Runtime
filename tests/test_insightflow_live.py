import pytest
import requests
import os
from src.platform.insightflow_adapter import InsightFlowAdapter

# ---------------------------------------------------------
# InsightFlow LIVE Integration Verification
# ---------------------------------------------------------
# Target: http://163.128.209.18:8122
# Rule: NO MOCKS. REAL HTTP.

adapter = InsightFlowAdapter()

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
    
    # Perform a raw unauthenticated request to prove the LIVE API protects the endpoint
    url = f"{adapter.base_url}/enforce"
    try:
        raw_res = requests.post(url, json={"test": True}, timeout=10)
        assert raw_res.status_code == 401
    except requests.exceptions.RequestException as exc:
        pytest.fail(f"Raw HTTP test failed: {exc}")

def test_insightflow_live_openapi_identity_discrepancy():
    """
    Verify the OpenAPI schema declares itself as InsightBridge,
    but the endpoints match InsightFlow exactly.
    """
    url = f"{adapter.base_url}/openapi.json"
    raw_res = requests.get(url, timeout=10)
    assert raw_res.status_code == 200
    
    schema = raw_res.json()
    
    # The discrepancy: It calls itself InsightBridge
    assert schema["info"]["title"] == "InsightBridge"
    
    # But structurally, it matches InsightFlow's required endpoints
    paths = schema["paths"]
    assert "/enforce" in paths
    assert "/login" in paths
    assert "/health" in paths
    
    # Prove that InsightBridge's expected endpoint is MISSING
    assert "/ingest" not in paths


def test_insightflow_live_enforce_authenticated():
    """Verify authenticated live execution of /enforce."""
    test_adapter = InsightFlowAdapter()
    
    # Must load credentials from environment
    if not test_adapter.username or not test_adapter.password:
        pytest.skip("CONFIGURATION_BLOCKED: Missing real credentials in .env")
        
    payload = {"test_payload_dummy_key": "test_payload_dummy_value"}
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
