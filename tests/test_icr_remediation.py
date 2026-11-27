"""
ICR Remediation & Negative Security Test Suite (QCG-QUANTUM-REMEDIATION-001)

Verifies:
  1. Fail-closed secret handling (no hardcoded fallback secrets for JWT_SECRET,
     CORE_CLIENT_SECRET, or INGESTION_TOKEN).
  2. Expired and tampered HS256 JWT rejection (401).
  3. Bounded idempotency cache eviction & route_quantum idempotent_replay flag.
  4. Honest fail-closed propagation in InsightBridgeParticipant (both HTTP and
     in-process quantum adapter paths).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from insight_execution_service import app as icr_app, _init_participants
from src.common.jwt_security import issue_hs256_jwt
from src.platform.insight_gateway_adapter import InsightGatewayAdapter
from src.services.insight_gateway_service import (
    _IDEMPOTENCY_CACHE,
    _MAX_IDEMPOTENCY_ENTRIES,
    _cache_put,
    app as bridge_app,
)
from src.services.insight_intelligence_service import app as core_app
from src.services.insight_workflow_service import app as flow_app


def test_fail_closed_missing_jwt_and_client_secrets(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("CORE_CLIENT_SECRET", raising=False)
    client = TestClient(core_app)

    # Missing CORE_CLIENT_SECRET -> 500 fail-closed
    res1 = client.post("/auth/issue", json={"client_id": "u1", "client_secret": "bridge_secret_123"})
    assert res1.status_code == 500

    # With CORE_CLIENT_SECRET set, missing JWT_SECRET -> 500 fail-closed
    monkeypatch.setenv("CORE_CLIENT_SECRET", "real-test-secret-001")
    res2 = client.post("/auth/issue", json={"client_id": "u1", "client_secret": "real-test-secret-001"})
    assert res2.status_code == 500


def test_fail_closed_missing_ingestion_token(monkeypatch):
    monkeypatch.delenv("INGESTION_TOKEN", raising=False)
    client = TestClient(flow_app)
    res = client.post(
        "/telemetry/ingest",
        json={
            "event_type": "decision.made",
            "decision_id": "dec-1",
            "client_id": "u1",
            "decision": "ALLOW",
            "timestamp": "2026-11-26T00:00:00Z",
        },
        headers={"X-Insight-Token": "flow_secret_789"},
    )
    assert res.status_code == 500

    adapter = InsightGatewayAdapter(base_url="http://127.0.0.1:18031")
    ad_res = adapter.ingest_telemetry({"event_type": "test"})
    assert ad_res["status"] == "FAILED"
    assert "not configured" in ad_res["error"]


def test_expired_and_tampered_jwt_rejected(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "remediation-jwt-secret-2026")
    monkeypatch.delenv("INSIGHT_EXECUTION_TOKEN", raising=False)
    monkeypatch.delenv("INSIGHT_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("INSIGHT_ENFORCE_TOKEN", raising=False)

    expired_tok = issue_hs256_jwt("u1", secret="remediation-jwt-secret-2026", ttl_seconds=-120)
    tampered_tok = issue_hs256_jwt("u1", secret="wrong-secret", ttl_seconds=3600)

    client = TestClient(bridge_app)
    r_exp = client.post(
        "/enforce",
        json={"resource": "quantum:circuit", "action": "execute"},
        headers={"Authorization": f"Bearer {expired_tok}"},
    )
    assert r_exp.status_code == 401

    r_tam = client.post(
        "/enforce",
        json={"resource": "quantum:circuit", "action": "execute"},
        headers={"Authorization": f"Bearer {tampered_tok}"},
    )
    assert r_tam.status_code == 401


def test_bounded_idempotency_cache_and_quantum_replay_flag(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "remediation-jwt-secret-2026")
    monkeypatch.setenv("INSIGHT_EXECUTION_TOKEN", "remediation-exec-token-2026")
    _IDEMPOTENCY_CACHE.clear()

    for i in range(_MAX_IDEMPOTENCY_ENTRIES + 25):
        _cache_put(f"k-{i}", {"status": "COMPLETED"})
    assert len(_IDEMPOTENCY_CACHE) == _MAX_IDEMPOTENCY_ENTRIES
    assert "k-0" not in _IDEMPOTENCY_CACHE
    assert f"k-{_MAX_IDEMPOTENCY_ENTRIES + 24}" in _IDEMPOTENCY_CACHE

    _IDEMPOTENCY_CACHE.clear()
    client = TestClient(bridge_app, headers={"Authorization": "Bearer remediation-exec-token-2026"})
    fake_mqr_ok = {
        "status": "SUCCESS",
        "result": {"measurement_counts": {"00": 512, "11": 512}, "is_simulator": True},
        "execution_digest": "a" * 64,
        "provenance_nonce": "nonce-1",
    }
    with patch("src.services.insight_gateway_service.MarineQuantumAdapter.execute_circuit", return_value=fake_mqr_ok):
        payload = {
            "route_target": "QUANTUM",
            "capability_id": "circuit_execution",
            "domain": "MARINE",
            "idempotency_key": "q-idem-001",
            "payload": {"num_qubits": 2, "gate_sequence": [{"gate": "h", "qubits": [0]}], "shots": 1024},
        }
        r1 = client.post("/api/v1/route/quantum", json=payload)
        assert r1.status_code == 200
        assert r1.json()["idempotent_replay"] is False

        r2 = client.post("/api/v1/route/quantum", json=payload)
        assert r2.status_code == 200
        assert r2.json()["idempotent_replay"] is True


def test_inprocess_bridge_quantum_unavailable_propagates_503(monkeypatch):
    monkeypatch.setenv("INSIGHT_SERVICES_HTTP", "0")
    monkeypatch.setenv("INSIGHT_EXECUTION_TOKEN", "remediation-exec-token-2026")
    _init_participants()

    icr_client = TestClient(icr_app, headers={"Authorization": "Bearer remediation-exec-token-2026"})
    with patch(
        "src.platform.quantum_adapter.MarineQuantumAdapter.execute_circuit",
        return_value={"status": "UNAVAILABLE", "error": "MQR unreachable"},
    ):
        res = icr_client.post(
            "/api/v1/execute",
            json={
                "service_id": "insightbridge.runtime.intelligence.v1",
                "operation": "execute",
                "version": "1.0.2",
                "invocation_id": "inv-inproc-fail-001",
                "payload": {
                    "route": "quantum",
                    "quantum_capability": "circuit_execution",
                    "quantum_payload": {"num_qubits": 2, "gate_sequence": []},
                },
            },
        )
        assert res.status_code == 503
        assert res.json()["status"] == "UNAVAILABLE"


def test_jwt_missing_exp_wrong_iss_and_wrong_alg_rejected(monkeypatch):
    import base64
    import hashlib
    import hmac
    import json
    from src.common.jwt_security import InvalidTokenError, decode_hs256_jwt

    secret = "test-jwt-secret-key-2026"
    monkeypatch.setenv("JWT_SECRET", secret)

    def _make_raw_jwt(header_obj, payload_obj):
        h = base64.urlsafe_b64encode(json.dumps(header_obj, separators=(",", ":")).encode()).rstrip(b"=").decode()
        p = base64.urlsafe_b64encode(json.dumps(payload_obj, separators=(",", ":")).encode()).rstrip(b"=").decode()
        sig = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
        s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        return f"{h}.{p}.{s}"

    # 1. Missing exp claim -> rejected
    tok_no_exp = _make_raw_jwt(
        {"alg": "HS256", "typ": "JWT"},
        {"iss": "sovereign-core", "aud": "insight-bridge", "sub": "u1"},
    )
    try:
        decode_hs256_jwt(tok_no_exp)
        assert False, "Expected InvalidTokenError for missing exp"
    except InvalidTokenError as exc:
        assert "exp" in str(exc)

    # 2. Wrong issuer -> rejected
    tok_bad_iss = issue_hs256_jwt("u1", secret=secret, issuer="untrusted-issuer")
    try:
        decode_hs256_jwt(tok_bad_iss)
        assert False, "Expected InvalidTokenError for wrong issuer"
    except InvalidTokenError as exc:
        assert "issuer" in str(exc).lower()

    # 3. Wrong algorithm ("none") -> rejected
    tok_none_alg = _make_raw_jwt(
        {"alg": "none", "typ": "JWT"},
        {"iss": "sovereign-core", "aud": "insight-bridge", "sub": "u1", "exp": 9999999999},
    )
    try:
        decode_hs256_jwt(tok_none_alg)
        assert False, "Expected InvalidTokenError for alg=none"
    except InvalidTokenError as exc:
        assert "algorithm" in str(exc).lower()


def test_inprocess_flow_and_bridge_parity_with_iwo_idempotency(monkeypatch, tmp_path):
    db_file = tmp_path / "test_inproc_workflows.db"
    monkeypatch.setenv("INSIGHT_SERVICES_HTTP", "0")
    monkeypatch.setenv("INSIGHT_EXECUTION_TOKEN", "remediation-exec-token-2026")
    monkeypatch.setenv("INSIGHT_WORKFLOW_DB_PATH", str(db_file))
    _init_participants()

    icr_client = TestClient(icr_app, headers={"Authorization": "Bearer remediation-exec-token-2026"})

    # 1. In-process InsightFlow executes full IWO -> ICRG -> IIE workflow with SQLite persistence & idempotency
    flow_req = {
        "service_id": "insightflow.runtime.intelligence.v1",
        "operation": "execute",
        "version": "1.0.2",
        "invocation_id": "inv-inproc-flow-1",
        "payload": {
            "workflow_type": "INTELLIGENCE",
            "task_type": "marine_signal_analysis",
            "idempotency_key": "wf-idem-inproc-001",
            "payload": {
                "salinity": 35.0,
                "temperature_celsius": 18.0,
                "pH": 8.0,
                "material_oxidation_potential": 0.4,
            },
        },
    }
    r1 = icr_client.post("/api/v1/execute", json=flow_req)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["status"] == "SUCCESS"
    wf_id_1 = d1["response"]["workflow_id"]
    assert wf_id_1.startswith("wf-")
    assert d1["response"]["workflow_state"] == "COMPLETED"

    # Duplicate submission with same idempotency_key returns the same workflow_id
    flow_req["invocation_id"] = "inv-inproc-flow-2"
    r2 = icr_client.post("/api/v1/execute", json=flow_req)
    assert r2.status_code == 200
    assert r2.json()["response"]["workflow_id"] == wf_id_1

    # 2. In-process InsightBridge routes intelligence through ICRG -> IIE
    bridge_req = {
        "service_id": "insightbridge.runtime.intelligence.v1",
        "operation": "execute",
        "version": "1.0.2",
        "invocation_id": "inv-inproc-bridge-intel",
        "payload": {
            "route": "intelligence",
            "task_type": "workload_readiness_analysis",
            "payload": {"num_qubits": 8, "shots": 1024, "p_layers": 2},
        },
    }
    r3 = icr_client.post("/api/v1/execute", json=bridge_req)
    assert r3.status_code == 200
    assert r3.json()["response"]["status"] == "executed"
    assert r3.json()["response"]["routed_result"]["status"] == "COMPLETED"

    # 3. In-process InsightBridge health reports LOCAL_READY without remote HTTP call
    h = icr_client.post(
        "/api/v1/execute",
        json={
            "service_id": "insightbridge.runtime.intelligence.v1",
            "operation": "health",
            "version": "1.0.2",
            "invocation_id": "inv-inproc-bridge-health",
            "payload": {},
        },
    )
    assert h.status_code == 200
    assert h.json()["response"]["gateway_health"] == "LOCAL_READY"


def test_inprocess_bridge_handles_dict_error_from_mqr_422(monkeypatch):
    from src.participants.insightbridge.participant import InsightBridgeParticipant

    monkeypatch.setenv("INSIGHT_SERVICES_HTTP", "0")
    bridge = InsightBridgeParticipant()
    with patch(
        "src.platform.quantum_adapter.MarineQuantumAdapter.invoke_capability",
        return_value={
            "status": "VALIDATION_ERROR",
            "error": {"status": "VALIDATION_ERROR", "detail": "Invalid BIOQUANTUM payload"},
            "execution_classification": "UNAVAILABLE / BLOCKED",
        },
    ):
        res = bridge.execute(
            {
                "route": "quantum",
                "target_capability": "quantum_pipeline",
                "quantum_payload": {"domain": "BIOQUANTUM", "n_qubits": 6},
            }
        )
        assert res["status"] == "FAILED"
        assert isinstance(res["error"], str)
        assert "VALIDATION_ERROR" in res["error"]
