"""
Development stubs for Platform Runtime components.

These stubs exist only to allow the Insight Runtime repository
to be imported and tested before the official Platform Runtime
packages are available.

Replace these with the official Platform Runtime implementation
during integration.
"""


class PlatformCapabilitySDK:
    """Development stub for PlatformCapabilitySDK."""

    def __init__(self, *args, **kwargs):
        pass

    def _unavailable(self, method):
        raise NotImplementedError(
            f"{method} requires the official PlatformCapabilitySDK."
        )

    def discover_services(self, *args, **kwargs):
        self._unavailable("discover_services")

    def get_service(self, *args, **kwargs):
        self._unavailable("get_service")

    def negotiate_version(self, *args, **kwargs):
        self._unavailable("negotiate_version")

    def validate_manifest(self, *args, **kwargs):
        self._unavailable("validate_manifest")

    def check_health(self, *args, **kwargs):
        self._unavailable("check_health")

    def invoke_capability(self, *args, **kwargs):
        self._unavailable("invoke_capability")

    def get_federation_status(self, *args, **kwargs):
        self._unavailable("get_federation_status")


class PlatformServiceRegistry:
    """Development stub for PlatformServiceRegistry."""

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        raise NotImplementedError(
            f"PlatformServiceRegistry.{name}() requires the official Platform Runtime."
        )


class PlatformServiceRecord:
    """
    Lightweight development representation of a PlatformServiceRecord.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class ReplayRegistry:
    """
    Development stub for ReplayRegistry.

    Provides in-memory message deduplication matching the
    contract of the canonical Platform Replay Registry.
    """

    def __init__(self, *args, **kwargs):
        self._seen: dict = {}
        self._sequence: int = 0

    def check(self, message_id: str) -> bool:
        """Return True if the message_id has already been seen."""
        return message_id in self._seen

    def record(self, message_id: str, issued_at=None, trace_reference=None) -> int:
        """Record a message_id and return the assigned sequence number."""
        self._sequence += 1
        self._seen[message_id] = {
            "sequence": self._sequence,
            "issued_at": issued_at,
            "trace_reference": trace_reference,
        }
        return self._sequence


class ReplayVerdict:
    """
    Development replay verdict.
    """

    def __init__(self, is_valid=True, sequence_number=1, status="VALID", reason=""):
        self.is_valid = is_valid
        self.sequence_number = sequence_number
        self.status = status
        self.reason = reason


class CanonicalReplayAuthority:
    """
    Development stub for CanonicalReplayAuthority.

    Performs real in-memory deduplication:
    - First submit() with a given message_id → VALID
    - Second submit() with the same message_id → DUPLICATE
    """

    def __init__(self, registry=None):
        self.registry = registry or ReplayRegistry()

    def submit(self, message_id=None, issued_at=None, trace_reference=None, **kwargs):
        if message_id is None:
            message_id = kwargs.get("message_id")

        if self.registry.check(message_id):
            return ReplayVerdict(
                is_valid=False,
                sequence_number=0,
                status="DUPLICATE",
                reason=f"message_id '{message_id}' has already been processed",
            )

        sequence = self.registry.record(message_id, issued_at, trace_reference)
        return ReplayVerdict(
            is_valid=True,
            sequence_number=sequence,
            status="VALID",
            reason="",
        )

class CapabilityManifest:
    """Development stub."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class OperationContract:
    """Development stub."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class StubTrustProvider:
    """Development trust provider."""

    def verify(self, *args, **kwargs):
        return True

    def sign(self, *args, **kwargs):
        return "stub-signature"

class TraceStore:
    """
    Development stub for Platform TraceStore.
    """

    def record_execution_trace(self, **kwargs):
        return {
            "status": "RECORDED",
            "type": "execution_trace",
            **kwargs,
        }

    def record_contract_lineage(self, **kwargs):
        return {
            "status": "RECORDED",
            "type": "contract_lineage",
            **kwargs,
        }

    def record_adapter_trace(self, **kwargs):
        return {
            "status": "RECORDED",
            "type": "adapter_trace",
            **kwargs,
        }

    def reconstruct_replay(self, trace_id):
        return {
            "trace_id": trace_id,
            "status": "AVAILABLE",
        }

    def export_opentelemetry(self, trace_id):
        return {
            "trace_id": trace_id,
            "exported": True,
            "provider": "OpenTelemetry",
        }

class StubTrustProvider:
    """Development trust provider."""

    def verify(self, *args, **kwargs):
        return True

    def sign(self, *args, **kwargs):
        return "stub-signature"


def create_trust_provider(provider_type="CLASSICAL"):
    """
    Development stub for create_trust_provider().
    """
    return StubTrustProvider()