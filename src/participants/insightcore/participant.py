"""
InsightCore Constitutional Runtime Participant.

InsightCore is responsible for intelligence processing, runtime analysis,
and knowledge contribution within the Insight Stack.

Platform concerns such as registration, capability discovery,
capability invocation, replay participation, and runtime health
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

from .lifecycle import InsightCoreLifecycle


class InsightCoreParticipant(BaseParticipant):
    """
    Constitutional Runtime Participant representing InsightCore.
    """

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTCORE"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTCORE"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=(
                "intelligence_processing",
                "knowledge_contribution",
                "runtime_analysis",
            ),
            dependencies=(
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "RuntimeCore",
                "ReplayRegistry",
            ),
        )

        super().__init__(participant)

        self.lifecycle = InsightCoreLifecycle()

    # ------------------------------------------------------------------
    # Participant Behaviour
    # ------------------------------------------------------------------

    def execute(self, payload):
        """
        Execute InsightCore business logic.
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

        This represents InsightCore's lifecycle state and is
        distinct from Platform Runtime health.
        """

        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
        }