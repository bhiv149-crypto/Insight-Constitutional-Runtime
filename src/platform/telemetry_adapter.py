"""
Platform Telemetry Adapter

Thin wrapper around the Platform Runtime observability services.

Responsibility:
    Expose telemetry functionality without implementing
    Platform Runtime observability.
"""

from src.platform.imports import TraceStore


class PlatformTelemetryAdapter:
    """
    Adapter for Platform Runtime telemetry and observability.
    """

    def __init__(self, trace_store=None):
        self.trace_store = trace_store or TraceStore()

    # ---------------------------------------------------------
    # Execution Traces
    # ---------------------------------------------------------

    def record_execution_trace(
        self,
        trace_id,
        participant,
        operation,
        metadata=None,
    ):
        """
        Record an execution trace.
        """

        return self.trace_store.record_execution_trace(
            trace_id=trace_id,
            participant=participant,
            operation=operation,
            metadata=metadata or {},
        )

    # ---------------------------------------------------------
    # Contract Lineage
    # ---------------------------------------------------------

    def record_contract_lineage(
        self,
        contract_id,
        parent_contract=None,
        metadata=None,
    ):
        """
        Record constitutional contract lineage.
        """

        return self.trace_store.record_contract_lineage(
            contract_id=contract_id,
            parent_contract=parent_contract,
            metadata=metadata or {},
        )

    # ---------------------------------------------------------
    # Adapter Trace
    # ---------------------------------------------------------

    def record_adapter_trace(
        self,
        adapter,
        action,
        metadata=None,
    ):
        """
        Record adapter execution.
        """

        return self.trace_store.record_adapter_trace(
            adapter=adapter,
            action=action,
            metadata=metadata or {},
        )

    # ---------------------------------------------------------
    # Replay Reconstruction
    # ---------------------------------------------------------

    def reconstruct_replay(self, trace_id):
        """
        Reconstruct execution from trace history.
        """

        return self.trace_store.reconstruct_replay(trace_id)

    # ---------------------------------------------------------
    # OpenTelemetry Export
    # ---------------------------------------------------------

    def export_opentelemetry(self, trace_id):
        """
        Export telemetry using the Platform Runtime.
        """

        return self.trace_store.export_opentelemetry(trace_id)