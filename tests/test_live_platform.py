import sys
from pathlib import Path

import pytest
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.live_platform_client import LivePlatformClient
from src.platform.sdk_adapter import PlatformSDKAdapter
from src.integration.platform_integration_service import PlatformIntegrationService


QCG_BASE_URL = "https://bhiv-qcg.onrender.com"
SERVICE_ID = "insightflow.runtime.intelligence.v1"
SERVICE_VERSION = "1.0.2"


@pytest.fixture(scope="module", autouse=True)
def ensure_registry_populated():
    """Ensure the volatile registry is populated before running live discovery tests."""
    service = PlatformIntegrationService()
    service._ensure_runtime_registration()


@pytest.fixture(scope="module")
def client():
    return LivePlatformClient()


@pytest.fixture(scope="module")
def sdk():
    return PlatformSDKAdapter()


# ---------------------------------------------------------------------------
# Basic Platform Checks
# ---------------------------------------------------------------------------

def test_server_health(client):
    result = client.server_health()

    assert isinstance(result, dict)
    assert result.get("status") == "UP"


def test_list_services(client):
    result = client.list_services()

    assert isinstance(result, dict)
    assert "services" in result
    assert "count" in result


# ---------------------------------------------------------------------------
# SDK Discovery
# ---------------------------------------------------------------------------

def test_sdk_discovers_insight_runtime(sdk):
    services = sdk.discover_services()

    assert isinstance(services, list)

    matching = [
        service
        for service in services
        if service.get("platform_service_id") == SERVICE_ID
    ]

    assert matching, (
        f"Expected {SERVICE_ID} to be registered in the live platform registry"
    )

    service = matching[0]

    assert service["version"] == SERVICE_VERSION
    assert service["status"] == "ACTIVE"
    # The live QCG platform stores the short participant name as registered.
    assert service["service_name"] in ("InsightFlow", "InsightFlow Runtime Intelligence")



# ---------------------------------------------------------------------------
# SDK Invocation
# ---------------------------------------------------------------------------

def test_sdk_invocation(sdk):
    result = sdk.invoke_capability(
        service_id=SERVICE_ID,
        operation="execute",
        payload={
            "test_id": "pytest-sdk-invocation"
        },
        version=SERVICE_VERSION,
    )

    assert result.status == "SUCCESS"
    assert result.invocation_id
    assert result.response

    assert result.response.get("invocation_id") == result.invocation_id


# ---------------------------------------------------------------------------
# End-to-End SDK -> Verify -> Replay
# ---------------------------------------------------------------------------

def _run_verify_and_replay_test(sdk, service_id, version, test_id_prefix):
    """Helper for end-to-end live integration testing."""
    result = sdk.invoke_capability(
        service_id=service_id,
        operation="execute",
        payload={
            "test_id": f"{test_id_prefix}-sdk-verify-replay"
        },
        version=version,
    )

    assert result.status == "SUCCESS"
    invocation_id = result.invocation_id
    assert invocation_id
    
    # QCG /verify
    verify_response = requests.post(
        f"{QCG_BASE_URL}/qcg/verify",
        json={
            "invocation_id": invocation_id
        },
        timeout=30,
    )

    detail = verify_response.json().get("detail", {})
    replay_stage = detail.get("stages", {}).get("replay", {})
    assert replay_stage.get("is_valid") is True
    assert replay_stage.get("status") == "VALID"

    # QCG /replay
    replay_response = requests.get(
        f"{QCG_BASE_URL}/qcg/replay/lineage/{invocation_id}",
        timeout=30,
    )
    assert replay_response.status_code == 200
    replay = replay_response.json()
    assert replay.get("message_id") == invocation_id
    verdict = replay.get("verdict", {})
    assert verdict.get("status") == "VALID"


def test_sdk_invocation_verify_and_replay_flow(sdk):
    _run_verify_and_replay_test(
        sdk, 
        service_id="insightflow.runtime.intelligence.v1", 
        version="1.0.2", 
        test_id_prefix="pytest-flow"
    )

def test_sdk_invocation_verify_and_replay_bridge(sdk):
    _run_verify_and_replay_test(
        sdk, 
        service_id="insightbridge.runtime.intelligence.v1", 
        version="1.0.2", 
        test_id_prefix="pytest-bridge"
    )

def test_sdk_invocation_verify_and_replay_core(sdk):
    _run_verify_and_replay_test(
        sdk, 
        service_id="insightcore.runtime.intelligence.v1", 
        version="1.0.2", 
        test_id_prefix="pytest-core"
    )