"""
InsightCore Constitutional Runtime Participant.
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

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTCORE"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTCORE"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=[
                "intelligence_processing",
                "knowledge_contribution",
                "runtime_analysis",
            ],
            dependencies=[
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "RuntimeCore",
                "ReplayRegistry",
            ],
        )

        super().__init__(participant)
        self.lifecycle = InsightCoreLifecycle()

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