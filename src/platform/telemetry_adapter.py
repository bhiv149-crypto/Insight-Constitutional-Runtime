"""
Platform Telemetry Adapter

Thin compatibility adapter around the Platform Runtime observability
implementation.

IMPORTANT BOUNDARY
------------------
Insight Runtime does NOT own telemetry storage or observability.

This adapter only delegates telemetry operations to the Platform
Runtime TraceStore/provider available through `src.platform.imports`.

The adapter supports:
    1. Current/local TraceStore implementation
    2. Future live Platform telemetry implementation
    3. Existing legacy TraceStore method signatures

It does NOT:
    - implement a telemetry database
    - create a second telemetry registry
    - implement replay
    - modify QCG
    - modify SDK invocation
    - claim that local telemetry is production/live telemetry
"""

from __future__ import annotations

import hashlib
import inspect
from typing import Any, Dict, Optional

from src.platform.imports import TraceStore
from src.platform.insightbridge_adapter import InsightBridgeAdapter


class PlatformTelemetryAdapter:
    """
    Boundary adapter for Platform Runtime telemetry.

    Ownership:
        Platform Runtime / TraceStore

    Consumer:
        Insight Constitutional Runtime

    The adapter delegates telemetry work and normalizes the result
    into a predictable dictionary representation.
    """

    def __init__(self, trace_store: Optional[Any] = None):
        # Dependency injection is intentionally supported so that:
        #
        #   - tests can provide a fake TraceStore
        #   - local development can use the existing TraceStore
        #   - production can provide a live Platform telemetry provider
        #
        # No telemetry state is owned here.
        self.trace_store = trace_store or TraceStore()
        self.insightbridge_client = InsightBridgeAdapter()


    # =========================================================
    # Internal Helpers
    # =========================================================

    @staticmethod
    def _hash(value: Any) -> str:
        """
        Generate a deterministic SHA-256 representation.

        Used only when the underlying Platform TraceStore requires
        hashes rather than the higher-level Insight representation.
        """
        return hashlib.sha256(
            str(value).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _method_parameters(method: Any) -> set[str]:
        """
        Return supported parameter names for a TraceStore method.

        Introspection keeps this adapter compatible with different
        Platform TraceStore versions.
        """
        try:
            return set(inspect.signature(method).parameters.keys())
        except (TypeError, ValueError):
            return set()

    @staticmethod
    def _sequence(result: Any) -> int:
        """
        Extract sequence number when supplied by the Platform runtime.
        """
        return getattr(result, "sequence", 0)

    @staticmethod
    def _safe_dict(result: Any) -> Any:
        """
        Preserve dictionaries as-is while leaving other provider
        response objects untouched.
        """
        return result

    # =========================================================
    # Execution Trace
    # =========================================================

    def record_execution_trace(
        self,
        trace_id: str,
        participant: str,
        operation: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record an execution trace through the Platform TraceStore.

        This method does not create local telemetry state.
        """

        if not trace_id:
            raise ValueError("trace_id is required")

        method = self.trace_store.record_execution_trace
        params = self._method_parameters(method)

        metadata = metadata or {}

        # -----------------------------------------------------
        # Current Platform TraceStore contract
        # -----------------------------------------------------

        # Call live InsightBridge adapter to ingest telemetry
        ib_result = None
        try:
            telemetry_data = {
                "request_id": trace_id,
                "path": "/api/v1/execute",
                "method": "POST",
                "status_code": metadata.get("status_code", 200),
                "latency_ms": float(metadata.get("duration_ms") or metadata.get("latency_ms") or 10.0),
            }
            ib_metadata = {
                "user_id": metadata.get("user_id") or metadata.get("source") or "insight-runtime",
                "app_version": metadata.get("app_version") or "1.0.2",
                "env": metadata.get("env") or "production",
            }
            telemetry_request = {
                "telemetry_data": telemetry_data,
                "metadata": ib_metadata,
            }
            ib_result = self.insightbridge_client.ingest_telemetry(telemetry_request)
        except Exception as exc:
            logger.error("Failed to execute live InsightBridge telemetry ingestion: %s", exc)
            ib_result = {"status": "FAILED", "error": str(exc)}

        if "contract_hash" in params:

            contract_hash = self._hash(operation)
            runtime_hash = self._hash(participant)

            result = method(
                trace_id=trace_id,
                contract_hash=contract_hash,
                ack="ACK",
                runtime_hash=runtime_hash,
                confidence=1.0,
            )

            return {
                "status": "RECORDED",
                "trace_id": trace_id,
                "type": "execution",
                "participant": participant,
                "operation": operation,
                "sequence": self._sequence(result),
                "provider": type(self.trace_store).__name__,
                "insightbridge_telemetry": ib_result,
            }

        # -----------------------------------------------------
        # Legacy / alternate Platform contract
        # -----------------------------------------------------

        legacy_res = self._safe_dict(
            method(
                trace_id=trace_id,
                participant=participant,
                operation=operation,
                metadata=metadata,
            )
        )
        if isinstance(legacy_res, dict):
            legacy_res["insightbridge_telemetry"] = ib_result
        return legacy_res

    # =========================================================
    # Contract Lineage
    # =========================================================

    def record_contract_lineage(
        self,
        contract_id: str,
        parent_contract: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record constitutional contract lineage through Platform.

        Insight does not own the lineage store.
        """

        if not contract_id:
            raise ValueError("contract_id is required")

        method = self.trace_store.record_contract_lineage
        params = self._method_parameters(method)

        metadata = metadata or {}

        # -----------------------------------------------------
        # Current Platform TraceStore contract
        # -----------------------------------------------------

        if "contract_version" in params:

            result = method(
                trace_id=contract_id,
                contract_version="1.0.0",
                producer_type="INSIGHT",
                governance_decisions=["APPROVED"],
                final_ack="ACK",
            )

            return {
                "status": "RECORDED",
                "contract_id": contract_id,
                "type": "contract_lineage",
                "parent_contract": parent_contract,
                "sequence": self._sequence(result),
                "provider": type(self.trace_store).__name__,
            }

        # -----------------------------------------------------
        # Legacy / alternate Platform contract
        # -----------------------------------------------------

        return self._safe_dict(
            method(
                contract_id=contract_id,
                parent_contract=parent_contract,
                metadata=metadata,
            )
        )

    # =========================================================
    # Adapter Trace
    # =========================================================

    def record_adapter_trace(
        self,
        adapter: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record an adapter execution through Platform telemetry.

        `trace_id` is optional for backward compatibility.

        If the underlying TraceStore requires a trace_id, the supplied
        trace_id is used. Otherwise a deterministic fallback is created
        from the adapter/action context.

        No fixed global trace ID is used.
        """

        if not adapter:
            raise ValueError("adapter is required")

        if not action:
            raise ValueError("action is required")

        method = self.trace_store.record_adapter_trace
        params = self._method_parameters(method)

        metadata = metadata or {}

        # -----------------------------------------------------
        # Current Platform TraceStore contract
        # -----------------------------------------------------

        if "adapter_type" in params:

            effective_trace_id = (
                trace_id
                or f"adapter-{self._hash(f'{adapter}:{action}')[:16]}"
            )

            input_hash = self._hash(metadata)
            output_hash = self._hash(action)

            result = method(
                trace_id=effective_trace_id,
                adapter_type=adapter,
                producer_type="INSIGHT",
                input_hash=input_hash,
                output_hash=output_hash,
            )

            return {
                "status": "RECORDED",
                "trace_id": effective_trace_id,
                "adapter": adapter,
                "action": action,
                "type": "adapter_trace",
                "sequence": self._sequence(result),
                "provider": type(self.trace_store).__name__,
            }

        # -----------------------------------------------------
        # Legacy / alternate Platform contract
        # -----------------------------------------------------

        return self._safe_dict(
            method(
                adapter=adapter,
                action=action,
                metadata=metadata,
            )
        )

    # =========================================================
    # Replay Reconstruction
    # =========================================================

    def reconstruct_replay(self, trace_id: str):
        """
        Delegate replay reconstruction to Platform telemetry.

        IMPORTANT:
            This is NOT the canonical QCG replay verification path.

        Canonical replay verification is handled by:
            SDK invocation
                ↓
            invocation_id
                ↓
            POST /qcg/verify
                ↓
            QCG Replay Authority
                ↓
            GET /qcg/replay/lineage/{invocation_id}

        This method only exposes whatever reconstruction facility
        the Platform TraceStore provides.
        """

        if not trace_id:
            raise ValueError("trace_id is required")

        return self.trace_store.reconstruct_replay(trace_id)

    # =========================================================
    # OpenTelemetry Export
    # =========================================================

    def export_opentelemetry(self, trace_id: str):
        """
        Delegate OpenTelemetry export to Platform Runtime.

        Insight does not directly export telemetry.
        """

        if not trace_id:
            raise ValueError("trace_id is required")

        return self.trace_store.export_opentelemetry(trace_id)

    # =========================================================
    # Provider Information
    # =========================================================

    def provider_info(self) -> Dict[str, Any]:
        """
        Return non-invasive information about the currently attached
        telemetry provider.

        This is useful for evidence because it makes it explicit
        whether the adapter is currently backed by the local/provider
        TraceStore implementation.
        """

        provider = type(self.trace_store).__name__

        module = type(self.trace_store).__module__

        return {
            "adapter": type(self).__name__,
            "provider": provider,
            "provider_module": module,
            "ownership": "PLATFORM_RUNTIME",
            "local_state_owned_by_adapter": False,
        }