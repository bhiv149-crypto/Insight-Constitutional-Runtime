"""
InsightFlow Constitutional Runtime Participant (Insight Workflow Orchestrator).

InsightFlow is responsible for deterministic workflow orchestration inside
the Insight Stack, delegating multi-step workflows to Insight Workflow Orchestrator (:8031)
when HTTP orchestration is enabled.
"""

from src.common.base_participant import BaseParticipant
from src.common.constants import (
    CONSTITUTIONAL_LAYER,
    PARTICIPANTS,
    PROJECT_VERSION,
    RUNTIME_IDENTITIES,
    RUNTIME_TYPE,
)
from src.common.insight_contracts import WorkflowState, WorkflowSubmitRequest
from src.common.models import RuntimeParticipant
from src.config.platform_config import is_http_services_mode
from src.platform.insight_workflow_adapter import InsightWorkflowAdapter
from src.platform.quantum_adapter import compute_execution_digest
from src.services.insight_workflow_service import run_workflow_pipeline

from .lifecycle import InsightFlowLifecycle


class InsightFlowParticipant(BaseParticipant):
    """Constitutional Runtime Participant representing InsightFlow (IWO)."""

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
        self.flow_adapter = InsightWorkflowAdapter()

    def execute(self, payload):
        """
        Execute InsightFlow workflow orchestration.

        - If INSIGHT_SERVICES_HTTP=true and workflow_type/task_type is specified,
          executes a full orchestrated workflow via Insight Workflow Orchestrator (:8031).
        - If action == "enforce", delegates policy enforcement via InsightWorkflowAdapter.
        - Otherwise performs deterministic workflow validation & digest calculation.
        """
        use_http = is_http_services_mode()

        if isinstance(payload, dict) and (payload.get("workflow_type") or payload.get("task_type")):
            wf_req = {
                "workflow_type": payload.get("workflow_type", "INTELLIGENCE"),
                "capability_id": payload.get("capability_id", "quantum_pipeline"),
                "task_type": payload.get("task_type", "marine_signal_analysis"),
                "domain": payload.get("domain", "QCG"),
                "payload": payload.get("data", payload.get("payload", payload)),
                **{k: payload[k] for k in ("correlation_id", "trace_id", "invocation_id", "idempotency_key") if k in payload},
            }
            if use_http:
                res = self.flow_adapter.execute_workflow(wf_req)
                if res["status"] != "SUCCESS":
                    return {
                        "participant": self.name,
                        "runtime_identity": self.identity,
                        "version": self.version,
                        "status": res["status"],
                        "workflow_state": WorkflowState.UNAVAILABLE.value if res["status"] == "UNAVAILABLE" else WorkflowState.FAILED.value,
                        "error": res.get("error"),
                        "payload": payload,
                    }
                wf_data = res["data"]
            else:
                wf_res = run_workflow_pipeline(
                    WorkflowSubmitRequest(**wf_req),
                    client_id=str(payload.get("client_id", "icr-principal")),
                    use_http=False,
                )
                wf_data = wf_res.model_dump()

            wf_state = wf_data.get("state", "FAILED")
            if hasattr(wf_state, "value"):
                wf_state = wf_state.value
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "executed" if wf_state == "COMPLETED" else wf_state,
                "workflow_id": wf_data.get("workflow_id"),
                "workflow_state": wf_state,
                "workflow_result": wf_data,
                "error": wf_data.get("error"),
                "payload": payload,
            }

        enforce_result = None
        if isinstance(payload, dict) and payload.get("action") == "enforce":
            enforce_result = self.flow_adapter.enforce(payload)

        digest = compute_execution_digest(payload)
        result = {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "executed",
            "workflow_state": WorkflowState.COMPLETED.value,
            "execution_digest": digest,
            "payload": payload,
        }
        if enforce_result is not None:
            result["enforce_result"] = enforce_result
        return result

    def health(self):
        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
        }
