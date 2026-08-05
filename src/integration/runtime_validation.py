"""
Runtime Validation

Validates that the Insight Runtime is correctly configured
for Constitutional Runtime integration.

This validator checks adapter availability and runtime wiring.
It does not require a live Platform Runtime.
"""

from src.platform.runtime_adapter import PlatformRuntimeAdapter
from src.platform.replay_adapter import PlatformReplayAdapter
from src.platform.health_adapter import PlatformHealthAdapter
from src.platform.telemetry_adapter import PlatformTelemetryAdapter


class RuntimeValidation:
    """
    Runtime readiness validator.
    """

    def __init__(self):
        self.runtime = PlatformRuntimeAdapter()
        self.replay = PlatformReplayAdapter()
        self.health = PlatformHealthAdapter()
        self.telemetry = PlatformTelemetryAdapter()

    def validate(self):
        """
        Validate Runtime readiness.
        """

        report = {
        "runtime_adapter": False,
        "health_adapter": False,
        "replay_adapter": False,
        "telemetry_adapter": False,
        "registration": False,
        "discovery": False,
        "capability_invocation": False,
        "runtime_health": False,
        "runtime_metrics": False,
        "trace_export": False,
        "replay_validation": False,
        "runtime_ready": False,
    }

        try:
            if self.runtime:
                report["runtime_adapter"] = True

            if self.health:
                report["health_adapter"] = True

            if self.replay:
                report["replay_adapter"] = True

            if self.telemetry:
                report["telemetry_adapter"] = True

            if hasattr(self.runtime, "register_service"):
                report["registration"] = True

            if hasattr(self.runtime, "discover_services"):
                report["discovery"] = True

            if hasattr(self.runtime, "invoke_capability"):
                report["capability_invocation"] = True

            if hasattr(self.runtime, "get_health"):
                report["runtime_health"] = True

            if hasattr(self.runtime, "metrics"):
                report["runtime_metrics"] = True

            if hasattr(self.runtime, "export_opentelemetry"):
                report["trace_export"] = True

            if hasattr(self.replay, "submit"):
                report["replay_validation"] = True

            report["runtime_ready"] = all(
                value for key, value in report.items()
                if key != "runtime_ready"
            )

        except Exception as exc:
            report["error"] = str(exc)

        return report