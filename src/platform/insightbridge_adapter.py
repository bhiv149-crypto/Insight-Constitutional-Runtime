import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("insight.platform.insightbridge_adapter")


class InsightBridgeAdapter:
    """
    Adapter for Vijay's live InsightBridge service.
    Exposes telemetry ingestion.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (
            base_url
            or os.getenv(
                "INSIGHT_BRIDGE_BASE_URL",
                "https://insightbridge-phase-4-2-integration-demo.onrender.com",
            )
        ).rstrip("/")

    def health(self) -> Dict[str, Any]:
        """
        Check health of live InsightBridge endpoint.
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
            logger.error("InsightBridge health check failed: %s", exc)
            return {
                "status": "UNAVAILABLE",
                "error": str(exc)
            }


    def ingest_telemetry(self, telemetry_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send telemetry request to live InsightBridge /ingest.
        """
        url = f"{self.base_url}/ingest"
        try:
            logger.info("POST to InsightBridge: %s with payload %s", url, telemetry_request)
            response = requests.post(
                url,
                json=telemetry_request,
                timeout=15,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return {
                "status": "SUCCESS",
                "http_status": response.status_code,
                "response": response.json() if response.content else {},
            }
        except requests.exceptions.RequestException as exc:
            logger.error("InsightBridge telemetry ingestion failed: %s", exc)
            return {
                "status": "FAILED",
                "error": str(exc),
                "http_status": getattr(exc.response, "status_code", None) if hasattr(exc, "response") else None,
            }
