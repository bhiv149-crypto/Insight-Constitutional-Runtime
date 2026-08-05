"""
Platform Replay Adapter

Thin wrapper around the Constitutional Runtime Replay system.

Insight Runtime does not implement replay logic.
It delegates replay validation to the Platform Runtime.
"""

from src.platform.imports import (
    ReplayRegistry,
    CanonicalReplayAuthority,
)


class PlatformReplayAdapter:
    """
    Thin wrapper around Platform Replay services.
    """

    def __init__(self, registry=None, authority=None):
        self.registry = registry or ReplayRegistry(
            path="replay_registry.json",
            ttl_seconds=300.0,
        )

        self.authority = authority or CanonicalReplayAuthority(
            registry=self.registry
        )

    def submit(
        self,
        message_id,
        issued_at,
        trace_reference,
    ):
        """
        Submit a message for replay validation.
        """
        return self.authority.submit(
            message_id=message_id,
            issued_at=issued_at,
            trace_reference=trace_reference,
        )

    def validate(
        self,
        message_id,
        issued_at,
        trace_reference,
    ):
        """
        Convenience wrapper.
        """
        verdict = self.submit(
            message_id,
            issued_at,
            trace_reference,
        )

        return verdict.is_valid

    def get_sequence(
        self,
        message_id,
        issued_at,
        trace_reference,
    ):
        """
        Return replay sequence number.
        """
        verdict = self.submit(
            message_id,
            issued_at,
            trace_reference,
        )

        return verdict.sequence_number