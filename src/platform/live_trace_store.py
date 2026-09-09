import requests
from typing import Dict, Any

class LiveTraceStore:
    """
    Live TraceStore client that connects to the QCG Platform telemetry backend.
    """
    def __init__(self, endpoint_url="https://bhiv-qcg.onrender.com/qcg/telemetry"):
        self.endpoint_url = endpoint_url
        self.timeout = 10

    def record_execution_trace(self, **kwargs) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.endpoint_url}/execution",
                json=kwargs,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "FAILED",
                "type": "execution_trace",
                "error": str(e),
                **kwargs
            }

    def record_contract_lineage(self, **kwargs) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.endpoint_url}/contract_lineage",
                json=kwargs,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "FAILED",
                "type": "contract_lineage",
                "error": str(e),
                **kwargs
            }

    def record_adapter_trace(self, **kwargs) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.endpoint_url}/adapter_trace",
                json=kwargs,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "FAILED",
                "type": "adapter_trace",
                "error": str(e),
                **kwargs
            }

    def reconstruct_replay(self, trace_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.endpoint_url}/replay/{trace_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "trace_id": trace_id,
                "status": "UNAVAILABLE",
                "error": str(e)
            }

    def export_opentelemetry(self, trace_id: str) -> Dict[str, Any]:
        return {
            "trace_id": trace_id,
            "exported": False,
            "error": "OpenTelemetry export is handled server-side.",
            "provider": "LiveTraceStore"
        }
