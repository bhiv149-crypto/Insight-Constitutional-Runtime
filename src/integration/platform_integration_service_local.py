from pathlib import Path
import time

import src.platform.imports
import config

from src.participants.insightflow.participant import InsightFlowParticipant
from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.participants.insightcore.participant import InsightCoreParticipant
from src.integration.registration_builder import RegistrationBuilder
from src.platform.runtime_adapter import PlatformRuntimeAdapter
from src.platform.replay_adapter import PlatformReplayAdapter
from src.platform.telemetry_adapter import PlatformTelemetryAdapter

from capability_registry import CapabilityRegistryServer
from platform_service_registry import (
    PlatformServiceRegistry,
    RegistrationEvidenceRecorder,
)
from platform_lifecycle_manager import LifecycleManager
from platform_service_discovery import PlatformDiscoveryServer
from federated_registry import FederatedRegistryNode


class PlatformIntegrationService:
    """
    Reusable orchestration service for Insight Runtime integration.

    Used by:
        - test_live_integration.py
        - insight_platform_agent.py

    Contains no FastAPI code.
    Contains no HTTP endpoints.
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]

        self.cap_server = None
        self.nodes = []
        self.discovery_servers = []

        self.participants = []

        self.registration_results = {}
        self.discovered_services = []

        self.replay_results = {}
        self.telemetry_results = {}

    def integrate(self, local_runtime=True):
        """
        Executes the complete runtime integration workflow.
        """
        if local_runtime:
            self._start_platform()

        try:

            self._prepare_directories()

            self._create_participants()

            self._register_participants()

            self._discover_capabilities()

            self._validate_replay()

            self._record_telemetry()

            self._generate_evidence()

            return self._build_response()

        finally:

            if local_runtime:
                self._shutdown_platform()
    #
    # Internal Steps
    #

    def _start_platform(self):
        """
        Starts the local Platform Runtime required for integration.
        """

        print("Starting Capability Registry Server...")

        self.cap_server = CapabilityRegistryServer(
            "127.0.0.1",
            config.REGISTRY_PORT,
        )

        self.cap_server.start()

        time.sleep(0.5)

        print("Starting Federated Discovery Nodes...")

        num_nodes = 3
        base_port = config.DISCOVERY_PORT_BASE

        self.nodes = []
        self.discovery_servers = []

        #
        # Create federation nodes
        #

        for i in range(num_nodes):

            node = FederatedRegistryNode(
                node_id=f"FEDERATION-NODE-{i+1}",
                registry=PlatformServiceRegistry(
                    evidence_recorder=RegistrationEvidenceRecorder()
                ),
                port=base_port + i,
            )

            self.nodes.append(node)

        #
        # Wire peers
        #

        for i, node in enumerate(self.nodes):

            for j, peer in enumerate(self.nodes):

                if i != j:
                    node.add_peer(peer)

        #
        # Start discovery servers
        #

        for i, node in enumerate(self.nodes):

            server = PlatformDiscoveryServer(
                host="127.0.0.1",
                port=base_port + i,
                registry=node.registry,
                lifecycle=LifecycleManager(),
                federation_node=node,
            )

            server.start()

            self.discovery_servers.append(server)

            time.sleep(0.3)

        print("Platform Runtime started successfully.")

    def _prepare_directories(self):
        """
        Create all required evidence directories.
        """

        self.evidence_packet_path = self.project_root / "evidence_packet"
        self.dep_path = self.project_root / "DEP"

        directories = [
            self.evidence_packet_path / "runtime_logs",
            self.evidence_packet_path / "api_samples",
            self.evidence_packet_path / "replay_evidence",
            self.evidence_packet_path / "telemetry",
            self.evidence_packet_path / "deployment_proof",
            self.evidence_packet_path / "production_readiness",
            self.evidence_packet_path / "registry_proof",
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

    def _register_participants(self):
        """
        Register all Insight Runtime participants with the Platform Runtime.
        """

        print("\nRegistering Insight Runtime participants...")

        node = self.nodes[0]

        self.registration_results = {}

        for participant in self.participants:

            record = RegistrationBuilder.build_service_record(
                participant.participant
            )

            manifest = RegistrationBuilder.build_capability_manifest(
                participant.participant
            )

            result = node.register_service_authenticated(
                record,
                manifest,
            )

            self.registration_results[
                participant.identity
            ] = result

            print(
                f"Registered {participant.name}: "
                f"{result.get('status')}"
            )

        #
        # Synchronize federation
        #

        print("\nSynchronizing registry...")

        for node in self.nodes:
            node.anti_entropy_sync()

        time.sleep(0.5)

    def _discover_capabilities(self):
        """
        Discover all registered Insight Runtime participants.
        """

        print("\nDiscovering registered runtime participants...")

        runtime_adapter = PlatformRuntimeAdapter()

        runtime_adapter.sdk.discovery_urls = [
            "http://127.0.0.1:9010"
        ]

        self.discovered_services = runtime_adapter.discover_services()

        print(
            f"Discovered {len(self.discovered_services)} services:"
        )

        for service in self.discovered_services:

            print(
                f"  - {service.get('platform_service_id')} "
                f"({service.get('service_name')})"
            )
    def _validate_replay(self):
        """
        Validate replay-safe execution.
        """

        print("\nValidating replay...")

        replay = PlatformReplayAdapter()

        first = replay.submit(
            "msg-insight-001",
            time.time(),
            "trace-ref-abc",
        )

        second = replay.submit(
            "msg-insight-001",
            time.time(),
            "trace-ref-abc",
        )

        print("Replay 1:", first.status)
        print("Replay 2:", second.status)

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
        Record runtime telemetry.
        """

        print("\nRecording telemetry...")

        telemetry = PlatformTelemetryAdapter()

        execution = telemetry.record_execution_trace(
            "trace-001",
            "INSIGHTFLOW",
            "execute",
            {"param": "val"},
        )

        lineage = telemetry.record_contract_lineage(
            "contract-001",
            "parent-001",
            {"policy": "strict"},
        )

        print("Execution:", execution.get("status"))
        print("Lineage :", lineage.get("status"))

        self.telemetry_results = {
            "execution_trace": execution,
            "contract_lineage": lineage,
        }

    def _generate_evidence(self):
        """
        Persist runtime evidence.
        """

        import json

        #
        # Registration
        #

        with open(
            self.evidence_packet_path
            / "registry_proof"
            / "registration_receipts.json",
            "w",
        ) as f:

            json.dump(
                self.registration_results,
                f,
                indent=2,
                default=str,
            )

        #
        # Discovery
        #

        with open(
            self.evidence_packet_path
            / "api_samples"
            / "discovered_services.json",
            "w",
        ) as f:

            json.dump(
                self.discovered_services,
                f,
                indent=2,
                default=str,
            )

        #
        # Replay
        #

        with open(
            self.evidence_packet_path
            / "replay_evidence"
            / "replay_validation.json",
            "w",
        ) as f:

            json.dump(
                self.replay_results,
                f,
                indent=2,
                default=str,
            )

        #
        # Telemetry
        #

        with open(
            self.evidence_packet_path
            / "telemetry"
            / "traces.json",
            "w",
        ) as f:

            json.dump(
                self.telemetry_results,
                f,
                indent=2,
                default=str,
            )

    def _shutdown_platform(self):
        """
        Shutdown platform runtime.
        """

        print("\nStopping Platform Runtime...")

        for server in self.discovery_servers:
            server.stop()

        if self.cap_server:
            self.cap_server.stop()

        print("Platform stopped.")

    def _build_response(self):

        return {
            "status": "SUCCESS",
            "participants": len(self.participants),
            "registered": len(self.registration_results),
            "discovered": len(self.discovered_services),
            "replay": self.replay_results,
            "telemetry": self.telemetry_results,
        }