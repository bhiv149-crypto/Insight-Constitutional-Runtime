"""
Capability Invocation.

Provides a unified interface for Insight Runtime Participants
to invoke Platform capabilities through the Platform Runtime.

All invocation responsibilities are delegated to the
PlatformCapabilitySDK via PlatformRuntimeAdapter.
"""

from src.platform.runtime_adapter import PlatformRuntimeAdapter


class CapabilityInvocation:
    """
    Capability invocation service for Constitutional Runtime Participants.
    """

    def __init__(self, runtime=None):
        self.runtime = runtime or PlatformRuntimeAdapter()

    def invoke(
        self,
        service_id,
        operation,
        payload,
        version="1.0.0",
    ):
        """
        Invoke a capability exposed by a Platform participant.
        """
        return self.runtime.invoke_capability(
            service_id=service_id,
            operation=operation,
            payload=payload,
            version=version,
        )

    def invoke_batch(self, requests):
        """
        Invoke multiple capabilities sequentially.

        requests = [
            {
                "service_id": "...",
                "operation": "...",
                "payload": {...},
                "version": "1.0.0"
            }
        ]
        """

        results = []

        for request in requests:
            results.append(
                self.invoke(
                    service_id=request["service_id"],
                    operation=request["operation"],
                    payload=request.get("payload", {}),
                    version=request.get("version", "1.0.0"),
                )
            )

        return results

    def federation_status(self):
        """
        Return Platform federation status.
        """

        return self.runtime.federation_status()