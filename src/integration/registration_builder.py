"""
Registration Builder

Builds the JSON payloads required to register
Insight Runtime participants with the live
BHIV Constitutional Runtime.

This module only constructs registration payloads.

It performs no network communication.
"""

import os

from src.common.models import RuntimeParticipant


class RegistrationBuilder:
    """
    Builds Platform Runtime registration artifacts from
    RuntimeParticipant metadata.
    """

    @staticmethod
    def _get_service_base_url() -> str:
        """
        Return the publicly reachable Insight execution-service URL.

        INSIGHT_SERVICE_URL must be supplied externally.

        No localhost, loopback, ngrok, localtunnel, or temporary
        tunnel fallback is permitted.
        """

        base_url = os.environ.get(
            "INSIGHT_SERVICE_URL",
            "",
        ).strip().rstrip("/")

        if not base_url:
            raise ValueError(
                "INSIGHT_SERVICE_URL is required for live registration. "
                "A public deployed Insight service URL must be provided."
            )

        forbidden_hosts = (
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            "ngrok",
            "loca.lt",
            "localtunnel",
        )

        lowered_url = base_url.lower()

        if any(host in lowered_url for host in forbidden_hosts):
            raise ValueError(
                "INSIGHT_SERVICE_URL must point to a real deployed "
                "public Insight service. Localhost and temporary "
                "tunnel URLs are not permitted."
            )

        return base_url

    @classmethod
    def build_service_record(
        cls,
        participant: RuntimeParticipant,
    ) -> dict:
        """
        Build the Platform Runtime service registration record.

        Accepts either:
        - RuntimeParticipant metadata
        - a BaseParticipant wrapper containing RuntimeParticipant

        No network communication occurs here.
        """

        metadata = getattr(participant, "participant", participant)

        service_id = metadata.runtime_identity
        base_url = cls._get_service_base_url()

        execution_endpoint = f"{base_url}/api/v1/execute"
        health_endpoint = f"{base_url}/api/v1/health/{service_id}"

        return {
            "platform_service_id": service_id,
            "capability_id": service_id,
            "service_name": metadata.participant_name,
            "version": metadata.version,
            "provider": "Insight Runtime",
            "owner": {
                "team": "Insight Stack",
                "contact": "insight-runtime@bhiv.internal",
            },
            "runtime_type": metadata.runtime_type,
            "service_classification": "DOMAIN_SERVICE",
            "capability_category": "INTELLIGENCE",
            "status": "ACTIVE",
            "description": (
                f"{metadata.participant_name} Runtime Participant"
            ),
            "tags": [
                "insight",
                "runtime",
                "constitutional",
            ],
            "endpoints": {
                "execution": execution_endpoint,
                "execute": execution_endpoint,
                "health": health_endpoint,
            },
            "dependencies": list(metadata.dependencies),
        }

    @staticmethod
    def build_capability_manifest(
        participant: RuntimeParticipant,
    ) -> dict:
        """
        Build the capability manifest expected by the
        canonical PlatformCapabilitySDK.

        Required SDK validation fields:
        - manifest_id
        - service_name
        - version
        - supported_operations
        - execution_modes
        """

        metadata = getattr(participant, "participant", participant)

        service_id = metadata.runtime_identity
        service_name = metadata.participant_name

        return {
            "manifest_id": f"{service_id}.manifest",
            "service_name": service_name,
            "capability_id": service_id,
            "capability_name": service_name.upper(),

            "owner": {
                "team": "Insight Stack",
                "contact": "insight-runtime@bhiv.internal",
            },

            "version": metadata.version,
            "status": "ACTIVE",
            "scope": "SYSTEM",

            "supported_operations": [
                {
                    "operation_name": "execute",
                    "input_contract": {
                        "type": "object",
                        "required": [],
                        "properties": {},
                    },
                    "output_contract": {
                        "type": "object",
                        "properties": {},
                    },
                },
                {
                    "operation_name": "health",
                    "input_contract": {
                        "type": "object",
                        "required": [],
                        "properties": {},
                    },
                    "output_contract": {
                        "type": "object",
                        "properties": {
                            "participant": {"type": "string"},
                            "runtime_identity": {"type": "string"},
                            "state": {"type": "string"},
                        },
                    },
                },
            ],

            "execution_modes": [
                "REST"
            ],

            "dependencies": list(
                metadata.dependencies
            ),

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

            "inputs": {
                "type": "object",
                "properties": {},
            },

            "outputs": {
                "type": "object",
                "properties": {},
            },

            "consumers": [],

            "documentation_reference": {
                "primary": f"{service_name}.md",
            },
        }