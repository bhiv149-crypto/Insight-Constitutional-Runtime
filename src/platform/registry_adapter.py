"""
Platform Registry Adapter

Thin wrapper around the canonical PlatformServiceRegistry.

Purpose:
    Allow Insight participants to interact with the Platform Registry
    without depending directly on registry implementation details.
"""

from src.platform.imports import (
    PlatformServiceRegistry,
    PlatformServiceRecord,
)


class PlatformRegistryAdapter:

    def __init__(self, registry=None):
        self.registry = registry or PlatformServiceRegistry()

    # Registration
    def register_service(self, record, manifest=None):
        return self.registry.register_service(record, manifest)

    def update_service(self, service_id, updates):
        return self.registry.update_service(service_id, updates)

    # Queries
    def get_service(self, service_id):
        return self.registry.get_service(service_id)

    def list_services(self):
        return self.registry.list_services()

    def get_manifest(self, service_id):
        return self.registry.get_manifest(service_id)

    def get_metadata(self, service_id):
        return self.registry.get_metadata(service_id)

    def get_endpoints(self, service_id):
        return self.registry.get_endpoints(service_id)

    # Versioning
    def negotiate_version(self, service_id, requested_version):
        return self.registry.negotiate_version(
            service_id,
            requested_version,
        )

    def get_versions(self, service_id):
        return self.registry.get_versions(service_id)

    # Health
    def get_health(self, service_id):
        return self.registry.get_health(service_id)

    def get_compatibility(self, service_id):
        return self.registry.get_compatibility(service_id)

    # Lifecycle
    def enable_service(self, service_id):
        return self.registry.enable_service(service_id)

    def disable_service(self, service_id):
        return self.registry.disable_service(service_id)

    def deprecate_service(self, service_id, reason=""):
        return self.registry.deprecate_service(service_id, reason)

    def retire_service(self, service_id, reason=""):
        return self.registry.retire_service(service_id, reason)