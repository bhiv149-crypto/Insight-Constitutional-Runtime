"""
Insight Workflow Orchestrator (IWO, Port 8031)

Primary Responsibilities:
  - Durable workflow lifecycle management (SQLite-backed state surviving restarts)
  - Explicit states: CREATED -> VALIDATED -> RUNNING -> COMPLETED | FAILED | CANCELLED | UNAVAILABLE
  - Sequential/Hybrid step orchestration via InsightBridge (Intelligence & Quantum)
  - Result aggregation, error propagation, and LiveTraceStore evidence emission
  - Preserves backward-compatible auxiliary POST /telemetry/ingest
  - Exposes GET /health and GET /ready
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hmac
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import Any, Dict, List, Optional
import uuid

from fastapi import Depends, FastAPI, Header, HTTPException
import requests

from src.common.jwt_security import verify_bearer_or_jwt
from src.common.insight_contracts import (
    ExecutionClassification,
    GatewayRouteRequest,
    RouteTarget,
    TelemetryEvent,
    WorkflowExecutionResponse,
    WorkflowState,
    WorkflowStepRecord,
    WorkflowSubmitRequest,
)
from src.platform.live_trace_store import LiveTraceStore
from src.services.insight_gateway_service import (
    route_intelligence_inprocess,
    route_quantum_inprocess,
)


app = FastAPI(
    title="Insight Workflow Orchestrator (IWO)",
    description="QCG Workflow Orchestration, Durable State & Telemetry Service",
    version="1.0.0",
)


def _bridge_base_url() -> str:
    return (os.getenv("INSIGHT_GATEWAY_BASE_URL") or os.getenv("INSIGHT_BRIDGE_BASE_URL") or "http://163.128.209.18:8029").rstrip("/")


def _db_path() -> str:
    return (
        os.getenv("INSIGHT_WORKFLOW_DB_PATH")
        or os.getenv("INSIGHT_FLOW_DB_PATH")
        or str(Path(__file__).resolve().parents[2] / "insightflow_workflows.db")
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _init_db() -> None:
    db_file = _db_path()
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    with closing(sqlite3.connect(db_file)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                workflow_type TEXT NOT NULL,
                state TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                invocation_id TEXT NOT NULL,
                steps_json TEXT NOT NULL,
                aggregated_result_json TEXT NOT NULL,
                evidence_recorded INTEGER NOT NULL,
                evidence_details_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error TEXT,
                idempotency_key TEXT
            )
            """
        )
        cols = {row[1] for row in conn.execute("PRAGMA table_info(workflows)").fetchall()}
        if "idempotency_key" not in cols:
            conn.execute("ALTER TABLE workflows ADD COLUMN idempotency_key TEXT")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_workflows_idempotency_key ON workflows(idempotency_key)"
        )
        conn.commit()


