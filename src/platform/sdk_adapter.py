"""
Platform Capability SDK Adapter.

Wraps the PlatformCapabilitySDK used by the Constitutional Runtime.
Actual SDK package is provided by the Platform Services team.
"""

from typing import Any, Dict, List


class PlatformSDKAdapter:
    """
    Adapter around the Platform Capability SDK.
    """

    def __init__(self, sdk: Any):
        """
        Args:
            sdk:
                Instance of PlatformCapabilitySDK supplied
                by Platform Services.
        """
        self.sdk = sdk

    def discover_services(self) -> List[Dict]:
        """Discover registered Platform Services."""
        return self.sdk.discover_services()

    def negotiate_version(self, service_id: str, version: str):
        """Negotiate service version."""
        return self.sdk.negotiate_version(service_id, version)

    def validate_manifest(self, service_id: str):
        """Validate remote capability manifest."""
        return self.sdk.validate_manifest(service_id)

    def invoke(
        self,
        service_id: str,
        operation: str,
        payload: Dict,
    ):
        """Invoke a platform capability."""
        return self.sdk.invoke_capability(
            service_id=service_id,
            operation=operation,
            payload=payload,
        )