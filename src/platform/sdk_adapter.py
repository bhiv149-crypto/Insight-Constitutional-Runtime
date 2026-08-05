"""
Platform SDK Adapter

Thin adapter over the official PlatformCapabilitySDK.

Purpose:
    Provide a stable interface for Insight participants while delegating
    all runtime functionality to the Platform SDK.

This adapter intentionally contains no runtime logic.
"""

from src.platform.imports import PlatformCapabilitySDK
from src.platform.runtime_config import SDK_CONFIG

class PlatformSDKAdapter:

    def __init__(self, **sdk_kwargs):
        self.sdk = PlatformCapabilitySDK(**SDK_CONFIG)

    def discover_services(self, filters=None):
        return self.sdk.discover_services(filters)

    def get_service(self, service_id):
        return self.sdk.get_service(service_id)

    def negotiate_version(self, service_id, version):
        return self.sdk.negotiate_version(service_id, version)

    def validate_manifest(self, service_id):
        return self.sdk.validate_manifest(service_id)

    def check_health(self, service_id):
        return self.sdk.check_health(service_id)

    def invoke_capability(
        self,
        service_id,
        operation,
        payload,
        version="1.0.0",
    ):
        return self.sdk.invoke_capability(
            service_id=service_id,
            operation=operation,
            payload=payload,
            version=version,
        )

    def federation_status(self):
        return self.sdk.get_federation_status()