"""
Insight Gateway Adapter — Client for Insight Communication & Routing Gateway (:8029).

Supports:
  - GET /health
  - POST /api/v1/route/intelligence
  - POST /api/v1/route/quantum
  - Auxiliary POST /enforce and legacy ingest_telemetry() compatibility
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("insight.platform.insight_gateway_adapter")


class InsightGatewayAdapter:
    """HTTP adapter for the Insight Communication & Routing Gateway (:8029)."""

    def __init__(self, base_url: Optional[str] = None, bearer_token: Optional[str] = None):
        self._explicit_base_url = base_url.rstrip("/") if base_url else None
        self.bearer_token = (
            bearer_token
            or os.getenv("INSIGHT_EXECUTION_TOKEN")
            or os.getenv("INSIGHT_ENFORCE_TOKEN")
        )

    @property
    def base_url(self) -> str:
        if self._explicit_base_url:
            return self._explicit_base_url
        url = (
            os.getenv("INSIGHT_GATEWAY_BASE_URL")
            or os.getenv("INSIGHT_BRIDGE_BASE_URL")
            or "http://163.128.209.18:8029"
        )
        return url.rstrip("/")

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        auth_token = (
            token
            or os.getenv("INSIGHT_EXECUTION_TOKEN")
            or os.getenv("INSIGHT_ENFORCE_TOKEN")
            or self.bearer_token
        )
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {"status": "HEALTHY", "http_status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as exc:
            logger.error("Insight Gateway health check failed: %s", exc)
            return {"status": "UNAVAILABLE", "error": str(exc)}

    def route_intelligence(self, route_request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/route/intelligence"
        try:
            response = requests.post(url, json=route_request, headers=self._headers(token), timeout=15)
            if response.status_code >= 400:
                return {"status": "FAILED", "http_status": response.status_code, "error": response.text, "service_url": url}
            return {"status": "SUCCESS", "http_status": response.status_code, "data": response.json(), "service_url": url}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc), "service_url": url}

    def route_quantum(self, route_request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/route/quantum"
        try:
            response = requests.post(url, json=route_request, headers=self._headers(token), timeout=20)
            if response.status_code >= 400:
                return {"status": "FAILED", "http_status": response.status_code, "error": response.text, "service_url": url}
            return {"status": "SUCCESS", "http_status": response.status_code, "data": response.json(), "service_url": url}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc), "service_url": url}

    def enforce(self, resource: str, action: str, token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/enforce"
        try:
            response = requests.post(
                url,
                json={"resource": resource, "action": action},
                headers=self._headers(token),
                timeout=10,
            )
            if response.status_code >= 400:
                return {"status": "FAILED", "http_status": response.status_code, "error": response.text}
            return {"status": "SUCCESS", "http_status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc)}

    def ingest_telemetry(self, telemetry_request: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy compatibility wrapper routing telemetry to Insight Workflow Orchestrator."""
        flow_url = (
            os.getenv("INSIGHT_WORKFLOW_BASE_URL")
            or os.getenv("INSIGHT_FLOW_BASE_URL")
            or "http://163.128.209.18:8031"
        ).rstrip("/")
        url = f"{flow_url}/telemetry/ingest"
        ingestion_token = os.getenv("INGESTION_TOKEN", "").strip()
        if not ingestion_token:
            return {
                "status": "FAILED",
                "error": "INGESTION_TOKEN is not configured; failing closed.",
                "http_status": None,
            }
        try:
            response = requests.post(
                url,
                json=telemetry_request,
                timeout=15,
                headers={
                    "Content-Type": "application/json",
                    "X-Insight-Token": ingestion_token,
                },
            )
            response.raise_for_status()
            return {
                "status": "SUCCESS",
                "http_status": response.status_code,
                "response": response.json() if response.content else {},
            }
        except requests.exceptions.RequestException as exc:
            return {
                "status": "FAILED",
                "error": str(exc),
                "http_status": getattr(exc.response, "status_code", None) if hasattr(exc, "response") else None,
            }


# Backward-compatible class alias
InsightBridgeAdapter = InsightGatewayAdapter

__all__ = ["InsightGatewayAdapter", "InsightBridgeAdapter"]
