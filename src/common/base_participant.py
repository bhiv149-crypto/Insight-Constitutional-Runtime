"""
Base abstractions for Constitutional Runtime Participants.
"""

from abc import ABC, abstractmethod

from .models import RuntimeParticipant
from src.platform.runtime_adapter import PlatformRuntimeAdapter


class BaseParticipant(ABC):
    """
    Base class for all Constitutional Runtime Participants.

    Platform responsibilities such as runtime registration,
    capability discovery, capability invocation, runtime health,
    and registry participation are delegated to the Platform
    Runtime Adapter.

    Participant implementations are responsible only for
    participant-specific intelligence.
    """

    def __init__(
        self,
        participant: RuntimeParticipant,
        runtime_adapter: PlatformRuntimeAdapter | None = None,
    ):
        self.participant = participant
        self.runtime = runtime_adapter or PlatformRuntimeAdapter()

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def identity(self) -> str:
        return self.participant.runtime_identity

    @property
    def name(self) -> str:
        return self.participant.participant_name

    @property
    def version(self)-> str:
        return self.participant.version

    # ------------------------------------------------------------------
    # Runtime Integration
    # ------------------------------------------------------------------

    def register(self, record, manifest=None):
        """
        Register this participant with the Platform Runtime.
        """
        return self.runtime.register_service(record, manifest)

    def discover_services(self, filters=None)  -> dict:
        """
        Discover Platform capabilities.
        """
        return self.runtime.discover_services(filters)

    def invoke_capability(
        self,
        service_id,
        operation,
        payload,
        version="1.0.0",
    ):
        """
        Invoke a Platform capability.
        """
        return self.runtime.invoke_capability(
            service_id=service_id,
            operation=operation,
            payload=payload,
            version=version,
        )

    def get_health(self, service_id):
        """
        Query runtime health.
        """
        return self.runtime.get_health(service_id)

    # ------------------------------------------------------------------
    # Participant Behaviour
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, payload):
        """
        Execute participant-specific workload.
        """

    @abstractmethod
    def health(self):
        """
        Return participant-specific runtime health.
        """