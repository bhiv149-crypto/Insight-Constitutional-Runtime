"""
Marine Quantum Runtime Adapter

Thin, reversible adapter over the local Marine Quantum Runtime.

Purpose:
    Provide an isolated gateway for InsightBridge to discover, query, and
    invoke Quantum capabilities via HTTP endpoints.
    Treats the underlying quantum runtime as an external, immutable service.

Hard Boundaries:
    - Does NOT alter PlatformSDKAdapter or LivePlatformClient.
    - Does NOT replace QCG or establish a parallel global registry.
    - Fails closed (with clear error structures) if Marine is unreachable.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import requests


logger = logging.getLogger("insight.platform.quantum_adapter")


class MarineQuantumAdapter:
    """
    Isolated adapter to interface with the external Marine Quantum Runtime
    via HTTP endpoints.
    """

    def __init__(
        self,
        mode: Optional[str] = None,
        runtime_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.mode = (
            mode
            or os.getenv("QUANTUM_RUNTIME_MODE", "local")
        ).upper()

        self.base_url = (
            runtime_url
            or os.getenv(
                "QUANTUM_RUNTIME_URL",
                "http://localhost:8000",
            )
        ).rstrip("/")

        self.api_key = (
            api_key
            or os.getenv(
                "QUANTUM_RUNTIME_API_KEY",
                "dev-insecure-key",
            )
        )

        self.headers = {
            "X-API-Key": self.api_key,
        }

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Query health from the Marine Quantum Runtime API.

        Only LOCAL mode is supported by this adapter. Unsupported modes
        fail closed rather than silently using the local runtime.
        """

        if self.mode != "LOCAL":
            return {
                "status": "UNAVAILABLE",
                "mode": self.mode,
                "runtime_url": self.base_url,
                "error": (
                    f"Unsupported QUANTUM_RUNTIME_MODE: {self.mode}. "
                    "This adapter supports LOCAL mode only."
                ),
            }

        try:
            res = requests.get(
                f"{self.base_url}/health",
                timeout=5,
            )
            res.raise_for_status()

            data = res.json()

            return {
                "status": "HEALTHY",
                "mode": self.mode,
                "runtime_url": self.base_url,
                "heartbeat": {
                    "heartbeat": "ALIVE"
                },
                "api_response": data,
            }
        
        except requests.exceptions.RequestException as exc:
            logger.error(
                "Marine Quantum Runtime health check failed: %s",
                exc,
            )

            return {
                "status": "UNAVAILABLE",
                "mode": self.mode,
                "runtime_url": self.base_url,
                "error": (
                    "Failed to connect to Quantum Runtime API: "
                    f"{exc}"
                ),
            }

        except ValueError as exc:
            logger.error(
                "Marine Quantum Runtime returned invalid JSON: %s",
                exc,
            )

            return {
                "status": "UNAVAILABLE",
                "mode": self.mode,
                "runtime_url": self.base_url,
                "error": (
                    "Quantum Runtime API returned invalid JSON: "
                    f"{exc}"
                ),
            }

    # ------------------------------------------------------------------
    # Capability Discovery
    # ------------------------------------------------------------------

    def list_capabilities(self) -> List[Dict[str, Any]]:
        """
        List all registered quantum and runtime capabilities via API.

        Returns an empty list when the Marine runtime is unavailable or
        returns an invalid capability response.
        """

        if self.mode != "LOCAL":
            logger.error(
                "Cannot list capabilities in unsupported mode: %s",
                self.mode,
            )
            return []

        try:
            res = requests.get(
                f"{self.base_url}/api/v1/capabilities",
                headers=self.headers,
                timeout=10,
            )
            res.raise_for_status()

            data = res.json()

            if not isinstance(data, list):
                logger.error(
                    "Marine capabilities response is not a list"
                )
                return []

            return data

        except requests.exceptions.RequestException as exc:
            logger.error(
                "Marine list_capabilities failed: %s",
                exc,
            )
            return []

        except ValueError as exc:
            logger.error(
                "Marine capabilities response contains invalid JSON: %s",
                exc,
            )
            return []

    def discover_capability(
        self,
        capability_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Discover a specific capability descriptor from Marine.

        The external API may identify capabilities using:
            - capability_id
            - id
            - name

        The adapter accepts all three forms without changing the
        underlying runtime.
        """

        caps = self.list_capabilities()

        if not caps:
            return None

        for cap in caps:
            if not isinstance(cap, dict):
                continue

            if (
                cap.get("capability_id") == capability_id
                or cap.get("id") == capability_id
                or cap.get("name") == capability_id
            ):
                return cap

        return None

    # ------------------------------------------------------------------
    # Capability Invocation
    # ------------------------------------------------------------------

    def invoke_capability(
        self,
        capability_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Invoke a capability on the local Marine Quantum Runtime.

        The adapter supports LOCAL mode only. Unsupported runtime modes
        fail closed without attempting an HTTP request.
        """

        # ---------------------------------------------------------------
        # Hard boundary: LOCAL mode only
        # ---------------------------------------------------------------
        if self.mode != "LOCAL":
            return {
                "status": "UNAVAILABLE",
                "capability_id": capability_id,
                "error": (
                    f"Unsupported QUANTUM_RUNTIME_MODE: {self.mode}. "
                    "This adapter supports LOCAL mode only."
                ),
                "runtime_mode": self.mode,
                "quantum_provider_source": "Marine Quantum Runtime",
                "execution_classification": "UNAVAILABLE / BLOCKED",
            }

        # Marine API expects:
        # {"payload": payload}
        url = f"{self.base_url}/api/v1/capability/{capability_id}"
        request_body = {"payload": payload}

        try:
            res = requests.post(
                url,
                json=request_body,
                headers=self.headers,
                timeout=30,
            )
            res.raise_for_status()
            result = res.json()

            # -----------------------------------------------------------
            # Explicit InsightBridge quantum provenance
            # -----------------------------------------------------------
            if isinstance(result, dict):
                result["runtime_mode"] = "LOCAL"
                result["quantum_provider_source"] = "Marine Quantum Runtime"

                if "execution_classification" not in result:
                    result["execution_classification"] = "QUANTUM_LOCAL"

                # Preserve/enrich nested execution result when present.
                if isinstance(result.get("result"), dict):
                    inner = result["result"]

                    if "execution_classification" not in inner:
                        inner["execution_classification"] = "QUANTUM_LOCAL"

                    if "provider" not in inner:
                        inner["provider"] = "local_simulator"

            return result

        except requests.exceptions.RequestException as exc:
            logger.error(
                "Execution request error for '%s': %s",
                capability_id,
                exc,
            )

            # -----------------------------------------------------------
            # Extract server response for useful validation errors
            # -----------------------------------------------------------
            error_details: Any = str(exc)
            errors: List[Any] = []

            if getattr(exc, "response", None) is not None:
                try:
                    error_details = exc.response.json()
                except Exception:
                    error_details = exc.response.text

                if isinstance(error_details, dict):
                    if isinstance(error_details.get("errors"), list):
                        errors = error_details["errors"]

                    elif isinstance(error_details.get("detail"), list):
                        errors = error_details["detail"]

                    elif isinstance(error_details.get("detail"), dict):
                        errors = [error_details["detail"]]

                    elif isinstance(error_details.get("attachment_check"), dict):
                        errors = [error_details["attachment_check"]]

                    else:
                        errors = [error_details]

                elif error_details:
                    errors = [error_details]

            status = "FAILED"

            if (
                getattr(exc, "response", None) is not None
                and exc.response.status_code == 422
            ):
                status = "VALIDATION_ERROR"

            return {
                "status": status,
                "capability_id": capability_id,
                "error": error_details,
                "errors": errors,
                "runtime_mode": "LOCAL",
                "quantum_provider_source": "Marine Quantum Runtime",
                "execution_classification": "UNAVAILABLE / BLOCKED",
            }