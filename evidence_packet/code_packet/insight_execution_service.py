"""
insight_execution_service.py — Insight Stack Canonical Execution Service

Exposes the Insight Stack participants (InsightFlow, InsightBridge, InsightCore)
as a live HTTP service conforming to Kanishk's TANTRA Platform Runtime invocation
contract.

Canonical Invocation Endpoint
-------------------------------
POST /api/v1/execute

    {
        "service_id":    "insightflow.runtime.intelligence.v1",
        "operation":     "execute",
        "payload":       {},
        "version":       "1.0.0",
        "invocation_id": "<uuid>"
    }

    → InvocationResult:
    {
        "status":        "SUCCESS",
        "invocation_id": "<uuid>",
        "service_id":    "insightflow.runtime.intelligence.v1",
        "operation":     "execute",
        "response":      { <participant output> },
        "duration_ms":   ...,
        "trust_method":  "CLASSICAL",
        "evidence":      { ... },
        "error":         null,
        "retry_count":   0,
        "timestamp":     "..."
    }

Supported Status Values
-----------------------
SUCCESS        — operation completed normally
FAILED         — participant raised an exception
INVALID_OP     — operation not supported by this participant
NOT_FOUND      — service_id not recognised by this service

Design Principles
-----------------
- This service contains ZERO Platform Runtime logic.
- It does not register, discover, or relay to other services.
- It is an execution host — it receives a canonical invocation request
  and routes it to the matching participant's execute() method.
- The Platform SDK runs on the CALLER side.
- No circular dependency with the Platform Registry.
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# -------------------------------------------------------------------------
# Path setup — resolve project root so src/ is importable
# -------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
        "Canonical TANTRA Platform Runtime execution endpoint for "
        "InsightFlow, InsightBridge, and InsightCore."
    ),
    version="1.0.0",
)

# -------------------------------------------------------------------------
# Participant Registry
# -------------------------------------------------------------------------

_PARTICIPANTS: Dict[str, Any] = {}

def _init_participants():
    """Instantiate all three participants once at startup."""
    global _PARTICIPANTS
    _PARTICIPANTS = {
        RUNTIME_IDENTITIES["INSIGHTFLOW"]:   InsightFlowParticipant(),
        RUNTIME_IDENTITIES["INSIGHTBRIDGE"]: InsightBridgeParticipant(),
        RUNTIME_IDENTITIES["INSIGHTCORE"]:   InsightCoreParticipant(),
    }
    
    # Activate participants for production
    for p in _PARTICIPANTS.values():
        if hasattr(p, "lifecycle") and hasattr(p.lifecycle, "activate"):
            p.lifecycle.activate()

# -------------------------------------------------------------------------
# Request / Response Models
# -------------------------------------------------------------------------

class InvocationRequest(BaseModel):
    service_id: str
    operation: str
    payload: dict
    version: str
    invocation_id: str


def _make_hash(data: dict) -> str:
    """Deterministic SHA-256 over a dict."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _make_response(
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
    """Build a canonical InvocationResult dict."""
    request_hash = _make_hash(request_payload)
    response_hash = _make_hash(response)

    evidence = {
        "invocation_id": invocation_id,
        "service_id": service_id,
        "operation": operation,
        "request_hash": request_hash,
        "response_hash": response_hash,
        "trust_method": "CLASSICAL",
        "duration_ms": duration_ms,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -------------------------------------------------------------------------
# Execution Router
# -------------------------------------------------------------------------

SUPPORTED_OPERATIONS = {
    "execute": "_execute_op",
    "health":  "_health_op",
}


def _execute_op(participant, payload: dict) -> dict:
    """Route to participant.execute()."""
    return participant.execute(payload)


def _health_op(participant, payload: dict) -> dict:
    """Route to participant.health()."""
    return participant.health()


def _dispatch(participant, operation: str, payload: dict):
    """
    Dispatch an operation to the correct participant method.

    Returns (result_dict, error_str_or_None).
    """
    if operation not in SUPPORTED_OPERATIONS:
        return None, f"Operation '{operation}' is not supported by this participant."

    handler_name = SUPPORTED_OPERATIONS[operation]
    if handler_name == "_execute_op":
        return _execute_op(participant, payload), None
    if handler_name == "_health_op":
        return _health_op(participant, payload), None
    return None, f"Internal routing error for operation '{operation}'."


# -------------------------------------------------------------------------
# /api/v1/execute — Canonical Invocation Endpoint
# -------------------------------------------------------------------------

@app.post("/api/v1/execute")
async def execute(req: InvocationRequest):
    """
    Canonical capability invocation endpoint.

    Accepts Kanishk's PlatformCapabilitySDK invocation payload and
    routes it to the matching Insight participant.
    """
    invocation_id = req.invocation_id or str(uuid.uuid4())
    start_time = time.time()

    request_payload = {
        "service_id": req.service_id,
        "operation": req.operation,
        "payload": req.payload,
        "version": req.version,
        "invocation_id": invocation_id,
    }

    # Participant lookup
    participant = _PARTICIPANTS.get(req.service_id)
    if participant is None:
        duration_ms = (time.time() - start_time) * 1000
        return JSONResponse(
            status_code=200,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="NOT_FOUND",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error=f"Service '{req.service_id}' is not hosted by this execution service.",
            ),
        )

    # Version check
    if req.version != participant.version:
        duration_ms = (time.time() - start_time) * 1000
        return JSONResponse(
            status_code=200,
            content=_make_response(
                invocation_id=invocation_id,
                service_id=req.service_id,
                operation=req.operation,
                status="VERSION_REJECTED",
                response={},
                duration_ms=duration_ms,
                request_payload=request_payload,
                error=f"Version '{req.version}' is not supported. Supported version is '{participant.version}'.",
            ),
        )

    # Dispatch to participant
    try:
        result, error = _dispatch(participant, req.operation, req.payload)
        duration_ms = (time.time() - start_time) * 1000

        if error:
            return JSONResponse(
                status_code=200,
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
        duration_ms = (time.time() - start_time) * 1000
        return JSONResponse(
            status_code=200,
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
# /api/v1/health — Platform-Facing Health Endpoint
# -------------------------------------------------------------------------

@app.get("/api/v1/health")
async def global_health():
    """
    Platform-level health endpoint.

    Returns the aggregate health of all hosted participants.
    """
    services = {}
    all_up = True

    for service_id, participant in _PARTICIPANTS.items():
        try:
            ph = participant.health()
            state = ph.get("state", "UNKNOWN")
            services[service_id] = {
                "service_id": service_id,
                "state": state,
                "status": "UP" if state in ("INITIALISED", "RUNNING", "HEALTHY", "ACTIVE") else "DEGRADED",
            }
            if state not in ("INITIALISED", "RUNNING", "HEALTHY", "ACTIVE"):
                all_up = False
        except Exception as exc:
            services[service_id] = {"service_id": service_id, "status": "ERROR", "error": str(exc)}
            all_up = False

    return {
        "status": "UP" if all_up else "DEGRADED",
        "service": "Insight Stack Execution Service",
        "version": "1.0.0",
        "participants": list(_PARTICIPANTS.keys()),
        "participant_health": services,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/health/{service_id}")
async def service_health(service_id: str):
    """
    Per-service health endpoint for SDK health checks.
    """
    participant = _PARTICIPANTS.get(service_id)
    if not participant:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_id}' not hosted here.",
        )
    ph = participant.health()
    state = ph.get("state", "UNKNOWN")
    return {
        "service_id": service_id,
        "status": "UP" if state in ("INITIALISED", "RUNNING", "HEALTHY") else "DEGRADED",
        "version": participant.version,
        "state": state,
        "uptime_seconds": 0.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -------------------------------------------------------------------------
# /api/v1/services — Discovery metadata
# -------------------------------------------------------------------------

@app.get("/api/v1/services")
async def list_hosted_services():
    """
    List all services hosted by this execution service.
    """
    service_url = os.environ.get("INSIGHT_SERVICE_URL", "http://127.0.0.1:8003")
    services = []
    for service_id, participant in _PARTICIPANTS.items():
        services.append({
            "service_id": service_id,
            "participant": participant.name,
            "version": participant.version,
            "execution_endpoint": f"{service_url}/api/v1/execute",
            "health_endpoint": f"{service_url}/api/v1/health/{service_id}",
        })
    return {"services": services, "count": len(services)}


# -------------------------------------------------------------------------
# Root
# -------------------------------------------------------------------------

@app.get("/")
async def root():
    service_url = os.environ.get("INSIGHT_SERVICE_URL", "http://127.0.0.1:8003")
    return {
        "service": "Insight Stack Execution Service",
        "status": "ONLINE",
        "version": "1.0.0",
        "participants": list(_PARTICIPANTS.keys()),
        "canonical_execution_endpoint": f"{service_url}/api/v1/execute",
        "health_endpoint": f"{service_url}/api/v1/health",
        "docs": "/docs",
    }


# -------------------------------------------------------------------------
# Startup
# -------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    _init_participants()
    service_url = os.environ.get("INSIGHT_SERVICE_URL", "http://127.0.0.1:8003")
    print("=" * 64)
    print("  Insight Stack Execution Service")
    print("=" * 64)
    print(f"  Participants : {', '.join(_PARTICIPANTS.keys())}")
    print(f"  Execute URL  : {service_url}/api/v1/execute")
    print(f"  Health URL   : {service_url}/api/v1/health")
    print("=" * 64)


# -------------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8003))
    service_url = os.environ.get("INSIGHT_SERVICE_URL", f"http://127.0.0.1:{port}")

    _init_participants()

    uvicorn.run(
        "insight_execution_service:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
