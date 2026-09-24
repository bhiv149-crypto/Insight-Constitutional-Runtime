"""
LIVE Integration Tests — Marine Quantum Runtime

These tests perform REAL HTTP requests against the deployed
Marine Quantum Runtime at:
    https://marine-quantum-runtime-final.onrender.com

No mocks, patches, stubs, or fake responses.

The runtime credential is loaded from the environment variable
``Quantum_Runtime_Auth_Key``.  If absent or empty the tests are skipped
rather than silently falling back to a stale development key.
"""

import sys
import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.quantum_adapter import MarineQuantumAdapter

LIVE_URL = "https://marine-quantum-runtime-final.onrender.com"
HAS_KEY = bool(os.getenv("Quantum_Runtime_Auth_Key"))

skip_no_key = pytest.mark.skipif(
    not HAS_KEY,
    reason="Quantum_Runtime_Auth_Key not set — live tests cannot authenticate",
)


@pytest.fixture
def live_adapter():
    """
    Return a MarineQuantumAdapter configured for the live Marine Runtime.
    Credential is resolved from environment; never hardcoded.
    """
    return MarineQuantumAdapter(mode="LIVE", runtime_url=LIVE_URL)


# ------------------------------------------------------------------ #
# 1. Health (public — no auth required)
# ------------------------------------------------------------------ #

def test_live_health_public(live_adapter):
    """GET /health — no authentication required."""
    health = live_adapter.health()
    assert health["status"] == "HEALTHY", f"Unexpected: {health}"
    assert health["mode"] == "LIVE"
    assert health["api_response"]["runtime"] == "marine-quantum-runtime"


# ------------------------------------------------------------------ #
# 2. Health detailed (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_health_detailed(live_adapter):
    """GET /health/detailed — authenticated."""
    import requests as req
    r = req.get(
        f"{LIVE_URL}/health/detailed",
        headers=live_adapter.headers,
        timeout=15,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert "backends" in data


# ------------------------------------------------------------------ #
# 3. Capability discovery (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_capabilities(live_adapter):
    """GET /api/v1/capabilities — authenticated."""
    caps = live_adapter.list_capabilities()
    assert isinstance(caps, list), f"Expected list, got {type(caps)}"
    assert len(caps) > 0, "No capabilities returned"
    cap_ids = [c.get("capability_id") for c in caps]
    assert "signal" in cap_ids, f"Missing 'signal' in {cap_ids}"


# ------------------------------------------------------------------ #
# 4. Signal execution (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_signal_execution(live_adapter):
    """POST /api/v1/capability/signal — authenticated real execution."""
    result = live_adapter.invoke_capability("signal", {
        "confidence": 0.92,
        "energy_delta": 0.0001,
        "iterations": 120,
        "node_id": "qnode_01",
        "variance": 0.002,
    })
    assert result["status"] == "SUCCESS", f"Signal failed: {json.dumps(result, indent=2)}"
    assert result["capability_id"] == "signal"
    assert result["runtime_mode"] == "LIVE"
    assert result["quantum_provider_source"] == "Marine Quantum Runtime"
    assert "invocation_id" in result
    assert "deterministic_hash" in result
    assert "output" in result
    assert result["output"]["transition"]["next"] == "CONVERGED"


# ------------------------------------------------------------------ #
# 5. Quantum pipeline execution (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_quantum_pipeline(live_adapter):
    """POST /api/v1/capability/quantum_pipeline — authenticated real execution."""
    result = live_adapter.invoke_capability("quantum_pipeline", {
        "salinity": 35.2,
        "temperature_celsius": 18.5,
        "pH": 7.8,
        "material_oxidation_potential": 0.44,
        "dissolved_oxygen_mgl": 6.5,
        "current_density_mAcm2": 0.12,
    })
    assert result["status"] == "SUCCESS", f"Pipeline failed: {json.dumps(result, indent=2)}"
    assert result["capability_id"] == "quantum_pipeline"
    assert "invocation_id" in result
    assert "deterministic_hash" in result


# ------------------------------------------------------------------ #
# 6. Quantum circuit execution (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_quantum_execute(live_adapter):
    """POST /api/v1/quantum/execute — direct circuit execution."""
    import requests as req
    body = {
        "num_qubits": 2,
        "gate_sequence": [
            {"gate": "h", "qubits": [0]},
            {"gate": "cx", "qubits": [0, 1]},
        ],
        "shots": 1024,
        "preferred_provider": "local_simulator",
        "require_simulator": True,
    }
    r = req.post(
        f"{LIVE_URL}/api/v1/quantum/execute",
        headers={**live_adapter.headers, "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["status"] == "SUCCESS"
    assert data["result"]["is_simulator"] is True
    assert "measurement_counts" in data["result"]


# ------------------------------------------------------------------ #
# 7. Failure path — missing auth returns 401
# ------------------------------------------------------------------ #

def test_live_missing_auth_returns_401():
    """Protected endpoint without API key must return 401."""
    import requests as req
    r = req.get(f"{LIVE_URL}/health/detailed", timeout=15)
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"


# ------------------------------------------------------------------ #
# 8. Failure path — invalid capability returns 422
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_invalid_payload_returns_422(live_adapter):
    """Invoke with missing required fields must return VALIDATION_ERROR."""
    result = live_adapter.invoke_capability("signal", {"bad_field": True})
    assert result["status"] == "VALIDATION_ERROR", f"Unexpected: {result}"


# ------------------------------------------------------------------ #
# 9. Quantum providers (auth required)
# ------------------------------------------------------------------ #

@skip_no_key
def test_live_quantum_providers(live_adapter):
    """GET /api/v1/quantum/providers — provider inventory."""
    import requests as req
    r = req.get(
        f"{LIVE_URL}/api/v1/quantum/providers",
        headers=live_adapter.headers,
        timeout=15,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    # The live API returns a dict keyed by provider name
    assert isinstance(data, dict), f"Unexpected type: {type(data)}"
    assert "local_simulator" in data

# ------------------------------------------------------------------ #
# 10. Failure behavior test — Unreachable runtime
# ------------------------------------------------------------------ #

def test_live_unreachable_runtime_fails_closed():
    """Ensure that an unreachable live runtime fails closed, and doesn't fall back to local."""
    unreachable_adapter = MarineQuantumAdapter(mode="LIVE", runtime_url="https://unreachable.invalid")
    
    # Check health behavior
    health = unreachable_adapter.health()
    assert health["status"] == "UNAVAILABLE"
    assert "Failed to connect" in health["error"]
    assert health["runtime_url"] == "https://unreachable.invalid"

    # Check execution behavior
    result = unreachable_adapter.invoke_capability("signal", {"test": True})
    assert result["status"] in ("UNAVAILABLE", "FAILED")
    assert result["execution_classification"] == "UNAVAILABLE / BLOCKED"
    assert "Failed to resolve" in result["error"] or "Max retries exceeded" in result["error"]
