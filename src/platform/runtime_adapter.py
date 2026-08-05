"""
Platform Runtime Adapter

Unified entry point for interacting with the Constitutional
Platform Runtime.

This adapter coordinates Platform SDK, Registry, Discovery,
Replay, Health and Telemetry services without implementing
Platform Runtime logic.
"""

from src.platform.sdk_adapter import PlatformSDKAdapter
from src.platform.registry_adapter import PlatformRegistryAdapter
from src.platform.discovery_adapter import PlatformDiscoveryAdapter
from src.platform.health_adapter import PlatformHealthAdapter
from src.platform.replay_adapter import PlatformReplayAdapter
from src.platform.telemetry_adapter import PlatformTelemetryAdapter


class PlatformRuntimeAdapter:
    """
    Unified Platform Runtime adapter.
    """

    def __init__(self):
        self.sdk = PlatformSDKAdapter()
        self.registry = PlatformRegistryAdapter()
        self.discovery = PlatformDiscoveryAdapter(self.sdk)
        self.health_adapter = PlatformHealthAdapter(
            self.sdk,
            self.registry,
        )
        self.replay_adapter = PlatformReplayAdapter()
        self.telemetry = PlatformTelemetryAdapter()

    # ---------------------------------------------------------
    # Discovery
    # ---------------------------------------------------------

    def discover_services(self, filters=None):
        return self.discovery.discover_services(filters)

    def get_service(self, service_id):
        return self.discovery.get_service(service_id)

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register_service(self, record, manifest=None):
        return self.registry.register_service(
            record,
            manifest,
        )

    # ---------------------------------------------------------
    # Capability Invocation
    # ---------------------------------------------------------

    def invoke_capability(
        self,
        service_id,
        operation,
        payload,
        version="1.0.0",
    ):
        return self.sdk.invoke_capability(
            service_id,
            operation,
            payload,
            version,
        )

    # ---------------------------------------------------------
    # Manifest & Version
    # ---------------------------------------------------------

    def validate_manifest(self, service_id):
        return self.sdk.validate_manifest(service_id)

    def negotiate_version(self, service_id, version):
        return self.sdk.negotiate_version(
            service_id,
            version,
        )

    # ---------------------------------------------------------
    # Replay
    # ---------------------------------------------------------

    def submit_replay(
        self,
        message_id,
        issued_at,
        trace_reference,
    ):
        return self.replay_adapter.submit(
            message_id,
            issued_at,
            trace_reference,
        )

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    def get_health(self, service_id):
        return self.health_adapter.overall_health(service_id)

    def readiness(self, service_id):
        return self.health_adapter.readiness(service_id)

    def metrics(self, service_id):
        return self.health_adapter.metrics(service_id)

    # ---------------------------------------------------------
    # Telemetry
    # ---------------------------------------------------------

    def record_execution_trace(
        self,
        trace_id,
        participant,
        operation,
        metadata=None,
    ):
        return self.telemetry.record_execution_trace(
            trace_id,
            participant,
            operation,
            metadata,
        )

    def record_contract_lineage(
        self,
        contract_id,
        parent_contract=None,
        metadata=None,
    ):
        return self.telemetry.record_contract_lineage(
            contract_id,
            parent_contract,
            metadata,
        )

    def record_adapter_trace(
        self,
        adapter,
        action,
        metadata=None,
    ):
        return self.telemetry.record_adapter_trace(
            adapter,
            action,
            metadata,
        )

    def reconstruct_replay(self, trace_id):
        return self.telemetry.reconstruct_replay(trace_id)

    def export_opentelemetry(self, trace_id):
        return self.telemetry.export_opentelemetry(trace_id)

    # ---------------------------------------------------------
    # Federation
    # ---------------------------------------------------------

    def federation_status(self):
        return self.sdk.federation_status()