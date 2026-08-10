"""
Platform Runtime Imports
========================
Loads the official PlatformCapabilitySDK from Kanishk's Platform Runtime
repository (bhiv-QCG-main).

Strategy
--------
1.  Attempt to inject the bhiv-QCG-main directory into sys.path and import
    the official PlatformCapabilitySDK directly from there.
2.  If the path is unavailable, fall back to the local development stubs
    with an explicit warning — this should only occur in offline environments.

Replay and Telemetry
--------------------
The live CanonicalReplayAuthority and TraceStore are implemented here as
thin in-process classes that mirror the expected SDK contracts without
duplicating Platform Runtime logic.
"""

import sys
import logging
import hashlib
import json
import threading
import time
import uuid
from pathlib import Path

logger = logging.getLogger("insight.platform.imports")

# ---------------------------------------------------------------------------
# Locate the official SDK from the peer repository
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[4]  # C:\Ganesh_149\Bhiv QCG works\
_SDK_DIR = _REPO_ROOT / "copy of main" / "bhiv-QCG-main"
_SDK_AVAILABLE = False

if _SDK_DIR.exists() and str(_SDK_DIR) not in sys.path:
    sys.path.insert(0, str(_SDK_DIR))
    logger.info(f"Platform SDK path registered: {_SDK_DIR}")

try:
    from platform_capability_sdk import PlatformCapabilitySDK
    from quantum_trust_provider import create_trust_provider
    
    # Monkey-patch Kanishk's PlatformCapabilitySDK.get_service because the live Platform Registry
    # drops the "execution" key, causing the SDK to fallback to the discovery endpoint.
    _orig_get_service = PlatformCapabilitySDK.get_service
    def _patched_get_service(self, service_id, *args, **kwargs):
        svc = _orig_get_service(self, service_id, *args, **kwargs)
        if svc and "endpoints" in svc and "execute" in svc["endpoints"]:
            svc["endpoints"]["execution"] = svc["endpoints"]["execute"]
        return svc
    PlatformCapabilitySDK.get_service = _patched_get_service

    _SDK_AVAILABLE = True
    logger.info("Live PlatformCapabilitySDK loaded from bhiv-QCG-main and patched for execution.")
except ImportError as _exc:
    logger.warning(
        f"Official PlatformCapabilitySDK not available ({_exc}). "
        "Falling back to development stubs. Integration will be limited."
    )
    from .stubs import PlatformCapabilitySDK, create_trust_provider

# ---------------------------------------------------------------------------
# Stubs for registry types (not required in the live invocation path)
# ---------------------------------------------------------------------------
from .stubs import (
    PlatformServiceRegistry,
    PlatformServiceRecord,
    CapabilityManifest,
    OperationContract,
)

# ---------------------------------------------------------------------------
# Live Replay Authority
# ---------------------------------------------------------------------------

class _LiveReplayRegistry:
    """
    In-process replay deduplication store.

    Tracks submitted message_ids with their first-seen timestamp.
    Provides sequence numbers for ordering.
    TTL-based expiry prevents unbounded growth.
    """

    def __init__(self, ttl_seconds: float = 300.0):
        self._store: dict = {}      # message_id -> {"ts": float, "seq": int}
        self._sequence: int = 0
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def _evict_expired(self):
        now = time.time()
        expired = [k for k, v in self._store.items() if now - v["ts"] > self._ttl]
        for k in expired:
            del self._store[k]

    def check_and_register(self, message_id: str) -> dict:
        with self._lock:
            self._evict_expired()
            if message_id in self._store:
                entry = self._store[message_id]
                return {
                    "is_duplicate": True,
                    "sequence": entry["seq"],
                    "first_seen": entry["ts"],
                }
            self._sequence += 1
            self._store[message_id] = {"ts": time.time(), "seq": self._sequence}
            return {
                "is_duplicate": False,
                "sequence": self._sequence,
                "first_seen": self._store[message_id]["ts"],
            }


