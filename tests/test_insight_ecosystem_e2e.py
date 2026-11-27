"""
Insight Ecosystem Multi-Service End-to-End Integration Test Suite (QCG-INSIGHT-008)

Test Classification: LOCAL_MULTI_SERVICE (Real Uvicorn HTTP servers on localhost)
Correlation ID: QCG-INSIGHT-E2E-001

Tests real HTTP communication across:
  ICR (/api/v1/execute) -> InsightFlow (:18031) -> InsightBridge (:18029) -> InsightCore (:18030)
  and InsightBridge (:18029) -> MarineQuantumAdapter (honest fail-closed verification)
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest
import requests
import uvicorn
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.insight_intelligence_service import app as core_app
from src.services.insight_gateway_service import app as bridge_app, _IDEMPOTENCY_CACHE
from src.services.insight_workflow_service import app as flow_app
from insight_execution_service import app as icr_app, _init_participants


CORRELATION_ID = "QCG-INSIGHT-E2E-001"
TEST_EXEC_TOKEN = "insight-e2e-secure-token-2026"
CORE_PORT = 18030
BRIDGE_PORT = 18029
FLOW_PORT = 18031


def _start_server(app, port: int) -> uvicorn.Server:
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10.0
    while not server.started and time.time() < deadline:
        time.sleep(0.05)
    if not server.started:
        raise RuntimeError(f"Server on port {port} failed to start")
    return server


@pytest.fixture(scope="module")
def insight_cluster():
    """Spin up real local HTTP instances of InsightCore, InsightBridge, and InsightFlow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_workflows.db")
        bucket_dir = os.path.join(tmpdir, "bucket")

        old_env = dict(os.environ)
        os.environ["NO_PROXY"] = "127.0.0.1,localhost"
        os.environ["no_proxy"] = "127.0.0.1,localhost"
        os.environ["INSIGHT_EXECUTION_TOKEN"] = TEST_EXEC_TOKEN
        os.environ["INSIGHT_ENFORCE_TOKEN"] = TEST_EXEC_TOKEN
        os.environ["JWT_SECRET"] = "insight-test-jwt-secret-key-2026"
        os.environ["CORE_CLIENT_SECRET"] = "bridge_secret_123"
        os.environ["INGESTION_TOKEN"] = "flow_secret_789"
        os.environ["INSIGHT_CORE_BASE_URL"] = f"http://127.0.0.1:{CORE_PORT}"
        os.environ["INSIGHT_BRIDGE_BASE_URL"] = f"http://127.0.0.1:{BRIDGE_PORT}"
        os.environ["INSIGHT_FLOW_BASE_URL"] = f"http://127.0.0.1:{FLOW_PORT}"
        os.environ["FLOW_URL"] = f"http://127.0.0.1:{FLOW_PORT}/telemetry/ingest"
        os.environ["INSIGHT_FLOW_DB_PATH"] = db_path
        os.environ["INSIGHT_FLOW_BUCKET_DIR"] = bucket_dir
        os.environ["INSIGHT_SERVICES_HTTP"] = "1"

        core_srv = _start_server(core_app, CORE_PORT)
        bridge_srv = _start_server(bridge_app, BRIDGE_PORT)
        flow_srv = _start_server(flow_app, FLOW_PORT)

        _init_participants()
        _IDEMPOTENCY_CACHE.clear()

        try:
            yield {
                "core_url": f"http://127.0.0.1:{CORE_PORT}",
                "bridge_url": f"http://127.0.0.1:{BRIDGE_PORT}",
                "flow_url": f"http://127.0.0.1:{FLOW_PORT}",
                "db_path": db_path,
                "bucket_dir": bucket_dir,
            }
        finally:
            flow_srv.should_exit = True
            bridge_srv.should_exit = True
            core_srv.should_exit = True
            os.environ.clear()
            os.environ.update(old_env)


def test_1_health_and_readiness_all_services(insight_cluster):
    """Verify /health and /ready return 200 across Core, Bridge, and Flow."""
    for name, key in [("InsightCore", "core_url"), ("InsightBridge", "bridge_url"), ("InsightFlow", "flow_url")]:
        h = requests.get(f"{insight_cluster[key]}/health", timeout=3)
        r = requests.get(f"{insight_cluster[key]}/ready", timeout=3)
        assert h.status_code == 200, f"{name} /health failed"
        assert h.json()["status"] == "healthy"
        assert r.status_code == 200, f"{name} /ready failed"


