"""
InsightFlow Constitutional Runtime Participant.
"""

from src.common.base_participant import BaseParticipant
from src.common.models import RuntimeParticipant
from src.common.constants import (
    PARTICIPANTS,
    RUNTIME_IDENTITIES,
    PROJECT_VERSION,
    CONSTITUTIONAL_LAYER,
    RUNTIME_TYPE,
)

from .lifecycle import InsightFlowLifecycle


class InsightFlowParticipant(BaseParticipant):

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTFLOW"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTFLOW"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=[
                "workflow_orchestration",
                "capability_invocation",
                "trace_generation",
                "evidence_generation",
            ],
            dependencies=[
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "PlatformRegistry",
                "RuntimeCore",
            ],
        )

        super().__init__(participant)

        self.lifecycle = InsightFlowLifecycle()

    def register(self):
        """
        Registration is delegated to the Platform Registry Adapter.
        """
        raise NotImplementedError(
            "Registration must be performed using PlatformRegistryAdapter."
        )

    def publish_capability(self):
        """
        Capability publication is delegated to Platform SDK.
        """
        raise NotImplementedError(
            "Capability publication must be performed using PlatformSDKAdapter."
        )

    def execute(self, payload):
        """
        Executes InsightFlow business logic.
        """
        return {
            "participant": self.participant.participant_name,
            "status": "accepted",
            "payload": payload,
        }

    def health(self):
        return {
            "participant": self.participant.participant_name,
            "state": self.lifecycle.state.value,
        }