"""
Participant Registration.

Responsible for attaching Constitutional Runtime Participants
to the Platform Runtime.

Registration logic is delegated to PlatformRuntimeAdapter.
"""

from src.platform.runtime_adapter import PlatformRuntimeAdapter
from src.platform.imports import PlatformServiceRecord


class ParticipantRegistration:
    """
    Registers Insight Runtime Participants with the
    Constitutional Runtime.
    """

    def __init__(self, runtime=None):
        self.runtime = runtime or PlatformRuntimeAdapter()

    def build_service_record(self, participant):
        """
        Convert a RuntimeParticipant into a PlatformServiceRecord.
        """

        return PlatformServiceRecord(
            platform_service_id=participant.runtime_identity,
            capability_id=participant.runtime_identity,
            service_name=participant.participant_name,
            version=participant.version,
            provider="Insight Stack",
            owner={
                "team": "Insight",
                "participant": participant.participant_name,
            },
            runtime_type=participant.runtime_type,
            service_classification="DOMAIN_SERVICE",
            capability_category="EXECUTION",
            status="ACTIVE",
        )

    def build_registration(self, participant, manifest=None):
        """
        Build a Platform Runtime registration payload.
        """

        return {
            "record": self.build_service_record(participant),
            "manifest": manifest,
        }

    def register(self, participant, manifest=None):
        """
        Register a single participant.
        """

        registration = self.build_registration(
            participant,
            manifest,
        )

        return self.runtime.register_service(
            registration["record"],
            registration["manifest"],
        )

    def register_all(self, participants, manifest_lookup=None):
        """
        Register multiple participants.
        """

        results = {}

        manifest_lookup = manifest_lookup or {}

        for participant in participants:

            manifest = manifest_lookup.get(
                participant.runtime_identity
            )

            results[participant.runtime_identity] = self.register(
                participant,
                manifest,
            )

        return results