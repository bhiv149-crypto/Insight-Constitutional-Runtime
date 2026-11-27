"""
Insight Communication & Routing Gateway (ICRG, Port 8029)

Primary Responsibilities:
  - Service-to-service routing & client management (InsightCore + Marine Quantum Runtime)
  - Request validation, JWT/Bearer authentication, and deterministic policy enforcement
  - Bounded retries, timeouts, and idempotency key deduplication
  - Cryptographic provenance anchoring (SHA-256 execution_digest + provenance_nonce)
  - Preserves backward-compatible auxiliary POST /enforce (with datetime bug fixed)
  - Exposes GET /health and GET /ready
"""

from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timezone
import json
import os
import time
from typing import Any, Dict, Optional
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException
import requests

from src.common.jwt_security import evaluate_policy, verify_bearer_or_jwt
from src.common.insight_contracts import (
    GatewayRouteRequest,
    GatewayRouteResponse,
    EnforceRequest,
    ExecutionClassification,
    IntelligenceProcessRequest,
    RouteTarget,
)
from src.platform.quantum_adapter import MarineQuantumAdapter, compute_execution_digest
from src.services.insight_intelligence_service import execute_intelligence_task


app = FastAPI(
    title="Insight Communication & Routing Gateway (ICRG)",
    description="QCG Routing, Policy Gate & Marine Quantum Adapter Boundary",
    version="1.0.0",
)

# Bounded in-memory idempotency store (key -> GatewayRouteResponse dict)
_MAX_IDEMPOTENCY_ENTRIES = 1024
_IDEMPOTENCY_CACHE: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()


def _cache_put(key: str, value: Dict[str, Any]) -> None:
    if key in _IDEMPOTENCY_CACHE:
        _IDEMPOTENCY_CACHE.move_to_end(key)
    _IDEMPOTENCY_CACHE[key] = value
    while len(_IDEMPOTENCY_CACHE) > _MAX_IDEMPOTENCY_ENTRIES:
        _IDEMPOTENCY_CACHE.popitem(last=False)


def _core_base_url() -> str:
    return (os.getenv("INSIGHT_INTELLIGENCE_BASE_URL") or os.getenv("INSIGHT_CORE_BASE_URL") or "http://163.128.209.18:8030").rstrip("/")


def _flow_telemetry_url() -> str:
    return os.getenv("FLOW_URL", "http://163.128.209.18:8031/telemetry/ingest")


