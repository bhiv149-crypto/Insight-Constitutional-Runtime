"""
InsightBridge Constitutional Runtime Participant (Insight Communication & Routing Gateway).

InsightBridge is responsible for bridging runtime communication,
policy enforcement, trace propagation, intelligence routing, and
quantum execution boundary delegation.
"""

from src.common.base_participant import BaseParticipant
from src.common.constants import (
    CONSTITUTIONAL_LAYER,
    PARTICIPANTS,
    PROJECT_VERSION,
    RUNTIME_IDENTITIES,
    RUNTIME_TYPE,
)
from src.common.insight_contracts import ExecutionClassification, GatewayRouteRequest, RouteTarget
from src.common.jwt_security import evaluate_policy
from src.common.models import RuntimeParticipant
from src.config.platform_config import is_http_services_mode
from src.platform.insight_gateway_adapter import InsightGatewayAdapter
from src.platform.quantum_adapter import MarineQuantumAdapter, compute_execution_digest
from src.services.insight_gateway_service import (
    route_intelligence_inprocess,
    route_quantum_inprocess,
)

from .lifecycle import InsightBridgeLifecycle


class InsightBridgeParticipant(BaseParticipant):
    """Constitutional Runtime Participant representing InsightBridge (ICRG)."""

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
        self.bridge_adapter = InsightGatewayAdapter()

    def execute(self, payload):
        """
        Execute InsightBridge routing logic:
          - Quantum route -> MarineQuantumAdapter (or Insight Gateway HTTP service when INSIGHT_SERVICES_HTTP=true)
          - Intelligence route -> Insight Gateway HTTP service -> Insight Intelligence Engine
          - Standard bridge route -> deterministic policy evaluation + SHA-256 digest
        """
        use_http = is_http_services_mode()

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
                q_payload = {
                    k: v
                    for k, v in payload.items()
                    if k not in ("route", "target_capability", "quantum_capability", "participant", "operation", "version")
                }

            if use_http:
                res = self.bridge_adapter.route_quantum(
                    {
                        "route_target": "QUANTUM",
                        "capability_id": cap_id,
                        "domain": payload.get("domain", "MARINE"),
                        "payload": q_payload,
                        **{k: payload[k] for k in ("correlation_id", "trace_id", "invocation_id") if k in payload},
                    }
                )
                if res["status"] != "SUCCESS":
                    return {
                        "participant": self.name,
                        "runtime_identity": self.identity,
                        "version": self.version,
                        "status": res["status"],
                        "quantum_route": "DELEGATED_QUANTUM",
                        "quantum_capability": cap_id,
                        "error": res.get("error"),
                        "payload": payload,
                    }
                data = res["data"]
                return {
                    "participant": self.name,
                    "runtime_identity": self.identity,
                    "version": self.version,
                    "status": "accepted" if data.get("status") == "COMPLETED" else data.get("status", "FAILED"),
                    "quantum_route": "DELEGATED_QUANTUM",
                    "quantum_capability": cap_id,
                    "quantum_result": data.get("result", data),
                    "execution_classification": data.get("execution_classification"),
                    "payload": payload,
                }

            gw_req = GatewayRouteRequest(
                route_target=RouteTarget.QUANTUM,
                capability_id=cap_id,
                domain=payload.get("domain", "MARINE"),
                payload=q_payload,
                **{k: payload[k] for k in ("correlation_id", "trace_id", "invocation_id", "idempotency_key") if k in payload},
            )
            gw_res = route_quantum_inprocess(
                gw_req,
                client_id=str(payload.get("client_id", "icr-principal")),
            )
            q_status = str(gw_res.status).upper()
            mapped_status = "accepted" if q_status in ("SUCCESS", "COMPLETED") else q_status
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": mapped_status,
                "quantum_route": "DELEGATED_QUANTUM",
                "quantum_capability": cap_id,
                "quantum_result": gw_res.result,
                "execution_classification": gw_res.execution_classification,
                "execution_digest": gw_res.execution_digest,
                "provenance_nonce": gw_res.provenance_nonce,
                "idempotent_replay": gw_res.idempotent_replay,
                "error": gw_res.error if mapped_status != "accepted" else None,
                "payload": payload,
            }

        if isinstance(payload, dict) and (payload.get("route") == "intelligence" or payload.get("task_type")):
            if use_http:
                res = self.bridge_adapter.route_intelligence(
                    {
                        "route_target": "INTELLIGENCE",
                        "task_type": payload.get("task_type", "marine_signal_analysis"),
                        "domain": payload.get("domain", "QCG"),
                        "payload": payload.get("data", payload.get("payload", payload)),
                        **{k: payload[k] for k in ("correlation_id", "trace_id", "invocation_id", "idempotency_key") if k in payload},
                    }
                )
                if res["status"] != "SUCCESS":
                    return {
                        "participant": self.name,
                        "runtime_identity": self.identity,
                        "version": self.version,
                        "status": res["status"],
                        "error": res.get("error"),
                        "payload": payload,
                    }
                data = res["data"]
            else:
                gw_res = route_intelligence_inprocess(
                    GatewayRouteRequest(
                        route_target=RouteTarget.INTELLIGENCE,
                        task_type=payload.get("task_type", "marine_signal_analysis"),
                        domain=payload.get("domain", "QCG"),
                        payload=payload.get("data", payload.get("payload", payload)),
                        **{k: payload[k] for k in ("correlation_id", "trace_id", "invocation_id", "idempotency_key") if k in payload},
                    ),
                    client_id=str(payload.get("client_id", "icr-principal")),
                )
                data = gw_res.model_dump()

            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "executed" if data.get("status") == "COMPLETED" else data.get("status", "FAILED"),
                "execution_classification": data.get("execution_classification"),
                "execution_digest": data.get("execution_digest"),
                "routed_result": data,
                "error": data.get("error"),
                "payload": payload,
            }

        client_id = str(payload.get("client_id", "icr-principal")) if isinstance(payload, dict) else "icr-principal"
        decision, reason = evaluate_policy(client_id, "insightbridge:execute", "execute")
        digest = compute_execution_digest(payload)
        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "executed" if decision == "ALLOW" else "DENIED",
            "policy_decision": decision,
            "policy_reason": reason,
            "execution_classification": ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
            "execution_digest": digest,
            "payload": payload,
        }

    def invoke_quantum(self, capability_id: str, payload: dict) -> dict:
        return self.quantum_adapter.invoke_capability(capability_id, payload)

    def quantum_health(self) -> dict:
        return self.quantum_adapter.health()

    def health(self):
        gateway_health = self.bridge_adapter.health() if is_http_services_mode() else "LOCAL_READY"
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
