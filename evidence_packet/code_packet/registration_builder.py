"""
Registration Builder

Builds the JSON payloads required to register
Insight Runtime participants with the live
BHIV Constitutional Runtime.

This module only constructs REST payloads.

It performs no network communication.
"""
from src.common.models import RuntimeParticipant



class RegistrationBuilder:
    """
    Builds Platform Runtime registration artifacts from
    RuntimeParticipant metadata.
    """

    @staticmethod
    def build_service_record(participant: RuntimeParticipant) -> dict:

        service_id = participant.runtime_identity
        import os
        base_url = os.environ.get("INSIGHT_SERVICE_URL", "https://slapstick-ditch-raving.ngrok-free.dev")

        return {
            "platform_service_id": service_id,
            "capability_id": service_id,
            "service_name": participant.participant_name,
            "version": participant.version,
            "provider": "Insight Runtime",
            "owner": {
                "team": "Insight Stack",
                "contact": "insight-runtime@bhiv.internal",
            },
            "runtime_type": participant.runtime_type,
            "service_classification": "DOMAIN_SERVICE",
            "capability_category": "INTELLIGENCE",
            "status": "ACTIVE",
            "description": f"{participant.participant_name} Runtime Participant",
            "tags": [
                "insight",
                "runtime",
                "constitutional",
            ],
            "endpoints": {
                "execute": f"{base_url}/api/v1/execute",
                "execution": f"{base_url}/api/v1/execute",
                "health": f"{base_url}/api/v1/health/{service_id}",
            },
            "dependencies": list(participant.dependencies),
        }


    
    @staticmethod
    def build_capability_manifest(participant: RuntimeParticipant) -> dict:

        return {
            "capability_id": participant.runtime_identity,
            "capability_name": participant.participant_name.upper(),
            "owner": {
                "team": "Insight Stack",
                "contact": "insight-runtime@bhiv.internal",
            },
            "version": participant.version,
            "status": "ACTIVE",
            "scope": "SYSTEM",
            "dependencies": list(participant.dependencies),
            "attachment_rules": {
                "attachment_type": "embedded",
                "protocol": "REST",
                "idempotent": True,
            },
            "authority_limits": {
                "owns": [
                    "Insight execution",
                    "Evidence generation",
                ],
                "does_not_own": [
                    "Platform governance",
                    "Quantum execution",
                ],
                "requires_governance_approval": False,
            },
            "inputs": [],
            "outputs": [],
            "consumers": [],
            "documentation_reference": {
                "primary": f"{participant.participant_name}.md",
            },
        }
