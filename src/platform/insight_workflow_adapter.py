"""
Insight Workflow Adapter — Client for Insight Workflow Orchestrator (:8031).

Supports:
  - GET /health
  - POST /api/v1/workflows/execute (Workflow Orchestration)
  - GET /api/v1/workflows/{workflow_id}
  - Backward-compatible enforce() delegation via Insight Gateway (:8029)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("insight.platform.insight_workflow_adapter")


class InsightWorkflowAdapter:
    """HTTP adapter for the Insight Workflow Orchestrator (:8031)."""

    def __init__(self, base_url: Optional[str] = None, bearer_token: Optional[str] = None):
        self._explicit_base_url = base_url.rstrip("/") if base_url else None
        self.username = os.getenv("INSIGHT_FLOW_USERNAME")
        self.password = os.getenv("INSIGHT_FLOW_PASSWORD")
        self.token = (
            bearer_token
            or os.getenv("INSIGHT_FLOW_BEARER_TOKEN")
            or os.getenv("INSIGHT_EXECUTION_TOKEN")
        )

    @property
    def base_url(self) -> str:
        if self._explicit_base_url:
            return self._explicit_base_url
        url = (
            os.getenv("INSIGHT_WORKFLOW_BASE_URL")
            or os.getenv("INSIGHT_FLOW_BASE_URL")
            or "http://163.128.209.18:8031"
        )
        return url.rstrip("/")

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        auth_token = (
            token
            or os.getenv("INSIGHT_FLOW_BEARER_TOKEN")
            or os.getenv("INSIGHT_EXECUTION_TOKEN")
            or self.token
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
            logger.error("Insight Workflow Orchestrator health check failed: %s", exc)
            return {"status": "UNAVAILABLE", "error": str(exc)}

    def execute_workflow(self, workflow_request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/workflows/execute"
        try:
            response = requests.post(url, json=workflow_request, headers=self._headers(token), timeout=25)
            if response.status_code >= 400:
                return {"status": "FAILED", "http_status": response.status_code, "error": response.text, "service_url": url}
            return {"status": "SUCCESS", "http_status": response.status_code, "data": response.json(), "service_url": url}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc), "service_url": url}

    def get_workflow(self, workflow_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        try:
            response = requests.get(url, headers=self._headers(token), timeout=10)
            if response.status_code >= 400:
                return {"status": "FAILED", "http_status": response.status_code, "error": response.text}
            return {"status": "SUCCESS", "http_status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc)}

    def login(self) -> Optional[str]:
        """Acquire JWT from Insight Intelligence Engine (:8030) if username/password configured."""
        if self.token:
            return self.token
        if not self.username or not self.password:
            return None
        core_url = (
            os.getenv("INSIGHT_INTELLIGENCE_BASE_URL")
            or os.getenv("INSIGHT_CORE_BASE_URL")
            or "http://163.128.209.18:8030"
        ).rstrip("/")
        try:
            resp = requests.post(
                f"{core_url}/auth/issue",
                json={"client_id": self.username, "client_secret": self.password},
                timeout=10,
            )
            resp.raise_for_status()
            token = resp.json().get("access_token")
            if token:
                self.token = token
            return token
        except requests.exceptions.RequestException:
            return None

    def enforce(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate policy enforcement to Insight Gateway (:8029/enforce)."""
        token = self.login()
        if not token:
            return {
                "status": "BLOCKED",
                "reason": "AUTHENTICATION_FAILED",
                "message": "Missing or invalid Bearer token credentials.",
            }
        bridge_url = (
            os.getenv("INSIGHT_GATEWAY_BASE_URL")
            or os.getenv("INSIGHT_BRIDGE_BASE_URL")
            or "http://163.128.209.18:8029"
        ).rstrip("/")
        url = f"{bridge_url}/enforce"
        try:
            response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=15)
            if response.status_code >= 400:
                return {"status": "FAILED", "reason": "EXECUTION_FAILED", "http_status": response.status_code, "details": response.text}
            return {"status": "SUCCESS", "reason": "LIVE_EXECUTION", "http_status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as exc:
            return {"status": "FAILED", "reason": "LIVE_RUNTIME_UNAVAILABLE", "error": str(exc)}


# Backward-compatible class alias
InsightFlowAdapter = InsightWorkflowAdapter

__all__ = ["InsightWorkflowAdapter", "InsightFlowAdapter"]
