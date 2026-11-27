"""
Verification of Canonical Naming Standards, Contracts, and Service Entrypoints.

Ensures that:
1. Canonical contracts (src.common.insight_contracts) can be imported and instantiated.
2. Canonical services (workflow, gateway, intelligence) can be imported.
3. Canonical platform adapters can be instantiated.
4. Environment variable precedence and deprecation warning for INSIGHT_SERVICES_HTTP vs INSIGHT_OPTION_B_HTTP.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.insight_contracts import (
    ExecutionClassification,
    GatewayRouteRequest,
    GatewayRouteResponse,
    IntelligenceProcessRequest,
    IntelligenceProcessResult,
    RouteTarget,
    WorkflowExecutionResponse,
    WorkflowState,
    WorkflowStepRecord,
    WorkflowSubmitRequest,
)
from src.config.platform_config import is_http_services_mode
from src.platform.insight_gateway_adapter import InsightGatewayAdapter
from src.platform.insight_intelligence_adapter import InsightIntelligenceAdapter
from src.platform.insight_workflow_adapter import InsightWorkflowAdapter
from src.services.insight_gateway_service import app as gateway_app
from src.services.insight_intelligence_service import app as intelligence_app
from src.services.insight_workflow_service import app as workflow_app


def test_canonical_contracts_instantiation():
    """Verify that canonical domain contracts instantiate correctly."""
    req = WorkflowSubmitRequest(
        workflow_type=RouteTarget.INTELLIGENCE,
        task_type="marine_signal_analysis",
        payload={"salinity": 35.0, "temperature_celsius": 18.5, "pH": 8.1, "material_oxidation_potential": -0.45},
    )
    assert req.workflow_type == RouteTarget.INTELLIGENCE
    assert req.correlation_id.startswith("corr-")

    gw_req = GatewayRouteRequest(
        route_target=RouteTarget.QUANTUM,
        capability_id="quantum_pipeline",
        payload={"n_qubits": 4},
    )
    assert gw_req.route_target == RouteTarget.QUANTUM

    intel_req = IntelligenceProcessRequest(
        task_type="marine_signal_analysis",
        payload={"salinity": 35.0, "temperature_celsius": 18.5, "pH": 8.1, "material_oxidation_potential": -0.45},
    )
    assert intel_req.task_type == "marine_signal_analysis"


def test_canonical_services_instantiation():
    """Verify that canonical FastAPI service apps exist and have expected titles."""
    assert "Workflow" in workflow_app.title
    assert "Gateway" in gateway_app.title or "Routing" in gateway_app.title
    assert "Intelligence" in intelligence_app.title


def test_canonical_adapters_instantiation():
    """Verify that canonical platform adapters instantiate correctly."""
    w_adapter = InsightWorkflowAdapter(base_url="http://127.0.0.1:8031")
    g_adapter = InsightGatewayAdapter(base_url="http://127.0.0.1:8029")
    i_adapter = InsightIntelligenceAdapter(base_url="http://127.0.0.1:8030")

    assert w_adapter.base_url == "http://127.0.0.1:8031"
    assert g_adapter.base_url == "http://127.0.0.1:8029"
    assert i_adapter.base_url == "http://127.0.0.1:8030"


def test_http_services_mode_precedence_and_deprecation(monkeypatch, caplog):
    """Verify INSIGHT_SERVICES_HTTP precedence, conflict detection, and legacy deprecation."""
    monkeypatch.delenv("INSIGHT_SERVICES_HTTP", raising=False)
    monkeypatch.delenv("INSIGHT_OPTION_B_HTTP", raising=False)
    assert is_http_services_mode() is False

    # Canonical true
    monkeypatch.setenv("INSIGHT_SERVICES_HTTP", "true")
    assert is_http_services_mode() is True

    # Legacy fallback emits DeprecationWarning
    monkeypatch.delenv("INSIGHT_SERVICES_HTTP", raising=False)
    monkeypatch.setenv("INSIGHT_OPTION_B_HTTP", "1")
    with pytest.deprecated_call():
        assert is_http_services_mode() is True

    # Conflict: canonical overrides legacy and logs warning
    monkeypatch.setenv("INSIGHT_SERVICES_HTTP", "false")
    monkeypatch.setenv("INSIGHT_OPTION_B_HTTP", "1")
    with caplog.at_level(logging.WARNING, logger="insight.config.platform_config"):
        assert is_http_services_mode() is False
    assert any("Conflicting HTTP mode env vars" in rec.message for rec in caplog.records)
