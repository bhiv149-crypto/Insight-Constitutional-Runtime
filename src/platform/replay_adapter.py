"""
Platform Replay Adapter

Thin wrapper around the live QCG Constitutional Runtime Replay API.

Insight Runtime does not implement replay logic.
Replay authority remains owned by the Platform/QCG Runtime.

This adapter only communicates with the live replay API and does
not maintain a local replay registry.
"""

import requests


class PlatformReplayAdapter:
    """
    Adapter for the live Platform/QCG Replay Authority.

    The adapter does not own replay state.
    It queries the canonical replay authority exposed by QCG.
    """

    DEFAULT_BASE_URL = "https://bhiv-qcg.onrender.com"

    def __init__(self, base_url=None, timeout=10):
        self.base_url = (
            base_url or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout

    # ---------------------------------------------------------
    # Live Replay Lineage
    # ---------------------------------------------------------

    def lookup(self, trace_id):
        """
        Retrieve replay lineage from the live QCG replay authority.

        This is a read operation. It does not create replay state.
        """

        if not trace_id:
            raise ValueError("trace_id is required")

        url = f"{self.base_url}/qcg/replay/lineage/{trace_id}"

        response = requests.get(
            url,
            timeout=self.timeout,
            headers={
                "Accept": "application/json",
            },
        )

        if response.status_code == 404:
            return {
                "status": "NOT_FOUND",
                "trace_id": trace_id,
                "http_status": 404,
                "response": response.json(),
            }

        response.raise_for_status()

        data = response.json()

        return {
            "status": "FOUND",
            "trace_id": trace_id,
            "http_status": response.status_code,
            "response": data,
        }

    # ---------------------------------------------------------
    # Replay Validation
    # ---------------------------------------------------------

    def validate(
        self,
        message_id,
        issued_at=None,
        trace_reference=None,
    ):
        """
        Validate replay state using the live QCG replay lineage API.

        Note:
            The live lineage endpoint is a lookup endpoint.
            It does not submit a new replay event.

        Returns True only when a replay record is found.
        """

        trace_id = trace_reference or message_id

        result = self.lookup(trace_id)

        return result["status"] == "FOUND"

    # ---------------------------------------------------------
    # Replay Sequence
    # ---------------------------------------------------------

    def get_sequence(
        self,
        message_id,
        issued_at=None,
        trace_reference=None,
    ):
        """
        Retrieve the canonical replay sequence number
        from the live QCG replay authority.
        """

        trace_id = trace_reference or message_id

        result = self.lookup(trace_id)

        if result["status"] != "FOUND":
            return None

        verdict = result["response"].get("verdict", {})

        return verdict.get("sequence_number")

    # ---------------------------------------------------------
    # Raw Replay Verdict
    # ---------------------------------------------------------

    def get_verdict(self, trace_id):
        """
        Return the complete canonical replay verdict
        returned by the live QCG runtime.
        """

        result = self.lookup(trace_id)

        if result["status"] != "FOUND":
            return result

        return result["response"].get("verdict")