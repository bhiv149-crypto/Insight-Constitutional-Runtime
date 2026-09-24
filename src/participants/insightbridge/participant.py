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
from src.platform.quantum_adapter import MarineQuantumAdapter
from src.platform.insightbridge_adapter import InsightBridgeAdapter


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
        self.quantum_adapter = MarineQuantumAdapter()
        self.bridge_adapter = InsightBridgeAdapter()


    # ------------------------------------------------------------------
    # Participant Behaviour
    # ------------------------------------------------------------------

    def execute(self, payload):
        """
        Execute InsightBridge business logic.

        If payload requests Quantum execution (via target_capability or
        route="quantum"), delegates to the Marine Quantum Runtime
        via MarineQuantumAdapter. Otherwise, processes standard bridge payload.
        """
        if isinstance(payload, dict) and (
            payload.get("target_capability")
            or payload.get("quantum_capability")
            or payload.get("route") == "quantum"
        ):
            cap_id = (
                payload.get("target_capability")
                or payload.get("quantum_capability")
                or "quantum_pipeline"
            )
            q_payload = payload.get("quantum_payload")
            if q_payload is None:
                # If no nested quantum_payload, extract fields excluding routing keys
                q_payload = {
                    k: v
                    for k, v in payload.items()
                    if k not in ("route", "target_capability", "quantum_capability", "participant", "operation", "version")
                }
            quantum_result = self.quantum_adapter.invoke_capability(cap_id, q_payload)
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "accepted",
                "quantum_route": "DELEGATED_QUANTUM",
                "quantum_capability": cap_id,
                "quantum_result": quantum_result,
                "payload": payload,
            }

        # ---------------------------------------------------------
        # REAL PARTICIPANT EXECUTION LOGIC (CLASSICAL BRIDGE)
        # ---------------------------------------------------------
        # The semantic contract for classical runtime_bridge event routing
        # is insufficiently defined. The participant lacks a real internal event bus.
        
        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "executed",
            "semantic_status": "SEMANTIC_CONTRACT_INSUFFICIENTLY_DEFINED",
            "payload": payload,
        }

    def invoke_quantum(self, capability_id: str, payload: dict) -> dict:
        """
        Direct quantum invocation gateway on InsightBridge.
        """
        return self.quantum_adapter.invoke_capability(capability_id, payload)

    def quantum_health(self) -> dict:
        """
        Query health of the attached Quantum Runtime.
        """
        return self.quantum_adapter.health()

    def health(self):
        """
        Return participant runtime state.

        This represents InsightBridge's lifecycle state and is
        distinct from Platform Runtime health.
        """

        gateway_health = self.bridge_adapter.health()

        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
            "quantum_gateway": {
                "attached": True,
                "runtime": "Marine Quantum Runtime",
                "mode": self.quantum_adapter.mode,
            },
            "gateway_health": gateway_health,
        }
