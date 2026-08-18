"""
Tests for MarineQuantumAdapter
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from src.platform.quantum_adapter import MarineQuantumAdapter


def test_quantum_adapter_health():
    adapter = MarineQuantumAdapter()
    health = adapter.health()
    assert health["status"] in ("HEALTHY", "DEGRADED")
    assert health["mode"] == "LOCAL"
    assert "heartbeat" in health
    assert health["heartbeat"].get("heartbeat") == "ALIVE"


def test_quantum_adapter_list_capabilities():
    adapter = MarineQuantumAdapter()
    caps = adapter.list_capabilities()
    assert isinstance(caps, list)
    cap_ids = [c.get("capability_id") for c in caps]
    assert "quantum_pipeline" in cap_ids
    assert "signal" in cap_ids


def test_quantum_adapter_discover_capability():
    adapter = MarineQuantumAdapter()
    descriptor = adapter.discover_capability("quantum_pipeline")
    assert descriptor is not None
    assert descriptor["capability_id"] == "quantum_pipeline"
    assert descriptor["authority_ceiling"] == "QUANTUM_EXECUTION"


def test_quantum_adapter_invocation_quantum_pipeline():
    adapter = MarineQuantumAdapter()
    payload = {
        "salinity": 35.2,
        "temperature_celsius": 18.5,
        "pH": 7.8,
        "material_oxidation_potential": 0.44,
        "dissolved_oxygen_mgl": 6.5,
        "current_density_mAcm2": 0.12,
    }
    result = adapter.invoke_capability("quantum_pipeline", payload)
    assert result["status"] == "SUCCESS"
    assert result["capability_id"] == "quantum_pipeline"
    assert result["runtime_mode"] == "LOCAL"
    assert "invocation_id" in result
    assert "deterministic_hash" in result
    assert "degradation_probability" in result["output"]
    det_event = result["output"].get("deterministic_event", {})
    assert det_event.get("risk_level") in ("ELEVATED", "NORMAL", "HIGH", "CRITICAL")


def test_quantum_adapter_malformed_payload():
    adapter = MarineQuantumAdapter()
    # Salinity out of range [0.0, 50.0]
    payload = {
        "salinity": 999.0,
        "temperature_celsius": 18.5,
        "pH": 7.8,
        "material_oxidation_potential": 0.44,
        "dissolved_oxygen_mgl": 6.5,
        "current_density_mAcm2": 0.12,
    }
    result = adapter.invoke_capability("quantum_pipeline", payload)
    # Marine typed attachment / execution catches boundary violations
    assert result["status"] in ("VALIDATION_ERROR", "FAILED")
    assert len(result.get("errors", [])) > 0


def test_quantum_adapter_unavailable_mode():
    adapter = MarineQuantumAdapter(mode="remote_cluster")
    health = adapter.health()
    assert health["status"] == "UNAVAILABLE"
    assert "Unsupported QUANTUM_RUNTIME_MODE" in health["error"]

    result = adapter.invoke_capability("quantum_pipeline", {})
    assert result["status"] == "UNAVAILABLE"
    assert "Unsupported QUANTUM_RUNTIME_MODE" in result["error"]
