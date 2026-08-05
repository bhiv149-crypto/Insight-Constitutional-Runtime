"""
Registration Builder

Builds the Platform Runtime registration objects required for
registering an Insight Runtime Participant.

This module only constructs Platform models.
Registration is performed by ParticipantRegistration.
"""

from src.common.models import RuntimeParticipant

from src.platform.imports import (
    PlatformServiceRecord,
    CapabilityManifest,
    OperationContract,
)


class RegistrationBuilder:
    """
    Builds Platform Runtime registration artifacts from
    RuntimeParticipant metadata.
    """

    @staticmethod
    def build_operation_contract(participant: RuntimeParticipant):
        """
        Build the default execution contract.
        """

        return OperationContract(
            operation_name="execute",
            description=f"Execute {participant.participant_name}",
            input_contract={
                "type": "object"
            },
            output_contract={
                "type": "object"
            },
            execution_modes=["SYNCHRONOUS"],
            idempotent=True,
        )

    @staticmethod
    def build_capability_manifest(participant: RuntimeParticipant):

        operation = RegistrationBuilder.build_operation_contract(
            participant
        )

        return CapabilityManifest(
            manifest_id=f"{participant.runtime_identity}-MANIFEST",
            service_name=participant.participant_name,
            version=participant.version,
            supported_operations=[operation],
            execution_modes=["SYNCHRONOUS"],
            determinism_guarantees={
                "strict_determinism": True
            },
            replay_guarantees={
                "replay_safe": True
            },
            trust_requirements={
                "provider": "Platform"
            },
            evidence_guarantees={
                "hash_chain": True
            },
            runtime_dependencies=list(participant.dependencies),
            version_compatibility={
                "supported": [participant.version]
            },
            security_requirements={
                "authentication": True
            },
            resource_requirements={},
        )

    @staticmethod
    def build_service_record(participant: RuntimeParticipant):

        return PlatformServiceRecord(
            platform_service_id=participant.runtime_identity,
            capability_id=participant.runtime_identity,
            service_name=participant.participant_name,
            version=participant.version,
            provider="Insight Runtime",
            owner={
                "team": "Insight Stack"
            },
            runtime_type=participant.runtime_type,
            service_classification="DOMAIN_SERVICE",
            capability_category="INTELLIGENCE",
            status="ACTIVE",
            endpoints={},
        )