import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("insight.platform.insightflow_adapter")


class InsightFlowAdapter:
    """
    Adapter for Vijay's live InsightFlow service.
    Exposes enforcement client skeleton.

    Since /enforce contract is incomplete (request body schema is undocumented),
    this adapter acts as a client skeleton and marks /enforce execution as BLOCKED.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.getenv("INSIGHT_FLOW_BASE_URL", "https://insight-flow-f5j4.onrender.com")
        ).rstrip("/")
        self.username = os.getenv("INSIGHT_FLOW_USERNAME")
        self.password = os.getenv("INSIGHT_FLOW_PASSWORD")
        self.token = os.getenv("INSIGHT_FLOW_BEARER_TOKEN")

    def health(self) -> Dict[str, Any]:
        """
        Check health of live InsightFlow endpoint.
        """
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return {
                "status": "HEALTHY",
                "http_status": response.status_code
            }
        except requests.exceptions.RequestException as exc:
            logger.error("InsightFlow health check failed: %s", exc)
            return {
                "status": "UNAVAILABLE",
                "error": str(exc)
            }

    def login(self) -> Optional[str]:
        """
        Authenticate with live InsightFlow service and retrieve bearer token.
        """
        if self.token:
            return self.token

        if not self.username or not self.password:
            logger.warning("InsightFlow login credentials not configured in environment.")
            return None

        url = f"{self.base_url}/login"
        try:
            response = requests.post(
                url,
                params={"username": self.username, "password": self.password},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token") or data.get("token")
            if token:
                self.token = token
                return token
            logger.error("Login succeeded but no token was returned in response.")
            return None
        except requests.exceptions.RequestException as exc:
            logger.error("InsightFlow login failed: %s", exc)
            return None

    def enforce(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke live /enforce.
        This is currently BLOCKED / CONTRACT INCOMPLETE because the request body
        and response schemas are undocumented and unavailable.
        """
        token = self.login()
        if not token and (self.username and self.password):
            return {
                "status": "BLOCKED",
                "reason": "AUTHENTICATION_FAILED",
                "message": "Missing or invalid Bearer token credentials."
            }

        return {
            "status": "BLOCKED",
            "reason": "CONTRACT_INCOMPLETE",
            "message": "Enforce endpoint schema is undocumented/unavailable. Cannot construct request payload.",
            "service_url": f"{self.base_url}/enforce"
        }
