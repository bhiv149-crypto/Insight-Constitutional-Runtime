"""
Platform Registry Adapter.

Abstraction over Platform Service Registry.

The implementation intentionally delegates all registration
to the Platform Registry rather than implementing it locally.
"""

from typing import Any


class PlatformRegistryAdapter:

    def __init__(self, registry: Any):
        self.registry = registry

    def register(self, record, manifest):
        return self.registry.register_service(
            record,
            manifest,
        )

    def heartbeat(self, service_id: str):
        return self.registry.heartbeat(service_id)

    def revoke(self, service_id: str, reason: str):
        return self.registry.revoke(service_id, reason)