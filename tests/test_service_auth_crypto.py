"""
test_service_auth_crypto.py — Cryptographic Service Authentication & Trust Test Suite

Task ID: ICR-QCG-CRYPTO-ARCH-01
Scope:
  1. Cryptographic Signature Verification (ECDSA-P256, Ed25519, ML-DSA-44, ML-DSA-65, Hybrid).
  2. Deterministic Canonicalization (RFC-8785 & SDK compat).
  3. Trusted Public-Key Registry (Anti-spoofing, key rotation, revocation, expiry).
  4. Replay Attack & Timestamp Clock-Skew Protection.
  5. Dual-Mode Ingress Integration (Bearer Token & Asymmetric Signature paths).
  6. Independent Authorization Enforcement (Separation of auth and privileges).
  7. Negative Security & Attack Scenarios (Key substitution, tampering, replay, downgrade).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

try:
    from cryptography.hazmat.primitives.asymmetric import mldsa
    _MLDSA_AVAILABLE = True
except (ImportError, AttributeError):
    mldsa = None
    _MLDSA_AVAILABLE = False

from fastapi import HTTPException
from insight_execution_service import InvocationRequest, _init_participants, execute
from src.common.service_auth import (
    AuthenticatedPrincipal,
    KeyStatus,
    ReplayProtectionCache,
    TrustLevel,
    TrustedKeyRecord,
    TrustedKeyRegistry,
    authorize_service_operation,
    canonicalize_payload,
    canonicalize_payload_compat,
    get_replay_cache,
    get_trusted_key_registry,
    verify_cryptographic_signature,
    verify_signed_request,
)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Ensure clean registry and replay cache before and after each test."""
    _init_participants()
    reg = get_trusted_key_registry()
    cache = get_replay_cache()
    reg.clear()
    cache.clear()
    yield
    reg.clear()
    cache.clear()


# ---------------------------------------------------------------------------
# 1. Canonicalization Tests
# ---------------------------------------------------------------------------

def test_canonicalize_payload_deterministic():
    """Ensure key order independence and compact representation."""
    d1 = {"z": 1, "a": 2, "m": {"c": 3, "b": 4}}
    d2 = {"a": 2, "m": {"b": 4, "c": 3}, "z": 1}
    assert canonicalize_payload(d1) == canonicalize_payload(d2)
    assert canonicalize_payload(d1) == b'{"a":2,"m":{"b":4,"c":3},"z":1}'


def test_canonicalize_payload_compat():
    """Ensure compatibility mode produces space-separated JSON matching QCG SDK."""
    d = {"service_id": "test", "operation": "execute"}
    compat = canonicalize_payload_compat(d)
    assert b": " in compat or b", " in compat


# ---------------------------------------------------------------------------
# 2. Cryptographic Algorithm Tests
# ---------------------------------------------------------------------------

