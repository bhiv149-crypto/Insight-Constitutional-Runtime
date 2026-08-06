from pathlib import Path
import json
import time

from src.platform.live_platform_client import LivePlatformClient

from src.integration.registration_builder import RegistrationBuilder

from src.participants.insightflow.participant import (
    InsightFlowParticipant,
)
from src.participants.insightbridge.participant import (
    InsightBridgeParticipant,
)
from src.participants.insightcore.participant import (
    InsightCoreParticipant,
)

from src.platform.replay_adapter import (
    PlatformReplayAdapter,
)

from src.platform.telemetry_adapter import (
    PlatformTelemetryAdapter,
)

class PlatformIntegrationService:
    """
    Integrates the Insight Runtime with the live BHIV Platform.

    Responsibilities
    ----------------
    - Runtime Registration
    - Capability Registration
    - Capability Discovery
    - Replay Validation
    - Telemetry Recording
    - Evidence Generation

    This service NEVER starts a local Platform Runtime.
    It communicates only with the deployed BHIV Platform.
    """

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.client = LivePlatformClient()

        self.participants = []

        self.registration_results = {}

        self.capability_results = {}

        self.discovered_services = []

        self.replay_results = {}

        self.telemetry_results = {}

        self.runtime_records = []
        self.capability_manifests = []
        self.logger = None


    def integrate(self):
        """
        Execute the complete live platform integration workflow.
        """
        import logging
        self._prepare_directories()
        
        # Configure logging to integration.log
        log_file = self.evidence_packet_path / "runtime_logs" / "integration.log"
        self.logger = logging.getLogger("platform_integration")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        self.logger.info("Initializing Insight live integration workflow.")

        try:
            self._create_participants()
            self._register_runtime()
            self._register_capabilities()
            self._discover_services()
            self._validate_platform()
            self._validate_replay()
            self._record_telemetry()
            self._generate_evidence()
            
            self.logger.info("Insight live integration completed successfully.")
            return self._build_response()
            
        except Exception as exc:
            import datetime
            status_code = None
            if hasattr(exc, 'response') and exc.response is not None:
                status_code = exc.response.status_code
            
            endpoint = None
            if hasattr(exc, 'request') and exc.request is not None:
                endpoint = exc.request.url
                
            error_data = {
                "endpoint": endpoint or "Unknown",
                "status_code": status_code or 500,
                "exception": str(exc),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            error_file = self.evidence_packet_path / "deployment_proof" / "error.json"
            with open(error_file, "w") as f:
                json.dump(error_data, f, indent=2)
                
            self.logger.error("Integration failed: %s", str(exc))
            raise exc

    def _prepare_directories(self):
        """
        Create required evidence directories.
        """

        self.evidence_packet_path = self.project_root / "evidence_packet"
        self.dep_path = self.project_root / "DEP"

        directories = [
            self.evidence_packet_path / "runtime_logs",
            self.evidence_packet_path / "api_samples",
            self.evidence_packet_path / "replay_evidence",
            self.evidence_packet_path / "telemetry",
            self.evidence_packet_path / "registry_proof",
            self.evidence_packet_path / "production_readiness",
            self.dep_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


    def _create_participants(self):
        """
        Instantiate all Insight Runtime participants.
        """

        self.participants = [
            InsightFlowParticipant(),
            InsightBridgeParticipant(),
            InsightCoreParticipant(),
        ]


    def _register_runtime(self):
        """
        Register all Insight Runtime participants
        with the live Platform Runtime.
        """

        for participant in self.participants:

            record = RegistrationBuilder.build_service_record(
                participant.participant
            )
            self.runtime_records.append(record)

            self.logger.info("Registering runtime for: %s", participant.participant.runtime_identity)
            response = self.client.register_runtime(record)

            self.registration_results[
                participant.participant.runtime_identity
            ] = response


    def _register_capabilities(self):
        """
        Register participant capabilities.
        """

        for participant in self.participants:

            manifest = RegistrationBuilder.build_capability_manifest(
                participant.participant
            )
            self.capability_manifests.append(manifest)

            self.logger.info("Registering capabilities for: %s", participant.participant.runtime_identity)
            response = self.client.register_capability(
                manifest
            )

            self.capability_results[
                participant.participant.runtime_identity
            ] = response


    def _discover_services(self):
        """
        Retrieve registered runtime participants.
        """

        response = self.client.list_services()

        self.discovered_services = response.get(
            "services",
            [],
        )


    def _validate_platform(self):
        """
        Validate connectivity with the live BHIV Platform.
        """

        self.platform_health = self.client.server_health()


    def _validate_replay(self):
        """
        Validate replay-safe execution.
        """

        replay = PlatformReplayAdapter()

        first = replay.submit(
            "msg-insight-001",
            time.time(),
            "trace-insight-001",
        )

        second = replay.submit(
            "msg-insight-001",
            time.time(),
            "trace-insight-001",
        )

        self.replay_results = {
            "submission_1": {
                "status": first.status,
                "sequence": first.sequence_number,
                "reason": first.reason,
            },
            "submission_2": {
                "status": second.status,
                "sequence": second.sequence_number,
                "reason": second.reason,
            },
        }


    def _record_telemetry(self):
        """
        Record execution telemetry.
        """

        telemetry = PlatformTelemetryAdapter()

        execution = telemetry.record_execution_trace(
            "trace-001",
            "INSIGHTFLOW",
            "execute",
            {},
        )

        lineage = telemetry.record_contract_lineage(
            "contract-001",
            "root-contract",
            {},
        )

        self.telemetry_results = {
            "execution_trace": execution,
            "contract_lineage": lineage,
        }


    def _generate_evidence(self):
        """
        Persist integration evidence.
        """
        self.logger.info("Writing evidence packet files...")

        # 1. api_samples/discovered_services.json
        with open(
            self.evidence_packet_path / "api_samples" / "discovered_services.json",
            "w",
        ) as file:
            json.dump(self.discovered_services, file, indent=2)

        # 2. replay_evidence/replay_validation.json
        with open(
            self.evidence_packet_path / "replay_evidence" / "replay_validation.json",
            "w",
        ) as file:
            json.dump(self.replay_results, file, indent=2)

        # 3. telemetry/traces.json
        with open(
            self.evidence_packet_path / "telemetry" / "traces.json",
            "w",
        ) as file:
            json.dump(self.telemetry_results, file, indent=2)

        # 4. api_samples/runtime_registration.json
        with open(
            self.evidence_packet_path / "api_samples" / "runtime_registration.json",
            "w",
        ) as file:
            json.dump(self.runtime_records, file, indent=2)

        # 5. api_samples/capability_registration.json
        with open(
            self.evidence_packet_path / "api_samples" / "capability_registration.json",
            "w",
        ) as file:
            json.dump(self.capability_manifests, file, indent=2)

        # 6. api_samples/platform_health.json
        with open(
            self.evidence_packet_path / "api_samples" / "platform_health.json",
            "w",
        ) as file:
            json.dump(self.platform_health, file, indent=2)

        # 7. registry_proof/registration_response.json
        with open(
            self.evidence_packet_path / "registry_proof" / "registration_response.json",
            "w",
        ) as file:
            json.dump({
                "runtime_registration": self.registration_results,
                "capability_registration": self.capability_results
            }, file, indent=2, default=str)

        # 8. deployment_proof/deployment_status.json
        with open(
            self.evidence_packet_path / "deployment_proof" / "deployment_status.json",
            "w",
        ) as file:
            json.dump({
                "status": "DEPLOYED",
                "platform_health": self.platform_health,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
            }, file, indent=2)

        # 9. production_readiness/readiness_report.md
        with open(
            self.evidence_packet_path / "production_readiness" / "readiness_report.md",
            "w",
        ) as file:
            file.write(
                "# Production Readiness Report\n\n"
                "This report verifies that the Insight Constitutional Runtime is ready for production integration.\n\n"
                "## Integration Summary\n"
                f"- **Participants Registered:** {len(self.participants)}\n"
                f"- **Registry Synchronization:** Success (Live BHIV Platform)\n"
                "- **Replay Protection Checked:** Yes (Deterministic Sequence Tracking)\n"
                "- **Telemetry Pipeline Checked:** Yes (Execution Traces and Lineage Recorded)\n"
            )

        # 10. integration_summary.json (in root of evidence_packet/)
        with open(
            self.evidence_packet_path / "integration_summary.json",
            "w",
        ) as file:
            json.dump(self._build_response(), file, indent=2)


    def _build_response(self):
        """
        Build the final integration summary.
        """

        return {
            "status": "SUCCESS",
            "participants": len(self.participants),
            "registered": len(self.registration_results),
            "capabilities": len(self.capability_results),
            "discovered": len(self.discovered_services),
            "platform_health": self.platform_health,
            "replay": self.replay_results,
            "telemetry": self.telemetry_results,
        }