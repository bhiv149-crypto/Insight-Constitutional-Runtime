"""
Insight Intelligence Engine (IIE, Port 8030)

Primary Responsibilities:
  - Genuine deterministic computational intelligence processing aligned with QCG domains:
      1. marine_signal_analysis: Evaluates marine telemetry / corrosion electrochemistry
      2. workload_readiness_analysis: Evaluates QUBO/QAOA circuit qubit & depth feasibility
      3. domain_optimization_scoring: Scores constraint feasibility & cost/priority ratios
  - Preserves backward-compatible auxiliary POST /auth/issue (Sovereign JWT Issuer)
  - Exposes GET /health and GET /ready
  - Never fabricates results: unsupported task_types return explicit UNSUPPORTED status.
"""

from __future__ import annotations

import hmac
import math
import os
import time
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException

from src.common.jwt_security import issue_hs256_jwt, verify_bearer_or_jwt
from src.common.insight_contracts import (
    AuthIssueRequest,
    ExecutionClassification,
    IntelligenceProcessRequest,
    IntelligenceProcessResult,
)
from src.platform.quantum_adapter import compute_execution_digest


app = FastAPI(
    title="Insight Intelligence Engine (IIE)",
    description="QCG Sovereign Intelligence Processing & Auxiliary JWT Issuer",
    version="1.0.0",
)


def _analyze_marine_signal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic electrochemical & marine sensor intelligence evaluation.
    Computes corrosion risk index and operational recommendations from physical inputs.
    """
    required_keys = ["salinity", "temperature_celsius", "pH", "material_oxidation_potential"]
    missing = [k for k in required_keys if k not in payload]
    if missing:
        raise ValueError(f"Missing required marine telemetry fields: {missing}")

    salinity = float(payload["salinity"])
    temp = float(payload["temperature_celsius"])
    ph = float(payload["pH"])
    ox_pot = float(payload["material_oxidation_potential"])
    dissolved_o2 = float(payload.get("dissolved_oxygen_mgl", 6.5))
    current_density = float(payload.get("current_density_mAcm2", 0.1))

    # Deterministic corrosion risk score in [0.0, 1.0]
    salinity_factor = min(max(salinity / 45.0, 0.0), 1.0)
    acidity_factor = min(max(abs(7.5 - ph) / 4.5, 0.0), 1.0)
    ox_factor = min(max((ox_pot + 0.5) / 2.0, 0.0), 1.0)
    o2_factor = min(max(dissolved_o2 / 15.0, 0.0), 1.0)
    temp_factor = min(max((temp + 5.0) / 50.0, 0.0), 1.0)

    risk_score = round(
        0.28 * ox_factor + 0.24 * salinity_factor + 0.20 * acidity_factor + 0.16 * o2_factor + 0.12 * temp_factor,
        4,
    )
    risk_tier = "CRITICAL" if risk_score >= 0.70 else "ELEVATED" if risk_score >= 0.45 else "NOMINAL"

    return {
        "analysis": {
            "domain": "MARINE",
            "corrosion_risk_tier": risk_tier,
            "recommended_quantum_routing": risk_score >= 0.40,
            "cathodic_protection_needed": ox_pot > 0.30 or current_density > 0.15,
        },
        "metrics": {
            "corrosion_risk_index": risk_score,
            "salinity_psu": salinity,
            "temperature_celsius": temp,
            "pH": ph,
            "oxidation_potential_v": ox_pot,
        },
    }


def _analyze_workload_readiness(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic QUBO / QAOA hardware readiness & scaling evaluation.
    """
    num_qubits = int(payload.get("num_qubits", 0))
    shots = int(payload.get("shots", 1024))
    p_layers = int(payload.get("p_layers", 1))

    if num_qubits <= 0:
        raise ValueError("num_qubits must be a positive integer")

    classical_states = 2 ** min(num_qubits, 64)
    classical_tractable = num_qubits <= 28
    estimated_2q_gates = num_qubits * (num_qubits - 1) // 2 * p_layers
    fits_heron_r2 = num_qubits <= 156

    return {
        "analysis": {
            "classical_tractable_exact": classical_tractable,
            "fits_ibm_heron_r2_156q": fits_heron_r2,
            "recommended_execution_tier": "REMOTE_QUANTUM_RUNTIME" if num_qubits <= 29 else "PHYSICAL_QPU",
        },
        "metrics": {
            "num_qubits": num_qubits,
            "shots": shots,
            "p_layers": p_layers,
            "search_space_size_capped": classical_states,
            "estimated_all_to_all_2q_gates": estimated_2q_gates,
            "estimated_heavy_hex_physical_qubits": math.ceil(num_qubits * 1.25),
        },
    }


