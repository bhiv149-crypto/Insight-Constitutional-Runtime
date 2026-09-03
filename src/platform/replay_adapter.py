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
    # QCG Verification
    # ---------------------------------------------------------

    def verify_invocation(
        self,
        service_id,
        operation,
        version,
        payload,
        invocation_id,
    ):
        """
        Send the invocation through the live QCG verification pipeline.

        IMPORTANT:
            QCG /qcg/verify is the transition that causes the invocation
            to become visible to the canonical replay authority.

        The HTTP response may be 422 because a later QCG trust stage
        halts the overall verification pipeline.

        Therefore this method DOES NOT treat 422 as a transport failure.
        The caller must inspect the replay stage separately.
        """

        if not invocation_id:
            raise ValueError("invocation_id is required")

        url = f"{self.base_url}/qcg/verify"

        request_payload = {
            "service_id": service_id,
            "operation": operation,
            "version": version,
            "payload": payload,
            "invocation_id": invocation_id,
        }

        response = requests.post(
            url,
            json=request_payload,
            timeout=self.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        try:
            data = response.json()
        except ValueError:
            data = {
                "raw_response": response.text,
            }

        return {
            "http_status": response.status_code,
            "status": (
                "PROCESSED"
                if response.status_code < 500
                else "TRANSPORT_ERROR"
            ),
            "invocation_id": invocation_id,
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
        service_id=None,
        operation=None,
        version="1.0.0",
        payload=None,
    ):
        """
        Validate replay through the canonical QCG pipeline.

        Sequence:

            1. POST /qcg/verify
            2. QCG processes replay
            3. GET /qcg/replay/lineage/{invocation_id}
            4. Return replay validity

        The final replay decision comes from the canonical replay
        authority, not from the HTTP status of /qcg/verify.
        """

        invocation_id = trace_reference or message_id

        if not invocation_id:
            raise ValueError("message_id / invocation_id is required")

        verification = None

        # -----------------------------------------------------
        # Step 1: QCG verification
        # -----------------------------------------------------

        if service_id is not None and operation is not None:
            verification = self.verify_invocation(
                service_id=service_id,
                operation=operation,
                version=version,
                payload=payload or {},
                invocation_id=invocation_id,
            )

        # -----------------------------------------------------
        # Step 2: Canonical replay lineage
        # -----------------------------------------------------

        lineage = self.lookup(invocation_id)

        # -----------------------------------------------------
        # Step 3: Final replay decision
        # -----------------------------------------------------

        replay_valid = False

        if lineage["status"] == "FOUND":
            verdict = lineage["response"].get("verdict", {})
            replay_valid = verdict.get("status") == "VALID"

        return {
            "valid": replay_valid,
            "invocation_id": invocation_id,
            "verification": verification,
            "lineage": lineage,
        }
    
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
        Retrieve the canonical replay sequence number.

        This is intentionally read-only.

        The verification transition must happen before this method
        is called.
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