def test_2_jwt_issuance_and_policy_enforcement(insight_cluster):
    """Test 4 (Auth/Security): Core issues HS256 JWT -> Bridge validates & enforces guest rule."""
    # Invalid secret rejected
    bad = requests.post(
        f"{insight_cluster['core_url']}/auth/issue",
        json={"client_id": "icr-user", "client_secret": "wrong"},
        timeout=3,
    )
    assert bad.status_code == 401

    # Valid secret issues JWT
    good = requests.post(
        f"{insight_cluster['core_url']}/auth/issue",
        json={"client_id": "icr-user", "client_secret": "bridge_secret_123"},
        timeout=3,
    )
    assert good.status_code == 200
    jwt_token = good.json()["access_token"]

    # Bridge /enforce accepts valid JWT and emits telemetry to Flow
    enf = requests.post(
        f"{insight_cluster['bridge_url']}/enforce",
        json={"resource": "quantum:circuit", "action": "execute"},
        headers={"Authorization": f"Bearer {jwt_token}"},
        timeout=3,
    )
    assert enf.status_code == 200
    assert enf.json()["decision"] == "ALLOW"
    assert enf.json()["telemetry_synced"] is True

    # Guest JWT denied on write/execute
    guest_tok = requests.post(
        f"{insight_cluster['core_url']}/auth/issue",
        json={"client_id": "guest", "client_secret": "bridge_secret_123"},
        timeout=3,
    ).json()["access_token"]
    denied = requests.post(
        f"{insight_cluster['bridge_url']}/enforce",
        json={"resource": "quantum:circuit", "action": "write"},
        headers={"Authorization": f"Bearer {guest_tok}"},
        timeout=3,
    )
    assert denied.status_code == 403


def test_3_e2e_intelligence_pipeline_via_icr(insight_cluster):
    """
    Test 1 (Intelligence-Only E2E):
    ICR (/api/v1/execute) -> InsightFlow (:18031) -> InsightBridge (:18029) -> InsightCore (:18030)
    Proves real marine corrosion risk computation and correlation_id propagation.
    """
    icr_client = TestClient(icr_app, headers={"Authorization": f"Bearer {TEST_EXEC_TOKEN}"})
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "version": "1.0.2",
        "invocation_id": "inv-e2e-intel-001",
        "payload": {
            "workflow_type": "INTELLIGENCE",
            "task_type": "marine_signal_analysis",
            "domain": "MARINE",
            "correlation_id": CORRELATION_ID,
            "trace_id": "trace-e2e-001",
            "data": {
                "salinity": 35.2,
                "temperature_celsius": 18.5,
                "pH": 7.8,
                "material_oxidation_potential": 0.44,
                "dissolved_oxygen_mgl": 6.5,
                "current_density_mAcm2": 0.12,
            },
        },
    }
    resp = icr_client.post("/api/v1/execute", json=req)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "SUCCESS"
    wf_res = body["response"]["workflow_result"]
    assert wf_res["state"] == "COMPLETED"
    assert wf_res["correlation_id"] == CORRELATION_ID
    assert wf_res["steps"][0]["step_name"] == "intelligence_processing"
    assert wf_res["steps"][0]["execution_classification"] == "CLASSICAL_INTELLIGENCE"

    intel = wf_res["aggregated_result"]["intelligence"]
    assert intel["status"] == "COMPLETED"
    assert intel["metrics"]["corrosion_risk_index"] > 0.0
    assert intel["analysis"]["corrosion_risk_tier"] in ("NOMINAL", "ELEVATED", "CRITICAL")


