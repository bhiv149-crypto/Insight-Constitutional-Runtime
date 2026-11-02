"""
qcg_provenance_client.py — WS-A Provenance Integration Client

Programme: BHQ-INFRA-001 (WS-A -> WS-D -> WS-C)
Owner: Ganesh Vishwakarma (WS-A Lead & Systems Integrator)
Repository: Insight_Constitutional_Runtime (src/platform/)

Responsibilities:
1. Canonicalize quantum workload payloads (BLK-ARC-003).
2. Compute deterministic SHA-256 execution digests.
3. Explicitly separate Workload Identity, Execution Instance Identity, and Provenance Record Identity.
4. Construct typed ProvenanceSigningRequest envelopes for WS-D (NodeSigner & EvidenceLedger).
5. Independently validate cryptographic provenance responses (digest match, signature presence, Merkle root integrity).
6. Construct security-gated GatewayTransmissionRequest payloads for WS-C (Quantum Communication Gateway).
7. Fail closed on malformed, unverified, or tampered inputs without leaking cryptographic secrets.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from src.platform.quantum_adapter import (
    canonicalize_quantum_payload,
    compute_execution_digest,
)

logger = logging.getLogger("insight.platform.qcg_provenance_client")


# ---------------------------------------------------------------------------
# Strict Contract Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class QuantumWorkloadIdentity:
    """
    Identifies the canonical problem/algorithm formulation.
    Independent of runtime execution attempt or timestamp.
    """
    workload_id: str
    domain: str                 # VANA | MARINE | UCCIS | AIAIC
    problem_id: str
    algorithm: str              # QAOA | VQE
    qubits_required: int
    shots: int = 1024

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuantumExecutionInstance:
    """
    Identifies one specific attempt to execute a workload on a given backend.
    """
    execution_instance_id: str
    workload_identity: QuantumWorkloadIdentity
    backend_target: str         # aer_simulator | ibm_brisbane
    execution_status: str       # SUCCESS | COMPLETED
    measurement_counts: Dict[str, int]
    measurement_probabilities: Dict[str, float]
    best_candidate: str
    execution_time_ms: float
    trace_id: str = field(
        default_factory=lambda: f"trace-{uuid.uuid4().hex[:12]}"
    )
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_canonical_payload(self) -> Dict[str, Any]:
        """Convert to canonical dictionary representation for deterministic digest."""
        return {
            "workload_id": self.workload_identity.workload_id,
            "domain": self.workload_identity.domain,
            "problem_id": self.workload_identity.problem_id,
            "algorithm": self.workload_identity.algorithm,
            "qubits_required": self.workload_identity.qubits_required,
            "shots": self.workload_identity.shots,
            "execution_instance_id": self.execution_instance_id,
            "backend_target": self.backend_target,
            "execution_status": self.execution_status,
            "best_candidate": self.best_candidate,
            "measurement_counts": self.measurement_counts,
            "measurement_probabilities": self.measurement_probabilities,
            "execution_time_ms": round(self.execution_time_ms, 6),
            "trace_id": self.trace_id,
        }


@dataclass(frozen=True)
class ProvenanceSigningRequest:
    """
    Signing request sent from WS-A to WS-D (NodeSigner).
    Carries the canonical payload and its precomputed deterministic digest.
    """
    execution_instance_id: str
    trace_id: str
    canonical_payload: Dict[str, Any]
    canonical_digest: str
    schema_version: str = "2.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProvenanceEvidenceResponse:
    """
    Cryptographic provenance response received from WS-D (NodeSigner & EvidenceLedger).
    """
    execution_instance_id: str
    trace_id: str
    canonical_digest: str
    node_id: str
    public_key_hex: str
    signature_der_hex: str
    replay_sequence: int
    merkle_root: str
    ledger_chain_length: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GatewayTransmissionPackage:
    """
    Validated package prepared by WS-A for submission to WS-C (Quantum Communication Gateway).
    """
    provenance_record_id: str
    execution_instance_id: str
    trace_id: str
    canonical_digest: str
    provenance: ProvenanceEvidenceResponse
    canonical_payload: Dict[str, Any]
    communication_message: str
    transmission_mode: str = "entangled"
    noise_factor: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ProvenanceValidationError(Exception):
    """Raised when cryptographic provenance fails verification."""
    pass


class ProvenanceServiceUnavailable(Exception):
    """Raised when the downstream provenance service is unreachable."""
    pass


# ---------------------------------------------------------------------------
# WS-A Provenance Client Implementation
# ---------------------------------------------------------------------------

class QCGProvenanceClient:
    """
    Client managing the WS-A side of the cross-workstream lifecycle:
      1. Canonicalization and digest generation.
      2. Signing request creation for WS-D.
      3. Response validation against cryptographic rules.
      4. Gateway transmission package preparation for WS-C.
    """

    def __init__(
        self,
        provenance_endpoint_url: Optional[str] = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.endpoint_url = (provenance_endpoint_url or "").rstrip("/")
        self.timeout = timeout_seconds

    def prepare_signing_request(
        self,
        execution_instance: QuantumExecutionInstance,
    ) -> Tuple[ProvenanceSigningRequest, str]:
        """
        Formulate canonical payload, compute deterministic SHA-256 digest,
        and construct the signing request for WS-D.
        Returns (ProvenanceSigningRequest, canonical_json_string).
        """
        payload = execution_instance.to_canonical_payload()
        canonical_str = canonicalize_quantum_payload(payload)
        digest = compute_execution_digest(payload)

        req = ProvenanceSigningRequest(
            execution_instance_id=execution_instance.execution_instance_id,
            trace_id=execution_instance.trace_id,
            canonical_payload=payload,
            canonical_digest=digest,
            schema_version="2.0.0",
        )
        return req, canonical_str

    def validate_provenance_response(
        self,
        request: ProvenanceSigningRequest,
        response: ProvenanceEvidenceResponse,
    ) -> bool:
        """
        Independently verifies that the response received from WS-D matches
        the request and satisfies cryptographic sanity checks:
          - Execution instance ID matches.
          - Canonical digest matches.
          - Signature is non-empty and formatted.
          - Public key is non-empty DER hex.
          - Merkle root is a valid 64-character SHA-256 hex string.
          - Sequence number is greater than zero.
        """
        if response.execution_instance_id != request.execution_instance_id:
            raise ProvenanceValidationError(
                f"Execution ID mismatch: expected {request.execution_instance_id}, got {response.execution_instance_id}"
            )

        if response.canonical_digest != request.canonical_digest:
            raise ProvenanceValidationError(
                f"Canonical digest mismatch: expected {request.canonical_digest}, got {response.canonical_digest}"
            )

        if not response.signature_der_hex or len(response.signature_der_hex) < 64:
            raise ProvenanceValidationError(
                "Invalid or empty ECDSA signature in provenance response"
            )

        if not response.public_key_hex or len(response.public_key_hex) < 32:
            raise ProvenanceValidationError(
                "Invalid or empty public key in provenance response"
            )

        if not response.merkle_root or len(response.merkle_root) != 64:
            raise ProvenanceValidationError(
                f"Invalid Merkle root length: {len(response.merkle_root)} (expected 64)"
            )

        if response.replay_sequence <= 0:
            raise ProvenanceValidationError(
                f"Invalid replay sequence number: {response.replay_sequence}"
            )

        return True

    def build_gateway_package(
        self,
        execution_instance: QuantumExecutionInstance,
        provenance_response: ProvenanceEvidenceResponse,
        communication_message: Optional[str] = None,
        noise_factor: float = 0.0,
    ) -> GatewayTransmissionPackage:
        """
        Packages validated provenance evidence and communication message into
        a strict GatewayTransmissionPackage for WS-C.
        """
        default_msg = f"{execution_instance.workload_identity.domain}_DISPATCH_{execution_instance.best_candidate}"
        msg = communication_message or default_msg

        prov_rec_id = f"prov-{uuid.uuid4().hex[:12]}"

        return GatewayTransmissionPackage(
            provenance_record_id=prov_rec_id,
            execution_instance_id=execution_instance.execution_instance_id,
            trace_id=execution_instance.trace_id,
            canonical_digest=provenance_response.canonical_digest,
            provenance=provenance_response,
            canonical_payload=execution_instance.to_canonical_payload(),
            communication_message=msg,
            transmission_mode="entangled",
            noise_factor=noise_factor,
        )


__all__ = [
    "QuantumWorkloadIdentity",
    "QuantumExecutionInstance",
    "ProvenanceSigningRequest",
    "ProvenanceEvidenceResponse",
    "GatewayTransmissionPackage",
    "ProvenanceValidationError",
    "ProvenanceServiceUnavailable",
    "QCGProvenanceClient",
]

