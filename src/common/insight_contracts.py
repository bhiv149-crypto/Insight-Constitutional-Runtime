"""
Canonical Domain & Integration Contracts for the Insight Ecosystem.

This module defines the standardized Pydantic v2 schemas and enums
for all Insight subsystems:
  - Insight Workflow Orchestrator (IWO)
  - Insight Communication & Routing Gateway (ICRG)
  - Insight Intelligence Engine (IIE)
  - Auxiliary endpoints (/auth/issue, /enforce, /telemetry/ingest)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    """Return deterministic ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Canonical Enums
# ---------------------------------------------------------------------------

class WorkflowState(str, Enum):
    """Lifecycle states for Insight Workflow Orchestrator jobs."""
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNAVAILABLE = "UNAVAILABLE"


class RouteTarget(str, Enum):
    """Target processing domain for routing decisions."""
    INTELLIGENCE = "INTELLIGENCE"
    QUANTUM = "QUANTUM"
    HYBRID = "HYBRID"


class ExecutionClassification(str, Enum):
    """Architectural classification of execution target."""
    CLASSICAL_INTELLIGENCE = "CLASSICAL_INTELLIGENCE"
    QUANTUM_LOCAL = "QUANTUM_LOCAL"
    REMOTE_SIMULATOR = "REMOTE_SIMULATOR"
    REMOTE_QUANTUM_RUNTIME = "REMOTE_QUANTUM_RUNTIME"
    PHYSICAL_QPU = "PHYSICAL_QPU"
    HYBRID = "HYBRID"
    UNAVAILABLE = "UNAVAILABLE"


# ---------------------------------------------------------------------------
# Insight Intelligence Engine (formerly InsightCore) Contracts
# ---------------------------------------------------------------------------

class IntelligenceProcessRequest(BaseModel):
    """Request payload for deterministic intelligence processing."""
    task_type: str = Field(
        ...,
        description="Supported: marine_signal_analysis | workload_readiness_analysis | domain_optimization_scoring",
    )
    domain: str = Field(default="QCG", description="Domain context (e.g. MARINE, VANA, BIOQUANTUM, QCG)")
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:12]}")
    trace_id: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:12]}")
    invocation_id: str = Field(default_factory=lambda: f"inv-{uuid.uuid4().hex[:12]}")


class IntelligenceProcessResult(BaseModel):
    """Deterministic result from the intelligence processing engine."""
    status: str  # COMPLETED | FAILED | UNSUPPORTED | UNAVAILABLE
    task_type: str
    domain: str
    correlation_id: str
    trace_id: str
    invocation_id: str
    execution_classification: str = ExecutionClassification.CLASSICAL_INTELLIGENCE.value
    analysis: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    execution_digest: str
    processing_time_ms: float
    timestamp_utc: str = Field(default_factory=utc_now_iso)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Insight Communication & Routing Gateway (ICRG) Contracts
# ---------------------------------------------------------------------------

class GatewayRouteRequest(BaseModel):
    """Request payload for gateway routing and validation."""
    route_target: RouteTarget = RouteTarget.INTELLIGENCE
    capability_id: str = Field(default="quantum_pipeline")
    task_type: str = Field(default="marine_signal_analysis")
    domain: str = Field(default="QCG")
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:12]}")
    trace_id: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:12]}")
    invocation_id: str = Field(default_factory=lambda: f"inv-{uuid.uuid4().hex[:12]}")
    idempotency_key: Optional[str] = None


class GatewayRouteResponse(BaseModel):
    """Deterministic response from gateway route execution."""
    status: str  # COMPLETED | FAILED | UNAVAILABLE | DENIED
    route_target: str
    correlation_id: str
    trace_id: str
    invocation_id: str
    execution_classification: str
    execution_digest: str
    provenance_nonce: str
    downstream_service: str
    result: Dict[str, Any] = Field(default_factory=dict)
    attempts: int = 1
    duration_ms: float
    idempotent_replay: bool = False
    timestamp_utc: str = Field(default_factory=utc_now_iso)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Insight Workflow Orchestrator (formerly InsightFlow) Contracts
# ---------------------------------------------------------------------------

class WorkflowSubmitRequest(BaseModel):
    """Request payload for orchestrating a multi-step or single-step workflow."""
    workflow_type: RouteTarget = RouteTarget.INTELLIGENCE
    capability_id: str = Field(default="quantum_pipeline")
    task_type: str = Field(default="marine_signal_analysis")
    domain: str = Field(default="QCG")
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: f"corr-{uuid.uuid4().hex[:12]}")
    trace_id: str = Field(default_factory=lambda: f"trace-{uuid.uuid4().hex[:12]}")
    invocation_id: str = Field(default_factory=lambda: f"inv-{uuid.uuid4().hex[:12]}")
    idempotency_key: Optional[str] = None


class WorkflowStepRecord(BaseModel):
    """Execution record for an individual workflow step."""
    step_name: str
    target_service: str
    status: str
    duration_ms: float
    execution_classification: str
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class WorkflowExecutionResponse(BaseModel):
    """Complete lifecycle response for an orchestrated workflow."""
    workflow_id: str
    workflow_type: str
    state: WorkflowState
    correlation_id: str
    trace_id: str
    invocation_id: str
    steps: List[WorkflowStepRecord] = Field(default_factory=list)
    aggregated_result: Dict[str, Any] = Field(default_factory=dict)
    evidence_recorded: bool = False
    evidence_details: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Backward-Compatible Auxiliary Contracts (Preserved from VM v0.1.0)
# ---------------------------------------------------------------------------

class AuthIssueRequest(BaseModel):
    """Auxiliary credential request for issuing execution tokens."""
    client_id: str
    client_secret: str


class EnforceRequest(BaseModel):
    """Auxiliary resource/action policy verification request."""
    resource: str
    action: str


class TelemetryEvent(BaseModel):
    """Auxiliary telemetry ingestion payload."""
    event_type: str
    decision_id: str
    client_id: str
    decision: str
    reason: Optional[str] = None
    timestamp: str
