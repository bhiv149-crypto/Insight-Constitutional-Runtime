import sys
import pytest
from unittest.mock import patch, Mock
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.quantum_adapter import MarineQuantumAdapter


@pytest.fixture
def live_adapter():
    return MarineQuantumAdapter(mode="live", runtime_url="https://marine-quantum-runtime-final.onrender.com")


def test_live_health_success(live_adapter):
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        health = live_adapter.health()
        assert health["status"] == "HEALTHY"
        assert health["mode"] == "LIVE"


def test_live_capabilities_success(live_adapter):
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = [{"capability_id": "quantum_pipeline"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        caps = live_adapter.list_capabilities()
        assert len(caps) == 1
        assert caps[0]["capability_id"] == "quantum_pipeline"


def test_live_invoke_success(live_adapter):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "result": {"some_data": 42}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = live_adapter.invoke_capability("quantum_pipeline", {"payload": "test"})
        
        assert result["status"] == "SUCCESS"
        assert result["runtime_mode"] == "LIVE"
        assert result["quantum_provider_source"] == "Marine Quantum Runtime"
        assert result["execution_classification"] == "QUANTUM_LIVE"
        assert result["result"]["execution_classification"] == "QUANTUM_LIVE"
        assert result["result"]["provider"] == "live_provider"


def test_live_invoke_auth_failure(live_adapter):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 401
        
        mock_exc = requests.exceptions.HTTPError("401 Unauthorized")
        mock_exc.response = mock_response
        mock_post.side_effect = mock_exc

        result = live_adapter.invoke_capability("quantum_pipeline", {"payload": "test"})
        
        assert result["status"] == "UNAVAILABLE"
        assert result["capability_id"] == "quantum_pipeline"
        assert "Authentication failed" in result["error"]
        assert result["runtime_mode"] == "LIVE"
        assert result["execution_classification"] == "BLOCKED"


def test_live_invoke_validation_error(live_adapter):
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"detail": [{"msg": "validation failed"}]}
        
        mock_exc = requests.exceptions.HTTPError("422 Unprocessable Entity")
        mock_exc.response = mock_response
        mock_post.side_effect = mock_exc

        result = live_adapter.invoke_capability("quantum_pipeline", {"payload": "test"})
        
        assert result["status"] == "VALIDATION_ERROR"
        assert result["capability_id"] == "quantum_pipeline"
        assert result["runtime_mode"] == "LIVE"
        assert result["execution_classification"] == "UNAVAILABLE / BLOCKED"