class _LiveReplayVerdict:
    """Replay submission result."""
    def __init__(self, is_valid, sequence_number, status, reason=""):
        self.is_valid = is_valid
        self.sequence_number = sequence_number
        self.status = status
        self.reason = reason

    def to_dict(self):
        return {
            "status": self.status,
            "sequence": self.sequence_number,
            "reason": self.reason,
            "is_valid": self.is_valid,
        }


class _LiveReplayAuthority:
    """
    Live CanonicalReplayAuthority implementation.

    Accepts first submission of a message_id as VALID.
    Rejects subsequent submissions of the same message_id within TTL as DUPLICATE.
    """

    def __init__(self, registry=None):
        self.registry = registry or _LiveReplayRegistry()

    def submit(self, message_id, issued_at, trace_reference):
        result = self.registry.check_and_register(message_id)
        if result["is_duplicate"]:
            return _LiveReplayVerdict(
                is_valid=False,
                sequence_number=result["sequence"],
                status="DUPLICATE",
                reason=f"Message '{message_id}' already processed (seq={result['sequence']}).",
            )
        return _LiveReplayVerdict(
            is_valid=True,
            sequence_number=result["sequence"],
            status="VALID",
            reason="",
        )


class _LiveReplayRegistryCompat:
    """Compat wrapper so existing adapter code works unchanged."""
    def __init__(self, path=None, ttl_seconds=300.0):
        self._impl = _LiveReplayRegistry(ttl_seconds=ttl_seconds)

    def check_and_register(self, message_id):
        return self._impl.check_and_register(message_id)


# Public names expected by replay_adapter.py
ReplayRegistry = _LiveReplayRegistryCompat
CanonicalReplayAuthority = _LiveReplayAuthority

# ---------------------------------------------------------------------------
# Live Trace Store
# ---------------------------------------------------------------------------

class _LiveTraceStore:
    """
    In-process telemetry trace store.

    Accumulates execution traces, contract lineage and adapter traces
    as an ordered list for replay reconstruction and export.
    """

    def __init__(self):
        self._traces: list = []
        self._sequence: int = 0
        self._lock = threading.Lock()

    def _next_seq(self) -> int:
        self._sequence += 1
        return self._sequence

    def record_execution_trace(self, trace_id, participant, operation, metadata=None):
        with self._lock:
            entry = {
                "trace_id": trace_id,
                "type": "execution_trace",
                "participant": participant,
                "operation": operation,
                "metadata": metadata or {},
                "sequence": self._next_seq(),
                "timestamp": time.time(),
                "status": "RECORDED",
            }
            self._traces.append(entry)
            return entry

    def record_contract_lineage(self, contract_id, parent_contract=None, metadata=None):
        with self._lock:
            entry = {
                "trace_id": contract_id,
                "type": "contract_lineage",
                "contract_id": contract_id,
                "parent_contract": parent_contract,
                "metadata": metadata or {},
                "sequence": self._next_seq(),
                "timestamp": time.time(),
                "status": "RECORDED",
            }
            self._traces.append(entry)
            return entry

    def record_adapter_trace(self, adapter, action, metadata=None):
        with self._lock:
            entry = {
                "trace_id": f"adapter-{uuid.uuid4().hex[:8]}",
                "type": "adapter_trace",
                "adapter": adapter,
                "action": action,
                "metadata": metadata or {},
                "sequence": self._next_seq(),
                "timestamp": time.time(),
                "status": "RECORDED",
            }
            self._traces.append(entry)
            return entry

    def reconstruct_replay(self, trace_id):
        with self._lock:
            matching = [t for t in self._traces if t.get("trace_id") == trace_id]
            return {
                "trace_id": trace_id,
                "status": "AVAILABLE" if matching else "NOT_FOUND",
                "records": matching,
            }

    def export_opentelemetry(self, trace_id):
        with self._lock:
            matching = [t for t in self._traces if t.get("trace_id") == trace_id]
            return {
                "trace_id": trace_id,
                "exported": True,
                "provider": "OpenTelemetry-Compatible",
                "records": matching,
            }

    def get_all(self):
        with self._lock:
            return list(self._traces)


TraceStore = _LiveTraceStore
