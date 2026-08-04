"""
Platform Discovery Adapter.

Defines discovery operations required by Insight participants.
"""

from typing import Protocol


class DiscoveryClient(Protocol):
    def discover_services(self):
        ...

    def fetch_metadata(self, service_id: str):
        ...

    def fetch_contracts(self, service_id: str):
        ...

    def fetch_health(self, service_id: str):
        ...


class PlatformDiscoveryAdapter:

    def __init__(self, client: DiscoveryClient):
        self.client = client

    def services(self):
        return self.client.discover_services()

    def metadata(self, service_id: str):
        return self.client.fetch_metadata(service_id)

    def contracts(self, service_id: str):
        return self.client.fetch_contracts(service_id)

    def health(self, service_id: str):
        return self.client.fetch_health(service_id)