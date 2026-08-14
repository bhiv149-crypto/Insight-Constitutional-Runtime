import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.live_platform_client import LivePlatformClient


@pytest.fixture
def client():
    return LivePlatformClient()


def test_server_health(client):
    result = client.server_health()

    assert isinstance(result, dict)
    assert result.get("status") == "UP"


def test_list_services(client):
    result = client.list_services()

    assert isinstance(result, dict)
    assert "services" in result
    assert "count" in result