def test_ecdsa_p256_verification():
    """Verify ECDSA-P256 with DER encoding."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    data = b"canonical-message-001"
    sig = priv.sign(data, ec.ECDSA(hashes.SHA256()))

    assert verify_cryptographic_signature("ECDSA-P256", pub_bytes, data, sig) is True
    # Tampered message
    assert verify_cryptographic_signature("ECDSA-P256", pub_bytes, b"tampered-message", sig) is False
    # Wrong key
    other_pub_bytes = ec.generate_private_key(ec.SECP256R1()).public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    assert verify_cryptographic_signature("ECDSA-P256", other_pub_bytes, data, sig) is False


def test_ed25519_verification():
    """Verify Ed25519 signature."""
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    pub_bytes = pub.public_bytes_raw()
    data = b"ed25519-message-001"
    sig = priv.sign(data)

    assert verify_cryptographic_signature("Ed25519", pub_bytes, data, sig) is True
    assert verify_cryptographic_signature("Ed25519", pub_bytes, b"tampered-data", sig) is False


@pytest.mark.skipif(not _MLDSA_AVAILABLE, reason="ML-DSA not supported in this cryptography build")
def test_mldsa_44_verification():
    """Verify Post-Quantum ML-DSA-44 (NIST FIPS 204)."""
    priv = mldsa.MLDSA44PrivateKey.generate()
    pub = priv.public_key()
    pub_bytes = pub.public_bytes_raw()
    data = b"mldsa-post-quantum-workload"
    sig = priv.sign(data)

    assert verify_cryptographic_signature("ML-DSA-44", pub_bytes, data, sig) is True
    assert verify_cryptographic_signature("ML-DSA-44", pub_bytes, b"tampered-pqc-workload", sig) is False


@pytest.mark.skipif(not _MLDSA_AVAILABLE, reason="ML-DSA not supported in this cryptography build")
def test_mldsa_65_verification():
    """Verify Post-Quantum ML-DSA-65 (NIST FIPS 204)."""
    priv = mldsa.MLDSA65PrivateKey.generate()
    pub = priv.public_key()
    pub_bytes = pub.public_bytes_raw()
    data = b"mldsa-65-post-quantum-workload"
    sig = priv.sign(data)

    assert verify_cryptographic_signature("ML-DSA-65", pub_bytes, data, sig) is True
    assert verify_cryptographic_signature("ML-DSA-65", pub_bytes, b"tampered", sig) is False


@pytest.mark.skipif(not _MLDSA_AVAILABLE, reason="ML-DSA not supported in this cryptography build")
def test_hybrid_ecdsa_mldsa_verification():
    """Verify Composite Hybrid ECDSA + ML-DSA dual signature."""
    ec_priv = ec.generate_private_key(ec.SECP256R1())
    ec_pub = ec_priv.public_key()
    ec_pub_bytes = ec_pub.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    ml_priv = mldsa.MLDSA44PrivateKey.generate()
    ml_pub = ml_priv.public_key()
    ml_pub_bytes = ml_pub.public_bytes_raw()

    data = b"hybrid-payload-quantum-classical"
    sig_ec = ec_priv.sign(data, ec.ECDSA(hashes.SHA256()))
    sig_ml = ml_priv.sign(data)

    comb_pub = len(ec_pub_bytes).to_bytes(4, "big") + ec_pub_bytes + len(ml_pub_bytes).to_bytes(4, "big") + ml_pub_bytes
    comb_sig = len(sig_ec).to_bytes(4, "big") + sig_ec + len(sig_ml).to_bytes(4, "big") + sig_ml

    assert verify_cryptographic_signature("HYBRID-ECDSA-MLDSA", comb_pub, data, comb_sig) is True

    # Tampered EC sig
    tampered_sig = len(sig_ec).to_bytes(4, "big") + b"x"*len(sig_ec) + len(sig_ml).to_bytes(4, "big") + sig_ml
    assert verify_cryptographic_signature("HYBRID-ECDSA-MLDSA", comb_pub, data, tampered_sig) is False


def test_unsupported_algorithm_fails_closed():
    """Ensure unsupported algorithms fail closed safely."""
    assert verify_cryptographic_signature("UNKNOWN_ALG", b"pub", b"data", b"sig") is False


# ---------------------------------------------------------------------------
# 3. Trusted Public-Key Registry & Anti-Spoofing Tests
# ---------------------------------------------------------------------------

def test_trusted_key_registry_lifecycle():
    """Test key registration, lookup, expiry, and revocation."""
    reg = TrustedKeyRegistry()
    pub_bytes = b"sample-ec-pub-bytes-001"

    record = TrustedKeyRecord(
        service_id="tantra.platform.sdk",
        key_id="k-2026-v1",
        public_key_bytes=pub_bytes,
        algorithm="ECDSA-P256",
        trust_level=TrustLevel.CLASSICAL.value,
        status=KeyStatus.ACTIVE.value,
    )
    reg.register_key(record)

    # Lookup
    found = reg.get_key("tantra.platform.sdk", "k-2026-v1")
    assert found is not None
    assert found.public_key_bytes == pub_bytes

    # Revocation
    assert reg.revoke_key("tantra.platform.sdk", "k-2026-v1") is True
    valid, reason = reg.get_key("tantra.platform.sdk", "k-2026-v1").is_valid()
    assert valid is False
    assert "REVOKED" in reason

    # Expiry
    expired_record = TrustedKeyRecord(
        service_id="qcg.gateway",
        key_id="k-expired",
        public_key_bytes=b"pub",
        algorithm="ECDSA-P256",
        trust_level=TrustLevel.CLASSICAL.value,
        expires_at=time.time() - 10,
    )
    reg.register_key(expired_record)
    valid, reason = reg.get_key("qcg.gateway", "k-expired").is_valid()
    assert valid is False
    assert "expired" in reason


def test_public_key_substitution_attack_rejection():
    """Prevent caller from injecting their own key to spoof a registered service."""
    reg = get_trusted_key_registry()
    real_priv = ec.generate_private_key(ec.SECP256R1())
    real_pub_bytes = real_priv.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    # Legitimate key registered
    reg.register_key(TrustedKeyRecord(
        service_id="trusted.service.v1",
        key_id="real-key",
        public_key_bytes=real_pub_bytes,
        algorithm="ECDSA-P256",
        trust_level="CLASSICAL"
    ))

    # Attacker generates fake key and attempts to sign as 'trusted.service.v1'
    fake_priv = ec.generate_private_key(ec.SECP256R1())
    fake_pub_bytes = fake_priv.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    body = {"invocation_id": "spoof-test-1", "operation": "execute", "payload": {}}
    fake_sig = fake_priv.sign(canonicalize_payload(body), ec.ECDSA(hashes.SHA256()))

    headers = {
        "X-Service-ID": "trusted.service.v1",
        "X-Service-KeyID": "real-key",
        "X-Service-Signature": fake_sig.hex(),
        "X-Service-PublicKey": fake_pub_bytes.hex(),
        "X-Trust-Level": "CLASSICAL",
    }

    with pytest.raises(HTTPException) as exc:
        verify_signed_request(headers, body)
    assert exc.value.status_code == 403
    assert "Public key mismatch" in exc.value.detail


# ---------------------------------------------------------------------------
# 4. Replay Protection & Timestamp Tests
# ---------------------------------------------------------------------------

def test_replay_protection_duplicate_nonce():
    """Reject requests with duplicate invocation IDs."""
    cache = ReplayProtectionCache(ttl_seconds=60)
    ok, _ = cache.check_and_record("nonce-100")
    assert ok is True

    # Immediate replay
    ok2, reason = cache.check_and_record("nonce-100")
    assert ok2 is False
    assert "Replay detected" in reason


def test_timestamp_clock_skew_tolerance():
    """Reject timestamps outside allowable clock skew window."""
    cache = ReplayProtectionCache(max_skew_seconds=300)
    now = time.time()

    # Within tolerance (+60s)
    ok, _ = cache.check_and_record("n1", str(now + 60))
    assert ok is True

    # Excessive past skew (10 minutes ago)
    ok_past, reason_past = cache.check_and_record("n2", str(now - 600))
    assert ok_past is False
    assert "skew exceeds" in reason_past

    # Excessive future skew (+10 minutes)
    ok_future, reason_future = cache.check_and_record("n3", str(now + 600))
    assert ok_future is False
    assert "skew exceeds" in reason_future


# ---------------------------------------------------------------------------
# 5. End-to-End Dual-Mode Execution Tests
# ---------------------------------------------------------------------------

def test_execution_service_bearer_token_mode():
    """Verify legacy Bearer token succeeds on POST /api/v1/execute."""
    req = InvocationRequest(
        service_id="insightflow.runtime.intelligence.v1",
        operation="execute",
        payload={"test": "flow_bearer"},
        version="1.0.2",
        invocation_id="test-bearer-flow-1"
    )
    coro = execute(req, "test-legacy-bearer-token")
    try:
        coro.send(None)
    except StopIteration as exc:
        res = exc.value
        assert res.status_code == 200
        body = json.loads(res.body.decode())
        assert body["status"] == "SUCCESS"
        assert body["evidence"]["trust_method"] == "CLASSICAL"
        assert body["evidence"]["auth_type"] == "bearer_token"


def test_execution_service_asymmetric_ecdsa_mode():
    """Verify QCG SDK asymmetric ECDSA signature succeeds on /api/v1/execute."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    req_body = {
        "service_id": "insightbridge.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": "bridge_ecdsa"},
        "version": "1.0.2",
        "invocation_id": "test-bridge-ecdsa-1"
    }
    sig = priv.sign(canonicalize_payload(req_body), ec.ECDSA(hashes.SHA256()))

    headers = {
        "X-Service-ID": "tantra.platform.sdk",
        "X-Service-Signature": sig.hex(),
        "X-Service-PublicKey": pub_bytes.hex(),
        "X-Trust-Level": "CLASSICAL",
    }

    principal = verify_signed_request(headers, req_body)
    assert principal.auth_type == "asymmetric_signature"
    assert principal.trust_level == "CLASSICAL"

    req = InvocationRequest(**req_body)
    coro = execute(req, principal)
    try:
        coro.send(None)
    except StopIteration as exc:
        res = exc.value
        assert res.status_code == 200
        body = json.loads(res.body.decode())
        assert body["status"] == "SUCCESS"
        assert body["evidence"]["trust_method"] == "CLASSICAL"
        assert body["evidence"]["auth_type"] == "asymmetric_signature"
        assert body["evidence"]["principal_service"] == "tantra.platform.sdk"