def _save_workflow(record: WorkflowExecutionResponse, idempotency_key: Optional[str] = None) -> None:
    _init_db()
    with closing(sqlite3.connect(_db_path())) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO workflows (
                workflow_id, workflow_type, state, correlation_id, trace_id,
                invocation_id, steps_json, aggregated_result_json,
                evidence_recorded, evidence_details_json, created_at, updated_at, error, idempotency_key
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, (SELECT idempotency_key FROM workflows WHERE workflow_id = ?)))
            """,
            (
                record.workflow_id,
                record.workflow_type,
                record.state.value,
                record.correlation_id,
                record.trace_id,
                record.invocation_id,
                json.dumps([s.model_dump() for s in record.steps]),
                json.dumps(record.aggregated_result),
                1 if record.evidence_recorded else 0,
                json.dumps(record.evidence_details),
                record.created_at,
                record.updated_at,
                record.error,
                idempotency_key,
                record.workflow_id,
            ),
        )
        conn.commit()


def _row_to_workflow(row: tuple) -> WorkflowExecutionResponse:
    steps = [WorkflowStepRecord(**s) for s in json.loads(row[6])]
    return WorkflowExecutionResponse(
        workflow_id=row[0],
        workflow_type=row[1],
        state=WorkflowState(row[2]),
        correlation_id=row[3],
        trace_id=row[4],
        invocation_id=row[5],
        steps=steps,
        aggregated_result=json.loads(row[7]),
        evidence_recorded=bool(row[8]),
        evidence_details=json.loads(row[9]),
        created_at=row[10],
        updated_at=row[11],
        error=row[12],
    )


def _load_workflow(workflow_id: str) -> Optional[WorkflowExecutionResponse]:
    _init_db()
    with closing(sqlite3.connect(_db_path())) as conn:
        row = conn.execute(
            "SELECT workflow_id, workflow_type, state, correlation_id, trace_id, "
            "invocation_id, steps_json, aggregated_result_json, evidence_recorded, "
            "evidence_details_json, created_at, updated_at, error FROM workflows WHERE workflow_id = ?",
            (workflow_id,),
        ).fetchone()
    return _row_to_workflow(row) if row else None


def _load_workflow_by_idempotency_key(idempotency_key: str) -> Optional[WorkflowExecutionResponse]:
    _init_db()
    with closing(sqlite3.connect(_db_path())) as conn:
        row = conn.execute(
            "SELECT workflow_id, workflow_type, state, correlation_id, trace_id, "
            "invocation_id, steps_json, aggregated_result_json, evidence_recorded, "
            "evidence_details_json, created_at, updated_at, error FROM workflows "
            "WHERE idempotency_key = ? ORDER BY created_at DESC LIMIT 1",
            (idempotency_key,),
        ).fetchone()
    return _row_to_workflow(row) if row else None


def _call_bridge(
    endpoint_path: str,
    route_payload: Dict[str, Any],
    authorization: Optional[str],
) -> tuple[str, Dict[str, Any], float, Optional[str]]:
    start = time.perf_counter()
    url = f"{_bridge_base_url()}{endpoint_path}"
    headers = {"Content-Type": "application/json"}
    if authorization:
        headers["Authorization"] = authorization
    timeout_sec = float(os.getenv("INSIGHT_FLOW_TIMEOUT", "15"))

    try:
        resp = requests.post(url, json=route_payload, headers=headers, timeout=timeout_sec)
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        if resp.status_code >= 400:
            return "FAILED", {"http_status": resp.status_code, "body": resp.text[:300]}, duration_ms, f"Bridge HTTP {resp.status_code}"
        data = resp.json()
        return data.get("status", "FAILED"), data, duration_ms, data.get("error")
    except requests.exceptions.RequestException as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        return "UNAVAILABLE", {}, duration_ms, f"InsightBridge unreachable: {exc}"


# ---------------------------------------------------------------------------
# Health & Readiness
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    _init_db()
    return {
        "status": "healthy",
        "service": "InsightFlow",
        "role": "workflow_orchestration",
        "version": "1.0.0",
    }


@app.get("/ready")
async def ready():
    _init_db()
    bridge_ok = False
    try:
        res = requests.get(f"{_bridge_base_url()}/health", timeout=2)
        bridge_ok = res.status_code == 200
    except Exception:
        bridge_ok = False
    return {
        "status": "ready" if bridge_ok else "degraded",
        "insight_bridge_reachable": bridge_ok,
        "durable_store": "sqlite",
    }


# ---------------------------------------------------------------------------
# Workflow Orchestration Endpoints
# ---------------------------------------------------------------------------

def run_workflow_pipeline(
    req: WorkflowSubmitRequest,
    authorization: Optional[str] = None,
    client_id: str = "icr-principal",
    use_http: bool = True,
) -> WorkflowExecutionResponse:
    """
    Shared deterministic workflow orchestrator (HTTP & in-process modes).
    Deduplicates on idempotency_key when provided and persists every state transition.
    """
    if req.idempotency_key:
        existing = _load_workflow_by_idempotency_key(req.idempotency_key)
        if existing is not None:
            return existing

    workflow_id = f"wf-{uuid.uuid4().hex[:12]}"
    now = _utc_now()
    wf = WorkflowExecutionResponse(
        workflow_id=workflow_id,
        workflow_type=req.workflow_type.value,
        state=WorkflowState.CREATED,
        correlation_id=req.correlation_id,
        trace_id=req.trace_id,
        invocation_id=req.invocation_id,
        created_at=now,
        updated_at=now,
    )
    _save_workflow(wf, idempotency_key=req.idempotency_key)

    wf.state = WorkflowState.VALIDATED
    wf.updated_at = _utc_now()
    _save_workflow(wf)

    wf.state = WorkflowState.RUNNING
    wf.updated_at = _utc_now()
    _save_workflow(wf)

    steps: List[WorkflowStepRecord] = []
    aggregated: Dict[str, Any] = {}

    # Step 1: Intelligence (for INTELLIGENCE or HYBRID)
    if req.workflow_type in (RouteTarget.INTELLIGENCE, RouteTarget.HYBRID):
        intel_idem = f"{req.idempotency_key}-intel" if req.idempotency_key else None
        if use_http:
            intel_payload = {
                "route_target": RouteTarget.INTELLIGENCE.value,
                "task_type": req.task_type,
                "domain": req.domain,
                "payload": req.payload,
                "correlation_id": req.correlation_id,
                "trace_id": req.trace_id,
                "invocation_id": req.invocation_id,
                "idempotency_key": intel_idem,
            }
            st_status, st_data, st_ms, st_err = _call_bridge("/api/v1/route/intelligence", intel_payload, authorization)
        else:
            gw_resp = route_intelligence_inprocess(
                GatewayRouteRequest(
                    route_target=RouteTarget.INTELLIGENCE,
                    task_type=req.task_type,
                    domain=req.domain,
                    payload=req.payload,
                    correlation_id=req.correlation_id,
                    trace_id=req.trace_id,
                    invocation_id=req.invocation_id,
                    idempotency_key=intel_idem,
                ),
                client_id=client_id,
            )
            st_status = gw_resp.status
            st_data = gw_resp.model_dump()
            st_ms = gw_resp.duration_ms
            st_err = gw_resp.error

        steps.append(
            WorkflowStepRecord(
                step_name="intelligence_processing",
                target_service="InsightBridge->InsightCore",
                status=st_status,
                duration_ms=st_ms,
                execution_classification=st_data.get(
                    "execution_classification", ExecutionClassification.UNAVAILABLE.value
                ),
                output=st_data,
                error=st_err,
            )
        )
        aggregated["intelligence"] = st_data.get("result", st_data)
        if st_status != "COMPLETED":
            wf.steps = steps
            wf.aggregated_result = aggregated
            wf.state = WorkflowState.UNAVAILABLE if st_status == "UNAVAILABLE" else WorkflowState.FAILED
            wf.error = st_err or f"Intelligence step ended with status {st_status}"
            wf.updated_at = _utc_now()
            _save_workflow(wf)
            return wf

    # Step 2: Quantum (for QUANTUM or HYBRID)
    if req.workflow_type in (RouteTarget.QUANTUM, RouteTarget.HYBRID):
        q_idem = f"{req.idempotency_key}-quantum" if req.idempotency_key else None
        if use_http:
            q_payload = {
                "route_target": RouteTarget.QUANTUM.value,
                "capability_id": req.capability_id,
                "domain": req.domain,
                "payload": req.payload,
                "correlation_id": req.correlation_id,
                "trace_id": req.trace_id,
                "invocation_id": req.invocation_id,
                "idempotency_key": q_idem,
            }
            q_status, q_data, q_ms, q_err = _call_bridge("/api/v1/route/quantum", q_payload, authorization)
        else:
            gw_resp = route_quantum_inprocess(
                GatewayRouteRequest(
                    route_target=RouteTarget.QUANTUM,
                    capability_id=req.capability_id,
                    domain=req.domain,
                    payload=req.payload,
                    correlation_id=req.correlation_id,
                    trace_id=req.trace_id,
                    invocation_id=req.invocation_id,
                    idempotency_key=q_idem,
                ),
                client_id=client_id,
            )
            q_status = gw_resp.status
            q_data = gw_resp.model_dump()
            q_ms = gw_resp.duration_ms
            q_err = gw_resp.error

        steps.append(
            WorkflowStepRecord(
                step_name="quantum_execution",
                target_service="InsightBridge->MarineQuantumRuntime",
                status=q_status,
                duration_ms=q_ms,
                execution_classification=q_data.get(
                    "execution_classification", ExecutionClassification.UNAVAILABLE.value
                ),
                output=q_data,
                error=q_err,
            )
        )
        aggregated["quantum"] = q_data.get("result", q_data)
        if q_status != "COMPLETED":
            wf.steps = steps
            wf.aggregated_result = aggregated
            wf.state = WorkflowState.UNAVAILABLE if q_status == "UNAVAILABLE" else WorkflowState.FAILED
            wf.error = q_err or f"Quantum step ended with status {q_status}"
            wf.updated_at = _utc_now()
            _save_workflow(wf)
            return wf

    # All required steps completed
    trace_store = LiveTraceStore()
    trace_resp = trace_store.record_execution_trace(
        workflow_id=workflow_id,
        correlation_id=req.correlation_id,
        trace_id=req.trace_id,
        invocation_id=req.invocation_id,
        workflow_type=req.workflow_type.value,
        status="COMPLETED",
    )
    evidence_ok = trace_resp.get("status") != "FAILED"

    wf.steps = steps
    wf.aggregated_result = aggregated
    wf.state = WorkflowState.COMPLETED
    wf.evidence_recorded = evidence_ok
    wf.evidence_details = trace_resp
    wf.updated_at = _utc_now()
    _save_workflow(wf)
    return wf


@app.post("/api/v1/workflows/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    req: WorkflowSubmitRequest,
    authorization: Optional[str] = Header(None),
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    client_id = str(claims.get("sub", "icr-principal"))
    return run_workflow_pipeline(req, authorization=authorization, client_id=client_id, use_http=True)


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowExecutionResponse)
async def get_workflow(
    workflow_id: str,
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    wf = _load_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return wf


@app.post("/api/v1/workflows/{workflow_id}/cancel", response_model=WorkflowExecutionResponse)
async def cancel_workflow(
    workflow_id: str,
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    wf = _load_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    if wf.state in (WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED):
        raise HTTPException(status_code=409, detail=f"Cannot cancel workflow in terminal state {wf.state.value}")
    wf.state = WorkflowState.CANCELLED
    wf.updated_at = _utc_now()
    _save_workflow(wf)
    return wf


# ---------------------------------------------------------------------------
# Auxiliary Backward-Compatible Telemetry Ingestion Endpoint (VM :8031)
# ---------------------------------------------------------------------------

@app.post("/telemetry/ingest")
async def ingest_telemetry(
    event: TelemetryEvent,
    x_insight_token: Optional[str] = Header(None),
):
    expected = os.getenv("INGESTION_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=500, detail="INGESTION_TOKEN is not configured; failing closed.")
    if not x_insight_token or not hmac.compare_digest(x_insight_token, expected):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid Ingestion Token")

    bucket_dir = os.getenv(
        "INSIGHT_FLOW_BUCKET_DIR",
        str(Path(__file__).resolve().parents[2] / "evidence" / "telemetry_bucket"),
    )
    os.makedirs(bucket_dir, exist_ok=True)
    ts_clean = event.timestamp.replace(":", "-").replace(".", "-")
    filepath = os.path.join(bucket_dir, f"decision_{event.decision_id}_{ts_clean}.json")
    artifact = {
        "decision_id": event.decision_id,
        "timestamp": event.timestamp,
        "client_id": event.client_id,
        "decision": event.decision,
        "metadata": {
            "issuer": "sovereign-core",
            "enforcer": "insight-bridge",
            "reason": event.reason,
        },
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)
    return {"status": "ingested", "decision_id": event.decision_id}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("INSIGHT_FLOW_PORT", "8031"))
    uvicorn.run(app, host="0.0.0.0", port=port)