def _score_domain_optimization(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic constraint & objective scoring for domain optimization candidates.
    """
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("payload.candidates must be a non-empty list of candidate dicts")

    scored = []
    for idx, item in enumerate(candidates):
        if not isinstance(item, dict):
            raise ValueError(f"Candidate at index {idx} must be a dict")
        cost = float(item.get("cost", 0.0))
        priority = float(item.get("priority", 1.0))
        feasible = bool(item.get("feasible", True))
        net_score = round(priority - 0.1 * cost if feasible else -9999.0, 4)
        scored.append({"index": idx, "id": item.get("id", f"cand-{idx}"), "feasible": feasible, "net_score": net_score})

    scored.sort(key=lambda x: x["net_score"], reverse=True)
    feasible_count = sum(1 for s in scored if s["feasible"])

    return {
        "analysis": {
            "best_candidate": scored[0],
            "ranked_candidates": scored,
        },
        "metrics": {
            "total_candidates": len(scored),
            "feasible_candidates": feasible_count,
            "feasibility_ratio": round(feasible_count / len(scored), 4),
        },
    }


_PROCESSORS = {
    "marine_signal_analysis": _analyze_marine_signal,
    "workload_readiness_analysis": _analyze_workload_readiness,
    "domain_optimization_scoring": _score_domain_optimization,
}


def execute_intelligence_task(req: IntelligenceProcessRequest) -> IntelligenceProcessResult:
    """In-process deterministic intelligence execution entrypoint."""
    start = time.perf_counter()
    digest = compute_execution_digest(req.model_dump())

    processor = _PROCESSORS.get(req.task_type)
    if processor is None:
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        return IntelligenceProcessResult(
            status="UNSUPPORTED",
            task_type=req.task_type,
            domain=req.domain,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.UNAVAILABLE.value,
            execution_digest=digest,
            processing_time_ms=duration_ms,
            error=f"Unsupported intelligence task_type '{req.task_type}'. Supported: {sorted(_PROCESSORS.keys())}",
        )

    try:
        output = processor(req.payload)
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        return IntelligenceProcessResult(
            status="COMPLETED",
            task_type=req.task_type,
            domain=req.domain,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
            analysis=output["analysis"],
            metrics=output["metrics"],
            execution_digest=digest,
            processing_time_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 3)
        return IntelligenceProcessResult(
            status="FAILED",
            task_type=req.task_type,
            domain=req.domain,
            correlation_id=req.correlation_id,
            trace_id=req.trace_id,
            invocation_id=req.invocation_id,
            execution_classification=ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
            execution_digest=digest,
            processing_time_ms=duration_ms,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# FastAPI Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "InsightCore", "role": "intelligence_processing", "version": "1.0.0"}


@app.get("/ready")
async def ready():
    return {"status": "ready", "supported_tasks": sorted(_PROCESSORS.keys())}


@app.post("/api/v1/process", response_model=IntelligenceProcessResult)
async def process_intelligence(
    req: IntelligenceProcessRequest,
    claims: Dict[str, Any] = Depends(verify_bearer_or_jwt),
):
    result = execute_intelligence_task(req)
    if result.status == "UNSUPPORTED":
        raise HTTPException(status_code=422, detail=result.model_dump())
    if result.status == "FAILED":
        raise HTTPException(status_code=400, detail=result.model_dump())
    return result


# Auxiliary backward-compatible JWT Issuer endpoint (Preserved from VM :8030)
@app.post("/auth/issue")
async def issue_token(request: AuthIssueRequest):
    valid_secret = os.getenv("CORE_CLIENT_SECRET", "").strip()
    if not valid_secret:
        raise HTTPException(status_code=500, detail="CORE_CLIENT_SECRET is not configured; failing closed.")
    if not hmac.compare_digest(request.client_secret, valid_secret):
        raise HTTPException(status_code=401, detail="Invalid client secret")
    token = issue_hs256_jwt(client_id=request.client_id)
    return {"access_token": token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("INSIGHT_CORE_PORT", "8030"))
    uvicorn.run(app, host="0.0.0.0", port=port)
