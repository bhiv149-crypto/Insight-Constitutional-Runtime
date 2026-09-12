"""
InsightFlow Constitutional Runtime Participant.

InsightFlow is responsible for workflow orchestration inside the
Insight Stack. Platform concerns such as registration, capability
discovery, invocation and runtime health are delegated to the
Platform Runtime Adapter through BaseParticipant.
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
from src.platform.insightflow_adapter import InsightFlowAdapter


class InsightFlowParticipant(BaseParticipant):
    """
    Constitutional Runtime Participant representing InsightFlow.
    """

    def __init__(self):

        participant = RuntimeParticipant(
            participant_name=PARTICIPANTS["INSIGHTFLOW"],
            runtime_identity=RUNTIME_IDENTITIES["INSIGHTFLOW"],
            version=PROJECT_VERSION,
            constitutional_layer=CONSTITUTIONAL_LAYER,
            runtime_type=RUNTIME_TYPE,
            capabilities=(
                "workflow_orchestration",
                "capability_invocation",
                "trace_generation",
                "evidence_generation",
            ),
            dependencies=(
                "PlatformCapabilitySDK",
                "PlatformDiscovery",
                "PlatformRegistry",
                "RuntimeCore",
            ),
        )

        super().__init__(participant)

        self.lifecycle = InsightFlowLifecycle()
        self.flow_adapter = InsightFlowAdapter()

    # ------------------------------------------------------------------
    # Participant Behaviour
    # ------------------------------------------------------------------

    def execute(self, payload):
        """
        Execute InsightFlow business logic.

        Runtime responsibilities such as capability invocation,
        tracing and replay are delegated through BaseParticipant.
        """

        flow_health = self.flow_adapter.health()
        enforce_result = None

        if isinstance(payload, dict) and payload.get("action") == "enforce":
            enforce_result = self.flow_adapter.enforce(payload)

        # ---------------------------------------------------------
        # REAL PARTICIPANT EXECUTION LOGIC
        # ---------------------------------------------------------
        # The semantic contract for workflow_orchestration is insufficiently defined.
        # Flow validates /enforce but lacks an internal state machine.
        
        result = {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "executed",
            "semantic_status": "SEMANTIC_CONTRACT_INSUFFICIENTLY_DEFINED",
            "payload": payload,
            "flow_health": flow_health,
        }
        if enforce_result is not None:
            result["enforce_result"] = enforce_result
        return result

    def health(self):
        """
        Participant runtime state.

        This is participant health, not Platform Runtime health.
        """

        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
        }