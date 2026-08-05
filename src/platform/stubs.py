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
    """

    def __init__(self, *args, **kwargs):
        pass


class ReplayVerdict:
    """
    Development replay verdict.
    """

    def __init__(self):
        self.is_valid = True
        self.sequence_number = 1
        self.status = "VALID"
        self.reason = ""


class CanonicalReplayAuthority:
    """
    Development stub for CanonicalReplayAuthority.
    """

    def __init__(self, registry=None):
        self.registry = registry

    def submit(self, *args, **kwargs):
        return ReplayVerdict()

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