@pytest.mark.skipif(not _MLDSA_AVAILABLE, reason="ML-DSA not supported in this cryptography build")
def test_execution_service_asymmetric_mldsa_mode():
    """Verify Post-Quantum ML-DSA-44 signature succeeds on /api/v1/execute."""
    priv = mldsa.MLDSA44PrivateKey.generate()
    pub = priv.public_key()
    pub_bytes = pub.public_bytes_raw()

    req_body = {
        "service_id": "insightcore.runtime.intelligence.v1",
        "operation": "execute",
        "payload": {"test": "core_pqc"},
        "version": "1.0.2",
        "invocation_id": "test-core-pqc-1"
    }
    sig = priv.sign(canonicalize_payload(req_body))

    reg = get_trusted_key_registry()
    reg.register_key(TrustedKeyRecord(
        service_id="qcg.quantum.gateway.v1",
        key_id="pqc-k1",
        public_key_bytes=pub_bytes,
        algorithm="ML-DSA-44",
        trust_level=TrustLevel.POST_QUANTUM.value,
    ))

    headers = {
        "X-Service-ID": "qcg.quantum.gateway.v1",
        "X-Service-KeyID": "pqc-k1",
        "X-Service-Signature": sig.hex(),
        "X-Service-PublicKey": pub_bytes.hex(),
        "X-Trust-Level": "POST_QUANTUM",
    }

    principal = verify_signed_request(headers, req_body)
    assert principal.trust_level == "POST_QUANTUM"

    req = InvocationRequest(**req_body)
    coro = execute(req, principal)
    try:
        coro.send(None)
    except StopIteration as exc:
        res = exc.value
        assert res.status_code == 200
        body = json.loads(res.body.decode())
        assert body["status"] == "SUCCESS"
        assert body["evidence"]["trust_method"] == "POST_QUANTUM"
        assert body["evidence"]["auth_type"] == "asymmetric_signature"


def test_authorization_separation():
    """Verify that permissions are restricted by service permissions, not X-Trust-Level."""
    reg = get_trusted_key_registry()
    reg.register_key(TrustedKeyRecord(
        service_id="read.only.service",
        key_id="k1",
        public_key_bytes=b"pub",
        algorithm="ECDSA-P256",
        trust_level=TrustLevel.QUANTUM.value, # Claims high trust level!
        allowed_operations={"health"}, # But only allowed 'health'
    ))

    principal = AuthenticatedPrincipal(
        service_id="read.only.service",
        key_id="k1",
        auth_type="asymmetric_signature",
        trust_level="QUANTUM",
    )

    # 'health' is authorized
    ok, _ = authorize_service_operation(principal, "any.service", "health")
    assert ok is True

    # 'execute' is denied despite claiming QUANTUM trust
    ok, reason = authorize_service_operation(principal, "any.service", "execute")
    assert ok is False
    assert "not permitted" in reason
