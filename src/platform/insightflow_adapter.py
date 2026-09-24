import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("insight.platform.insightflow_adapter")


class InsightFlowAdapter:
    """
    Adapter for Vijay's live InsightFlow service.
    Exposes enforcement client.

    The /enforce request body schema is currently undocumented in OpenAPI,
    so this adapter forwards the provided payload verbatim.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.getenv("INSIGHT_FLOW_BASE_URL", "http://163.128.209.18:8122")
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
        """
        if not self.username or not self.password:
            return {
                "status": "BLOCKED",
                "reason": "CONFIGURATION_BLOCKED",
                "message": "Missing credentials in environment."
            }

        token = self.login()
        if not token:
            return {
                "status": "BLOCKED",
                "reason": "AUTHENTICATION_FAILED",
                "message": "Missing or invalid Bearer token credentials."
            }

        url = f"{self.base_url}/enforce"
        try:
            headers = {"Authorization": f"Bearer {token}"}
            # Forward the provided payload verbatim
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    # FastAPI schema validation errors return a "detail" array
                    if "detail" in error_data and isinstance(error_data["detail"], list):
                        return {
                            "status": "BLOCKED",
                            "reason": "CONTRACT_BLOCKED",
                            "message": "Payload schema rejected by server (Validation Error).",
                            "details": error_data,
                            "service_url": url
                        }
                except ValueError:
                    pass
                
                return {
                    "status": "FAILED",
                    "reason": "EXECUTION_FAILED",
                    "http_status": 422,
                    "message": "Server returned 422 but not explicitly a schema error.",
                    "details": response.text,
                    "service_url": url
                }

            response.raise_for_status()

            return {
                "status": "SUCCESS",
                "reason": "LIVE_EXECUTION",
                "http_status": response.status_code,
                "data": response.json() if response.content else {},
                "service_url": url
            }
        except requests.exceptions.HTTPError as exc:
            return {
                "status": "FAILED",
                "reason": "EXECUTION_FAILED",
                "error": str(exc),
                "http_status": exc.response.status_code if exc.response else None,
                "service_url": url
            }
        except requests.exceptions.RequestException as exc:
            return {
                "status": "FAILED",
                "reason": "LIVE_RUNTIME_UNAVAILABLE",
                "error": str(exc),
                "service_url": url
            }
