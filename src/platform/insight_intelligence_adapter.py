"""
Insight Intelligence Adapter — Client for Insight Intelligence Engine (:8030).

Supports:
  - GET /health
  - POST /api/v1/process (Intelligence processing)
  - POST /auth/issue (Auxiliary Sovereign JWT issuance)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("insight.platform.insight_intelligence_adapter")


class InsightIntelligenceAdapter:
    """HTTP adapter for the Insight Intelligence Engine (:8030)."""

    def __init__(self, base_url: Optional[str] = None, bearer_token: Optional[str] = None):
        self._explicit_base_url = base_url.rstrip("/") if base_url else None
        self.bearer_token = bearer_token or os.getenv("INSIGHT_EXECUTION_TOKEN") or os.getenv("INSIGHT_AUTH_TOKEN")

    @property
    def base_url(self) -> str:
        if self._explicit_base_url:
            return self._explicit_base_url
        url = (
            os.getenv("INSIGHT_INTELLIGENCE_BASE_URL")
            or os.getenv("INSIGHT_CORE_BASE_URL")
            or "http://163.128.209.18:8030"
        )
        return url.rstrip("/")

    def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return {"status": "HEALTHY", "http_status": resp.status_code, "data": resp.json()}
        except requests.exceptions.RequestException as exc:
            logger.error("Insight Intelligence Engine health check failed: %s", exc)
            return {"status": "UNAVAILABLE", "error": str(exc)}

    def issue_token(self, client_id: str, client_secret: str) -> Optional[str]:
        url = f"{self.base_url}/auth/issue"
        try:
            resp = requests.post(
                url,
                json={"client_id": client_id, "client_secret": client_secret},
                timeout=10,
            )
            resp.raise_for_status()
            token = resp.json().get("access_token")
            if token:
                self.bearer_token = token
            return token
        except requests.exceptions.RequestException as exc:
            logger.error("Insight Intelligence Engine token issuance failed: %s", exc)
            return None

    def process(self, process_request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/process"
        auth_token = (
            token
            or os.getenv("INSIGHT_EXECUTION_TOKEN")
            or os.getenv("INSIGHT_AUTH_TOKEN")
            or self.bearer_token
        )
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        try:
            resp = requests.post(url, json=process_request, headers=headers, timeout=15)
            if resp.status_code >= 400:
                return {
                    "status": "FAILED",
                    "http_status": resp.status_code,
                    "error": resp.text,
                    "service_url": url,
                }
            data = resp.json()
            return {"status": "SUCCESS", "http_status": resp.status_code, "data": data, "service_url": url}
        except requests.exceptions.RequestException as exc:
            return {"status": "UNAVAILABLE", "error": str(exc), "service_url": url}


# Backward-compatible class alias
InsightCoreAdapter = InsightIntelligenceAdapter

__all__ = ["InsightIntelligenceAdapter", "InsightCoreAdapter"]
