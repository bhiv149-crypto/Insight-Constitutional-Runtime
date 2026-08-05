"""
Platform Health Adapter

Thin wrapper around Platform Runtime health services.

Responsibility:
    Expose health-related functionality without implementing
    Platform Runtime health logic.
"""

from src.platform.sdk_adapter import PlatformSDKAdapter
from src.platform.registry_adapter import PlatformRegistryAdapter


class PlatformHealthAdapter:
    """
    Adapter for Platform Runtime health services.
    """

    def __init__(self, sdk=None, registry=None):
        self.sdk = sdk or PlatformSDKAdapter()
        self.registry = registry or PlatformRegistryAdapter()

    # ---------------------------------------------------------
    # Platform SDK Health
    # ---------------------------------------------------------

    def check_health(self, service_id):
        """
        Query Platform SDK for runtime health.
        """
        return self.sdk.check_health(service_id)

    # ---------------------------------------------------------
    # Registry Health
    # ---------------------------------------------------------

    def registry_health(self, service_id):
        """
        Query Platform Registry health information.
        """
        return self.registry.get_health(service_id)

    # ---------------------------------------------------------
    # Combined Health
    # ---------------------------------------------------------

    def overall_health(self, service_id):
        """
        Aggregate SDK and Registry health.
        """
        return {
            "sdk": self.check_health(service_id),
            "registry": self.registry_health(service_id),
        }

    # ---------------------------------------------------------
    # Runtime Readiness
    # ---------------------------------------------------------

    def readiness(self, service_id):
        """
        Runtime readiness summary.
        """

        return {
            "status": "READY",
            "health": self.overall_health(service_id),
        }

    # ---------------------------------------------------------
    # Runtime Metrics
    # ---------------------------------------------------------

    def metrics(self, service_id):
        """
        Placeholder for Platform metrics.

        Metrics are provided by the Platform Runtime.
        """

        return {
            "service_id": service_id,
            "metrics_available": True,
            "provider": "Platform Runtime",
        }