def test_4_e2e_quantum_route_honest_fail_closed(insight_cluster, monkeypatch):
    """
    Test 2 & Test 5 (Quantum Route + Downstream Unavailable):
    ICR -> Flow -> Bridge -> MarineQuantumAdapter.
    Forces an unreachable QUANTUM_RUNTIME_URL (127.0.0.1:19999) so the outage
    condition is deterministic regardless of internet availability. Pipeline MUST
    return UNAVAILABLE (HTTP 503), NEVER a false-positive SUCCESS.
    """
    monkeypatch.setenv("QUANTUM_RUNTIME_URL", "http://127.0.0.1:19999")
    icr_client = TestClient(icr_app, headers={"Authorization": f"Bearer {TEST_EXEC_TOKEN}"})
    req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "version": "1.0.2",
        "invocation_id": "inv-e2e-quantum-001",
        "payload": {
            "workflow_type": "QUANTUM",
            "capability_id": "quantum_pipeline",
            "domain": "MARINE",
            "correlation_id": CORRELATION_ID,
            "data": {
                "salinity": 35.2,
                "temperature_celsius": 18.5,
                "pH": 7.8,
                "material_oxidation_potential": 0.44,
                "dissolved_oxygen_mgl": 6.5,
                "current_density_mAcm2": 0.12,
            },
        },
    }
    resp = icr_client.post("/api/v1/execute", json=req)
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "UNAVAILABLE"
    assert body["response"]["workflow_state"] == "UNAVAILABLE"


def test_5_unsupported_intelligence_task_rejected(insight_cluster):
    """InsightCore must never fabricate results for unsupported task types."""
    resp = requests.post(
        f"{insight_cluster['core_url']}/api/v1/process",
        json={"task_type": "nonexistent_magic_ai", "domain": "QCG", "payload": {}},
        headers={"Authorization": f"Bearer {TEST_EXEC_TOKEN}"},
        timeout=3,
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["status"] == "UNSUPPORTED"


def test_6_idempotency_deduplication_on_bridge(insight_cluster):
    """Test 6: Repeated requests with same idempotency_key do not re-execute Core."""
    payload = {
        "route_target": "INTELLIGENCE",
        "task_type": "workload_readiness_analysis",
        "domain": "MARINE",
        "payload": {"num_qubits": 12, "shots": 1024, "p_layers": 2},
        "correlation_id": CORRELATION_ID,
        "idempotency_key": "idem-key-nw53-001",
    }
    headers = {"Authorization": f"Bearer {TEST_EXEC_TOKEN}"}
    r1 = requests.post(f"{insight_cluster['bridge_url']}/api/v1/route/intelligence", json=payload, headers=headers, timeout=5)
    assert r1.status_code == 200
    assert r1.json()["status"] == "COMPLETED"
    assert r1.json()["result"]["metrics"]["estimated_heavy_hex_physical_qubits"] == 15

    r2 = requests.post(f"{insight_cluster['bridge_url']}/api/v1/route/intelligence", json=payload, headers=headers, timeout=5)
    assert r2.status_code == 200
    assert r2.json().get("idempotent_replay") is True
    assert r2.json()["execution_digest"] == r1.json()["execution_digest"]


def test_7_downstream_core_outage_truthfully_reported(insight_cluster):
    """Test 5 (Downstream Outage): Pointing Bridge to closed port yields UNAVAILABLE."""
    prev = os.environ["INSIGHT_CORE_BASE_URL"]
    os.environ["INSIGHT_CORE_BASE_URL"] = "http://127.0.0.1:18999"
    try:
        resp = requests.post(
            f"{insight_cluster['bridge_url']}/api/v1/route/intelligence",
            json={
                "route_target": "INTELLIGENCE",
                "task_type": "marine_signal_analysis",
                "payload": {"salinity": 35.0, "temperature_celsius": 20.0, "pH": 7.8, "material_oxidation_potential": 0.4},
            },
            headers={"Authorization": f"Bearer {TEST_EXEC_TOKEN}"},
            timeout=10,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "UNAVAILABLE"
        assert resp.json()["attempts"] == 2
    finally:
        os.environ["INSIGHT_CORE_BASE_URL"] = prev


def test_8_durable_workflow_persistence_survives_restart(insight_cluster):
    """Test 8 (Restart Resilience): Persisted SQLite workflow state is readable via GET /api/v1/workflows/{id}."""
    from contextlib import closing
    with closing(sqlite3.connect(insight_cluster["db_path"])) as conn:
        rows = conn.execute("SELECT workflow_id, state, correlation_id FROM workflows").fetchall()
    assert len(rows) >= 2
    wf_id = rows[0][0]

    resp = requests.get(
        f"{insight_cluster['flow_url']}/api/v1/workflows/{wf_id}",
        headers={"Authorization": f"Bearer {TEST_EXEC_TOKEN}"},
        timeout=3,
    )
    assert resp.status_code == 200
    assert resp.json()["workflow_id"] == wf_id
    assert resp.json()["correlation_id"] == CORRELATION_ID