def _emit_auxiliary_telemetry(event_type: str, decision_id: str, client_id: str, decision: str, reason: Optional[str] = None) -> bool:
    ingestion_token = os.getenv("INGESTION_TOKEN", "").strip()
    if not ingestion_token:
        return False
    payload = {
        "event_type": event_type,
        "decision_id": decision_id,
        "client_id": client_id,
        "decision": decision,
        "reason": reason,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    headers = {"X-Insight-Token": ingestion_token}
    try:
        res = requests.post(_flow_telemetry_url(), json=payload, headers=headers, timeout=2)
        return res.status_code == 200
    except Exception:
        return False


def _post_with_retry(
    url: str,
    json_payload: Dict[str, Any],
    headers: Dict[str, str],
    timeout_sec: float = 10.0,
    max_attempts: int = 2,
) -> tuple[Optional[requests.Response], int, Optional[str]]:
    """Bounded retry on transient network/5xx errors; never retries 4xx client errors."""
    last_err: Optional[str] = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.post(url, json=json_payload, headers=headers, timeout=timeout_sec)
            if resp.status_code < 500:
                return resp, attempt, None
            last_err = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.exceptions.RequestException as exc:
            last_err = str(exc)
    return None, max_attempts, last_err


# ---------------------------------------------------------------------------
# Health & Readiness
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "InsightBridge",
        "role": "communication_and_quantum_routing",
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    core_ok = False
    try:
        res = requests.get(f"{_core_base_url()}/health", timeout=2)
        core_ok = res.status_code == 200
    except Exception:
        core_ok = False
    quantum_adapter = MarineQuantumAdapter()
    q_health = quantum_adapter.health()
    return {
        "status": "ready" if core_ok else "degraded",
        "insight_core_reachable": core_ok,
        "quantum_runtime_status": q_health.get("status", "UNKNOWN"),
    }


# ---------------------------------------------------------------------------
# Route: Intelligence (Gateway -> Intelligence Engine)
# ---------------------------------------------------------------------------

@app.post("/api/v1/route/intelligence", response_model=GatewayRouteResponse)
async def route_intelligence(
    req: GatewayRouteRequest,
    authorization: Optional[str] = Header(None),
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    start = time.perf_counter()
    if req.idempotency_key and req.idempotency_key in _IDEMPOTENCY_CACHE:
        cached = dict(_IDEMPOTENCY_CACHE[req.idempotency_key])
        cached["idempotent_replay"] = True
        return cached

    client_id = str(claims.get("sub", "unknown"))
    decision, reason = evaluate_policy(client_id, f"intelligence:{req.task_type}", "execute")
    digest = compute_execution_digest(req.model_dump())
    nonce = uuid.uuid4().hex

    if decision == "DENY":
        raise HTTPException(status_code=403, detail=reason)

    core_url = f"{_core_base_url()}/api/v1/process"
    core_payload = {
        "task_type": req.task_type,
        "domain": req.domain,
        "payload": req.payload,
        "correlation_id": req.correlation_id,
        "trace_id": req.trace_id,
        "invocation_id": req.invocation_id,
    }
    headers = {"Content-Type": "application/json"}
    if authorization:
        headers["Authorization"] = authorization

    timeout_sec = float(os.getenv("INSIGHT_BRIDGE_TIMEOUT", "10"))
    resp, attempts, net_err = _post_with_retry(core_url, core_payload, headers, timeout_sec=timeout_sec, max_attempts=2)
    duration_ms = round((time.perf_counter() - start) * 1000, 3)

    if resp is None:
        return GatewayRouteResponse(
            status="UNAVAILABLE",
            route_target=RouteTarget.INTELLIGENCE.value,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.UNAVAILABLE.value,
            execution_digest=digest,
            provenance_nonce=nonce,
            downstream_service=core_url,
            attempts=attempts,
            duration_ms=duration_ms,
            error=f"InsightCore unreachable: {net_err}",
        )

    if resp.status_code >= 400:
        try:
            err_body = resp.json()
        except Exception:
            err_body = {"detail": resp.text}
        return GatewayRouteResponse(
            status="FAILED",
            route_target=RouteTarget.INTELLIGENCE.value,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
            execution_digest=digest,
            provenance_nonce=nonce,
            downstream_service=core_url,
            result=err_body if isinstance(err_body, dict) else {"detail": err_body},
            attempts=attempts,
            duration_ms=duration_ms,
            error=f"InsightCore returned HTTP {resp.status_code}",
        )

    core_data = resp.json()
    out = GatewayRouteResponse(
        status="COMPLETED",
        route_target=RouteTarget.INTELLIGENCE.value,
        correlation_id=req.correlation_id,
        trace_id=req.trace_id,
        invocation_id=req.invocation_id,
        execution_classification=core_data.get(
            "execution_classification",
            ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
        ),
        execution_digest=core_data.get("execution_digest", digest),
        provenance_nonce=nonce,
        downstream_service=core_url,
        result=core_data,
        attempts=attempts,
        duration_ms=duration_ms,
    )
    if req.idempotency_key:
        _cache_put(req.idempotency_key, out.model_dump())
    return out


# ---------------------------------------------------------------------------
# Route: Quantum (Gateway -> MarineQuantumAdapter)
# ---------------------------------------------------------------------------

def route_intelligence_inprocess(
    req: GatewayRouteRequest,
    client_id: str = "icr-principal",
) -> GatewayRouteResponse:
    """In-process intelligence routing through ICRG policy & idempotency boundary."""
    start = time.perf_counter()
    if req.idempotency_key and req.idempotency_key in _IDEMPOTENCY_CACHE:
        cached = dict(_IDEMPOTENCY_CACHE[req.idempotency_key])
        cached["idempotent_replay"] = True
        return GatewayRouteResponse(**cached)

    decision, reason = evaluate_policy(client_id, f"intelligence:{req.task_type}", "execute")
    digest = compute_execution_digest(req.model_dump())
    nonce = uuid.uuid4().hex
    if decision == "DENY":
        return GatewayRouteResponse(
            status="DENIED",
            route_target=RouteTarget.INTELLIGENCE.value,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.UNAVAILABLE.value,
            execution_digest=digest,
            provenance_nonce=nonce,
            downstream_service="inprocess://insight-intelligence",
            duration_ms=round((time.perf_counter() - start) * 1000, 3),
            error=reason,
        )

    intel_res = execute_intelligence_task(
        IntelligenceProcessRequest(
            task_type=req.task_type,
            domain=req.domain,
            payload=req.payload,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
        )
    )
    duration_ms = round((time.perf_counter() - start) * 1000, 3)
    out = GatewayRouteResponse(
        status="COMPLETED" if intel_res.status == "COMPLETED" else "FAILED",
        route_target=RouteTarget.INTELLIGENCE.value,
        correlation_id=req.correlation_id,
        trace_id=req.trace_id,
        invocation_id=req.invocation_id,
        execution_classification=intel_res.execution_classification,
        execution_digest=intel_res.execution_digest,
        provenance_nonce=nonce,
        downstream_service="inprocess://insight-intelligence",
        result=intel_res.model_dump(),
        attempts=1,
        duration_ms=duration_ms,
        error=intel_res.error,
    )
    if req.idempotency_key and out.status == "COMPLETED":
        _cache_put(req.idempotency_key, out.model_dump())
    return out


def route_quantum_inprocess(
    req: GatewayRouteRequest,
    client_id: str = "icr-principal",
) -> GatewayRouteResponse:
    """Shared quantum routing through ICRG policy, idempotency, and MarineQuantumAdapter."""
    start = time.perf_counter()
    if req.idempotency_key and req.idempotency_key in _IDEMPOTENCY_CACHE:
        cached = dict(_IDEMPOTENCY_CACHE[req.idempotency_key])
        cached["idempotent_replay"] = True
        return GatewayRouteResponse(**cached)

    decision, reason = evaluate_policy(client_id, f"quantum:{req.capability_id}", "execute")
    digest = compute_execution_digest(req.payload)
    nonce = uuid.uuid4().hex
    if decision == "DENY":
        raise HTTPException(status_code=403, detail=reason)

    adapter = MarineQuantumAdapter()
    if req.capability_id in ("circuit_execution", "quantum_execute") or "gate_sequence" in req.payload:
        q_result = adapter.execute_circuit(req.payload)
    else:
        q_result = adapter.invoke_capability(req.capability_id, req.payload)

    duration_ms = round((time.perf_counter() - start) * 1000, 3)
    q_status = q_result.get("status", "UNAVAILABLE")

    if q_status == "SUCCESS":
        bridge_status = "COMPLETED"
        classification = ExecutionClassification.REMOTE_QUANTUM_RUNTIME.value
        err = None
    elif q_status == "UNAVAILABLE":
        bridge_status = "UNAVAILABLE"
        classification = ExecutionClassification.UNAVAILABLE.value
        raw_err = q_result.get("error", "Marine Quantum Runtime unavailable")
        err = json.dumps(raw_err) if isinstance(raw_err, (dict, list)) else str(raw_err)
    else:
        bridge_status = "FAILED"
        classification = q_result.get("execution_classification", ExecutionClassification.UNAVAILABLE.value)
        raw_err = q_result.get("error", f"Quantum execution status: {q_status}")
        err = json.dumps(raw_err) if isinstance(raw_err, (dict, list)) else str(raw_err)

    out = GatewayRouteResponse(
        status=bridge_status,
        route_target=RouteTarget.QUANTUM.value,
        correlation_id=req.correlation_id,
        trace_id=req.trace_id,
        invocation_id=req.invocation_id,
        execution_classification=classification,
        execution_digest=q_result.get("execution_digest", digest),
        provenance_nonce=q_result.get("provenance_nonce", nonce),
        downstream_service=adapter.base_url,
        result=q_result,
        attempts=1,
        duration_ms=duration_ms,
        error=err,
    )
    if req.idempotency_key and bridge_status == "COMPLETED":
        _cache_put(req.idempotency_key, out.model_dump())
    return out


@app.post("/api/v1/route/quantum", response_model=GatewayRouteResponse)
async def route_quantum(
    req: GatewayRouteRequest,
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    client_id = str(claims.get("sub", "unknown"))
    return route_quantum_inprocess(req, client_id=client_id)


# ---------------------------------------------------------------------------
# Auxiliary Backward-Compatible Security Enforcement Endpoint (VM :8029)
# ---------------------------------------------------------------------------

@app.post("/enforce")
async def enforce(
    request_body: EnforceRequest,
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    decision_id = str(uuid.uuid4())
    client_id = str(claims.get("sub", "unknown"))
    decision, reason = evaluate_policy(client_id, request_body.resource, request_body.action)
    telemetry_sent = _emit_auxiliary_telemetry("decision.made", decision_id, client_id, decision, reason)
    if decision == "DENY":
        raise HTTPException(status_code=403, detail=reason)
    return {
        "decision": decision,
        "decision_id": decision_id,
        "client_id": client_id,
        "telemetry_synced": telemetry_sent,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("INSIGHT_BRIDGE_PORT", "8029"))
    uvicorn.run(app, host="0.0.0.0", port=port)
