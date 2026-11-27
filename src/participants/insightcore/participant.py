"""
InsightCore Constitutional Runtime Participant (Insight Intelligence Engine).

InsightCore is responsible for genuine intelligence processing, runtime
analysis, and knowledge contribution within the Insight Stack.
"""

from typing import Any, Dict

from src.common.base_participant import BaseParticipant
from src.common.constants import (
    CONSTITUTIONAL_LAYER,
    PARTICIPANTS,
    PROJECT_VERSION,
    RUNTIME_IDENTITIES,
    RUNTIME_TYPE,
)
from src.common.insight_contracts import ExecutionClassification, IntelligenceProcessRequest
from src.common.models import RuntimeParticipant
from src.config.platform_config import is_http_services_mode
from src.platform.insight_intelligence_adapter import InsightIntelligenceAdapter
from src.platform.quantum_adapter import compute_execution_digest
from src.services.insight_intelligence_service import execute_intelligence_task

from .lifecycle import InsightCoreLifecycle


class InsightCoreParticipant(BaseParticipant):
    """Constitutional Runtime Participant representing InsightCore (IIE)."""

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
        self.core_adapter = InsightIntelligenceAdapter()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute InsightCore intelligence processing.

        - If INSIGHT_SERVICES_HTTP=true and task_type is provided, delegates over HTTP
          to the live/local Insight Intelligence Engine (:8030) service.
        - If task_type is provided locally, executes deterministic intelligence processing.
        - For lightweight contract probes without task_type, validates payload and
          computes canonical SHA-256 execution digest.
        """
        if not isinstance(payload, dict):
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "FAILED",
                "error": "Payload must be a JSON object",
            }

        use_http = is_http_services_mode()
        task_type = payload.get("task_type")

        if use_http and task_type:
            req_body = {
                "task_type": task_type,
                "domain": payload.get("domain", "QCG"),
                "payload": payload.get("data", payload.get("payload", payload)),
            }
            for k in ("correlation_id", "trace_id", "invocation_id"):
                if k in payload:
                    req_body[k] = payload[k]
            res = self.core_adapter.process(req_body)
            if res["status"] != "SUCCESS":
                return {
                    "participant": self.name,
                    "runtime_identity": self.identity,
                    "version": self.version,
                    "status": res["status"],
                    "error": res.get("error", "InsightCore processing failed"),
                    "downstream_result": res,
                }
            core_data = res["data"]
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "executed",
                "execution_classification": core_data.get(
                    "execution_classification", ExecutionClassification.CLASSICAL_INTELLIGENCE.value
                ),
                "execution_digest": core_data.get("execution_digest"),
                "processing_result": core_data,
                "payload": payload,
            }

        if task_type:
            req = IntelligenceProcessRequest(
                task_type=task_type,
                domain=payload.get("domain", "QCG"),
                payload=payload.get("data", payload.get("payload", payload)),
            )
            proc = execute_intelligence_task(req)
            if proc.status != "COMPLETED":
                return {
                    "participant": self.name,
                    "runtime_identity": self.identity,
                    "version": self.version,
                    "status": proc.status,
                    "execution_classification": proc.execution_classification,
                    "execution_digest": proc.execution_digest,
                    "error": proc.error,
                    "payload": payload,
                }
            return {
                "participant": self.name,
                "runtime_identity": self.identity,
                "version": self.version,
                "status": "executed",
                "execution_classification": proc.execution_classification,
                "execution_digest": proc.execution_digest,
                "processing_result": proc.model_dump(),
                "payload": payload,
            }

        digest = compute_execution_digest(payload)
        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "version": self.version,
            "status": "executed",
            "execution_classification": ExecutionClassification.CLASSICAL_INTELLIGENCE.value,
            "execution_digest": digest,
            "validated_keys": sorted(payload.keys()),
            "payload": payload,
        }

    def health(self) -> Dict[str, Any]:
        return {
            "participant": self.name,
            "runtime_identity": self.identity,
            "state": self.lifecycle.state.value,
            "core_service_health": self.core_adapter.health() if is_http_services_mode() else "LOCAL_READY",
        }
