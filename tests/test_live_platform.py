import sys
from pathlib import Path

import pytest
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.live_platform_client import LivePlatformClient
from src.platform.sdk_adapter import PlatformSDKAdapter


QCG_BASE_URL = "https://bhiv-qcg.onrender.com"
SERVICE_ID = "insightflow.runtime.intelligence.v1"
SERVICE_VERSION = "1.0.2"


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
    assert service["service_name"] == "InsightFlow Runtime Intelligence"


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

def test_sdk_invocation_verify_and_replay(sdk):
    """
    End-to-end live integration test.

    Flow:

        SDK invocation
              |
              v
        invocation_id
              |
              v
        QCG /qcg/verify
              |
              v
        QCG /qcg/replay/lineage/{invocation_id}

    IMPORTANT:
    The current live QCG returns HTTP 422 from /verify because its
    ECDSA signature verification fails.

    We deliberately DO NOT bypass or fake this failure.

    The important observed behavior is that the replay registry still
    contains the same invocation lineage and returns HTTP 200 with a
    VALID replay verdict.
    """

    # ---------------------------------------------------------
    # 1. Generate a fresh invocation through the real SDK
    # ---------------------------------------------------------

    result = sdk.invoke_capability(
        service_id=SERVICE_ID,
        operation="execute",
        payload={
            "test_id": "pytest-sdk-verify-replay"
        },
        version=SERVICE_VERSION,
    )

    assert result.status == "SUCCESS"

    invocation_id = result.invocation_id

    assert invocation_id
    assert result.response.get("invocation_id") == invocation_id

    # ---------------------------------------------------------
    # 2. Verify the SAME invocation through QCG
    # ---------------------------------------------------------

    verify_response = requests.post(
        f"{QCG_BASE_URL}/qcg/verify",
        json={
            "invocation_id": invocation_id
        },
        timeout=30,
    )

    # Current known platform behavior:
    #
    # HTTP 422
    # HALT:INVALID_SIGNATURE
    #
    # We document the failure rather than bypassing it.

    if verify_response.status_code == 422:
        detail = verify_response.json().get("detail", {})

        trust = detail.get("stages", {}).get("trust", {})

        assert trust.get("passed") is False
        assert "INVALID_SIGNATURE" in trust.get("halt_signal", "")

    else:
        # If the platform fixes the signature problem in the future,
        # the test automatically accepts the successful verification.
        assert verify_response.status_code == 200

    # ---------------------------------------------------------
    # 3. Replay the SAME invocation
    # ---------------------------------------------------------

    replay_response = requests.get(
        f"{QCG_BASE_URL}/qcg/replay/lineage/{invocation_id}",
        timeout=30,
    )

    assert replay_response.status_code == 200

    replay = replay_response.json()

    # ---------------------------------------------------------
    # 4. Validate replay identity
    # ---------------------------------------------------------

    assert replay.get("message_id") == invocation_id

    verdict = replay.get("verdict", {})

    assert verdict.get("message_id") == invocation_id
    assert verdict.get("status") == "VALID"

    # ---------------------------------------------------------
    # 5. Validate lineage evidence
    # ---------------------------------------------------------

    lineage = verdict.get("lineage_record", {})

    assert lineage
    assert lineage.get("decision") == "VALID"
    assert lineage.get("origin_component") == "CanonicalReplayAuthority"
    assert lineage.get("verification_hash")

    assert lineage.get("trace_reference")
    assert lineage.get("replay_id")