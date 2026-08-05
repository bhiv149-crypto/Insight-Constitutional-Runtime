"""
Platform Discovery Adapter

Thin wrapper around PlatformCapabilitySDK discovery interfaces.

Responsibility:
    Provide discovery services to Insight participants.

Does NOT implement:
    - Discovery protocol
    - Registry queries
    - Networking
"""

from src.platform.sdk_adapter import PlatformSDKAdapter


class PlatformDiscoveryAdapter:

    def __init__(self, sdk_adapter=None):
        self.sdk = sdk_adapter or PlatformSDKAdapter()

    def discover_services(self, filters=None):
        """Discover all available platform services."""
        return self.sdk.discover_services(filters)

    def get_service(self, service_id):
        """Fetch a single platform service."""
        return self.sdk.get_service(service_id)

    def discover_by_category(self, category):
        """Convenience helper."""
        return self.sdk.discover_services(
            {"capability_category": category}
        )

    def discover_active_services(self):
        """Return only ACTIVE services."""
        return self.sdk.discover_services(
            {"status": "ACTIVE"}
        )

    def discover_by_classification(self, classification):
        """Filter by service classification."""
        return self.sdk.discover_services(
            {"service_classification": classification}
        )