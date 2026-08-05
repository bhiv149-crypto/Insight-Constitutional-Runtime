"""
Capability Discovery.

Provides capability discovery for Insight Runtime Participants.
"""

from src.platform.runtime_adapter import PlatformRuntimeAdapter


class CapabilityDiscovery:

    def __init__(self, runtime=None):
        self.runtime = runtime or PlatformRuntimeAdapter()

    def discover_all(self):
        return self.runtime.discover_services()

    def discover(self, filters=None):
        return self.runtime.discover_services(filters)

    def get_service(self, service_id):
        return self.runtime.get_service(
            service_id
        )

    def discover_active(self):
        return self.runtime.discover_services(
            {"status": "ACTIVE"}
        )

    def discover_category(self, category):
        return self.runtime.discover_services(
            {
                "capability_category": category,
            }
        )

    def negotiate_version(
        self,
        service_id,
        version,
    ):
        return self.runtime.negotiate_version(
            service_id,
            version,
        )