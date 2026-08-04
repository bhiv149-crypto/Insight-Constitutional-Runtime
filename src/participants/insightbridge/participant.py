"""
InsightBridge Constitutional Runtime Participant.
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

from .lifecycle import InsightBridgeLifecycle


class InsightBridgeParticipant(BaseParticipant):

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTBRIDGE"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTBRIDGE"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=[
                "runtime_bridge",
                "trace_propagation",
                "event_forwarding",
            ],
            dependencies=[
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "RuntimeCore",
                "QuantumCommunicationGateway",
            ],
        )

        super().__init__(participant)
        self.lifecycle = InsightBridgeLifecycle()

    def execute(self, payload):
        return {
            "participant": self.name,
            "status": "accepted",
            "payload": payload,
        }

    def health(self):
        return {
            "participant": self.name,
            "state": self.lifecycle.state.value,
        }