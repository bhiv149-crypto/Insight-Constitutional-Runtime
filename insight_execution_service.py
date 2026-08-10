"""
Insight Stack — Canonical Execution Service

Exposes:
    InsightFlow
    InsightBridge
    InsightCore

through the canonical:

    POST /api/v1/execute

This service is an execution host only.

It does NOT:
- register itself
- perform discovery
- implement Platform Runtime logic
- create a registry
- call the copied QCG repository
- depend on localhost QCG
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# -------------------------------------------------------------------------
# Project path
# -------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# -------------------------------------------------------------------------
# Insight participants
# -------------------------------------------------------------------------

from src.participants.insightflow.participant import InsightFlowParticipant
from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.participants.insightcore.participant import InsightCoreParticipant
from src.common.constants import RUNTIME_IDENTITIES


# -------------------------------------------------------------------------
# Application
# -------------------------------------------------------------------------

app = FastAPI(
    title="Insight Stack Execution Service",
    description=(
        "Canonical TANTRA Platform Runtime execution endpoint "
        "for InsightFlow, InsightBridge and InsightCore."
    ),
    version="1.0.0",
)


# -------------------------------------------------------------------------
# Participant registry
# -------------------------------------------------------------------------

_PARTICIPANTS: Dict[str, Any] = {}


def _init_participants() -> None:
    """
    Initialise all Insight participants exactly once.
    """

    global _PARTICIPANTS

    if _PARTICIPANTS:
        return

    _PARTICIPANTS = {
        RUNTIME_IDENTITIES["INSIGHTFLOW"]: InsightFlowParticipant(),
        RUNTIME_IDENTITIES["INSIGHTBRIDGE"]: InsightBridgeParticipant(),
        RUNTIME_IDENTITIES["INSIGHTCORE"]: InsightCoreParticipant(),
    }

    for participant in _PARTICIPANTS.values():
        lifecycle = getattr(participant, "lifecycle", None)

        if lifecycle is not None:
            activate = getattr(lifecycle, "activate", None)

            if callable(activate):
                activate()


# -------------------------------------------------------------------------
# Request model
# -------------------------------------------------------------------------

class InvocationRequest(BaseModel):
    service_id: str
    operation: str
    payload: dict
    version: str
    invocation_id: str


# -------------------------------------------------------------------------
# Evidence helpers
# -------------------------------------------------------------------------

def _make_hash(data: dict) -> str:
    """
    Deterministic SHA-256 hash for request/response evidence.
    """

    canonical = json.dumps(
        data,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_response(
    *,
    invocation_id: str,
    service_id: str,
    operation: str,
    status: str,
    response: dict,
    duration_ms: float,
    request_payload: dict,
    error: Optional[str] = None,
    retry_count: int = 0,
) -> dict:
    """
    Build the canonical InvocationResult-compatible response.

    Important:
    Application failures remain failures.
    They are NOT converted into SUCCESS.
    """

    request_hash = _make_hash(request_payload)
    response_hash = _make_hash(response)
    timestamp = _utc_timestamp()

    evidence = {
        "invocation_id": invocation_id,
        "service_id": service_id,
        "operation": operation,
        "request_hash": request_hash,
        "response_hash": response_hash,
        "trust_method": "CLASSICAL",
        "duration_ms": duration_ms,
        "status": status,
        "timestamp": timestamp,
    }

    return {
        "invocation_id": invocation_id,
        "service_id": service_id,
        "operation": operation,
        "status": status,
        "response": response,
        "duration_ms": duration_ms,
        "trust_method": "CLASSICAL",
        "evidence": evidence,
        "error": error,
        "retry_count": retry_count,
        "timestamp": timestamp,
    }


# -------------------------------------------------------------------------
# Supported operations
# -------------------------------------------------------------------------

SUPPORTED_OPERATIONS = {
    "execute",
    "health",
}


def _dispatch(
    participant: Any,
    operation: str,
    payload: dict,
) -> tuple[Optional[dict], Optional[str]]:
    """
    Dispatch an operation to the participant.

    Returns:
        (result, error)
    """

    if operation == "execute":
        return participant.execute(payload), None

    if operation == "health":
        return participant.health(), None

    return None, (
        f"Operation '{operation}' is not supported "
        f"by this participant."
    )


# -------------------------------------------------------------------------
# Canonical execution endpoint
# -------------------------------------------------------------------------

@app.post("/api/v1/execute")
async def execute(req: InvocationRequest):
    """
    Canonical Insight capability execution endpoint.

    Request:
        service_id
        operation
        payload
        version
        invocation_id

    Response:
        InvocationResult-compatible envelope.
    """

    start_time = time.perf_counter()

    invocation_id = req.invocation_id

    request_payload = {
        "service_id": req.service_id,
        "operation": req.operation,
        "payload": req.payload,
        "version": req.version,
        "invocation_id": invocation_id,
    }

    # -------------------------------------------------------------
    # 1. Service lookup
    # -------------------------------------------------------------

    participant = _PARTICIPANTS.get(req.service_id)

    if participant is None:
        duration_ms = (time.perf_counter() - start_time) * 1000

        return JSONResponse(
            status_code=404,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="NOT_FOUND",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error=(
                    f"Service '{req.service_id}' "
                    "is not hosted by this execution service."
                ),
            ),
        )

    # -------------------------------------------------------------
    # 2. Version validation
    # -------------------------------------------------------------

    participant_version = getattr(participant, "version", None)

    if participant_version is None:
        duration_ms = (time.perf_counter() - start_time) * 1000

        return JSONResponse(
            status_code=500,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="FAILED",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error="Participant version is not configured.",
            ),
        )

    if req.version != participant_version:
        duration_ms = (time.perf_counter() - start_time) * 1000

        return JSONResponse(
            status_code=400,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="VERSION_REJECTED",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error=(
                    f"Version '{req.version}' is not supported. "
                    f"Supported version is '{participant_version}'."
                ),
            ),
        )

    # -------------------------------------------------------------
    # 3. Operation validation + participant execution
    # -------------------------------------------------------------

    try:
        result, error = _dispatch(
            participant,
            req.operation,
            req.payload,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Unsupported operation
        if error is not None:
            return JSONResponse(
                status_code=400,
                content=_make_response(
                    invocation_id=invocation_id,
                    service_id=req.service_id,
                    operation=req.operation,
                    status="INVALID_OP",
                    response={},
                    duration_ms=duration_ms,
                    request_payload=request_payload,
                    error=error,
                ),
            )

        # Genuine successful execution
        if not isinstance(result, dict):
            result = {"result": result}

        return JSONResponse(
            status_code=200,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="SUCCESS",
                response=result,
                duration_ms=duration_ms,
                request_payload=request_payload,
            ),
        )

    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000

        return JSONResponse(
            status_code=500,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="FAILED",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error=str(exc),
            ),
        )


# -------------------------------------------------------------------------
# Aggregate health
# -------------------------------------------------------------------------

@app.get("/api/v1/health")
async def global_health():
    """
    Aggregate health of all Insight participants.
    """

    services = {}
    all_up = True

    for service_id, participant in _PARTICIPANTS.items():

        try:
            health = participant.health()

            state = health.get("state", "UNKNOWN")

            healthy_states = {
                "INITIALISED",
                "RUNNING",
                "HEALTHY",
                "ACTIVE",
            }

            status = (
                "UP"
                if state in healthy_states
                else "DEGRADED"
            )

            if status != "UP":
                all_up = False

            services[service_id] = {
                "service_id": service_id,
                "state": state,
                "status": status,
            }

        except Exception as exc:

            all_up = False

            services[service_id] = {
                "service_id": service_id,
                "status": "ERROR",
                "error": str(exc),
            }

    return {
        "status": "UP" if all_up else "DEGRADED",
        "service": "Insight Stack Execution Service",
        "version": "1.0.0",
        "participants": list(_PARTICIPANTS.keys()),
        "participant_health": services,
        "timestamp": _utc_timestamp(),
    }


# -------------------------------------------------------------------------
# Per-service health
# -------------------------------------------------------------------------

@app.get("/api/v1/health/{service_id}")
async def service_health(service_id: str):

    participant = _PARTICIPANTS.get(service_id)

    if participant is None:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_id}' not hosted here.",
        )

    health = participant.health()

    state = health.get("state", "UNKNOWN")

    healthy_states = {
        "INITIALISED",
        "RUNNING",
        "HEALTHY",
        "ACTIVE",
    }

    return {
        "service_id": service_id,
        "status": (
            "UP"
            if state in healthy_states
            else "DEGRADED"
        ),
        "version": participant.version,
        "state": state,
        "timestamp": _utc_timestamp(),
    }


# -------------------------------------------------------------------------
# Hosted services metadata
# -------------------------------------------------------------------------

@app.get("/api/v1/services")
async def list_hosted_services():

    service_url = os.environ.get(
        "INSIGHT_SERVICE_URL",
        "",
    ).rstrip("/")

    services = []

    for service_id, participant in _PARTICIPANTS.items():

        execution_endpoint = (
            f"{service_url}/api/v1/execute"
            if service_url
            else "/api/v1/execute"
        )

        health_endpoint = (
            f"{service_url}/api/v1/health/{service_id}"
            if service_url
            else f"/api/v1/health/{service_id}"
        )

        services.append(
            {
                "service_id": service_id,
                "participant": participant.name,
                "version": participant.version,
                "execution_endpoint": execution_endpoint,
                "health_endpoint": health_endpoint,
            }
        )

    return {
        "services": services,
        "count": len(services),
    }


# -------------------------------------------------------------------------
# Root
# -------------------------------------------------------------------------

@app.get("/")
async def root():

    service_url = os.environ.get(
        "INSIGHT_SERVICE_URL",
        "",
    ).rstrip("/")

    return {
        "service": "Insight Stack Execution Service",
        "status": "ONLINE",
        "version": "1.0.0",
        "participants": list(_PARTICIPANTS.keys()),
        "canonical_execution_endpoint": (
            f"{service_url}/api/v1/execute"
            if service_url
            else "/api/v1/execute"
        ),
        "health_endpoint": (
            f"{service_url}/api/v1/health"
            if service_url
            else "/api/v1/health"
        ),
        "docs": "/docs",
    }


# -------------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():

    _init_participants()

    service_url = os.environ.get(
        "INSIGHT_SERVICE_URL",
        "",
    ).rstrip("/")

    print("=" * 64)
    print("  Insight Stack Execution Service")
    print("=" * 64)

    print(
        f"  Participants : "
        f"{', '.join(_PARTICIPANTS.keys())}"
    )

    print(
        f"  Execute URL  : "
        f"{service_url}/api/v1/execute"
        if service_url
        else "  Execute URL  : /api/v1/execute"
    )

    print(
        f"  Health URL   : "
        f"{service_url}/api/v1/health"
        if service_url
        else "  Health URL   : /api/v1/health"
    )

    print("=" * 64)


# -------------------------------------------------------------------------
# Direct entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8003"))

    uvicorn.run(
        "insight_execution_service:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )