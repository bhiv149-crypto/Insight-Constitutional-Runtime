"""
Base abstractions for Constitutional Runtime Participants.
"""

from abc import ABC, abstractmethod
from .models import RuntimeParticipant


class BaseParticipant(ABC):
    """
    Base class for all Insight Runtime Participants.

    Platform concerns such as registration,
    capability publication and discovery are delegated
    to Platform adapters.
    """

    def __init__(self, participant: RuntimeParticipant):
        self.participant = participant

    @property
    def identity(self):
        return self.participant.runtime_identity

    @property
    def name(self):
        return self.participant.participant_name

    @property
    def version(self):
        return self.participant.version

    @abstractmethod
    def execute(self, payload):
        """Execute participant-specific workload."""

    @abstractmethod
    def health(self):
        """Return participant runtime health."""