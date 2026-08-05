"""
InsightBridge Constitutional Runtime Participant.

InsightBridge is responsible for bridging runtime communication,
trace propagation, and event forwarding between the Insight Stack
and the Constitutional Runtime ecosystem.

Platform concerns such as registration, capability discovery,
capability invocation, runtime health, and replay participation
are delegated through BaseParticipant.
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
    """
    Constitutional Runtime Participant representing InsightBridge.
    """

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTBRIDGE"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTBRIDGE"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=(
                "runtime_bridge",
                "trace_propagation",
                "event_forwarding",
            ),
            dependencies=(
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "RuntimeCore",
                "QuantumCommunicationGateway",
            ),
        )

        super().__init__(participant)

        self.lifecycle = InsightBridgeLifecycle()

    # ------------------------------------------------------------------
    # Participant Behaviour
    # ------------------------------------------------------------------

    def execute(self, payload):
        """
        Execute InsightBridge business logic.
        """

        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "accepted",
            "payload": payload,
        }

    def health(self):
        """
        Return participant runtime state.

        This represents InsightBridge's lifecycle state and is
        distinct from Platform Runtime health.
        """

        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
        }