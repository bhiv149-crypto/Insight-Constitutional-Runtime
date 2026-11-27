"""
Shared RFC-7519 HS256 JWT & Policy Security Module for the Insight Ecosystem.

Preserves wire-compatibility with the deployed InsightCore JWT issuer
(iss="sovereign-core", aud="insight-bridge", HS256) and InsightBridge /enforce
policy rules without requiring external PyJWT installation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_scheme = HTTPBearer(auto_error=False)


class JWTError(Exception):
    """Base JWT verification error."""


class TokenExpiredError(JWTError):
    """Raised when token exp claim is in the past."""


class InvalidTokenError(JWTError):
    """Raised when token signature, format, or claims are invalid."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "").strip()
    if not secret:
        raise HTTPException(
            status_code=500,
            detail="JWT_SECRET is not configured; failing closed.",
        )
    return secret


def get_service_token() -> str:
    return (
        os.getenv("INSIGHT_EXECUTION_TOKEN")
        or os.getenv("INSIGHT_AUTH_TOKEN")
        or os.getenv("INSIGHT_ENFORCE_TOKEN")
        or ""
    )


def issue_hs256_jwt(
    client_id: str,
    secret: Optional[str] = None,
    issuer: str = "sovereign-core",
    audience: str = "insight-bridge",
    ttl_seconds: int = 3600,
) -> str:
    """Issue a standard HS256 JWT compatible with InsightCore /auth/issue."""
    signing_key = secret or get_jwt_secret()
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": client_id,
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + ttl_seconds,
    }
    h_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h_b64}.{p_b64}".encode("ascii")
    sig = hmac.new(signing_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{h_b64}.{p_b64}.{_b64url_encode(sig)}"


def decode_hs256_jwt(
    token: str,
    secret: Optional[str] = None,
    expected_audience: Optional[str] = "insight-bridge",
    expected_issuer: Optional[str] = "sovereign-core",
    leeway_seconds: int = 10,
) -> Dict[str, Any]:
    """Decode and verify an HS256 JWT. Fails closed on any tampering, missing exp/iss, or expiry."""
    signing_key = secret or get_jwt_secret()
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("Malformed JWT structure")

    h_b64, p_b64, s_b64 = parts
    try:
        header = json.loads(_b64url_decode(h_b64).decode("utf-8"))
        payload = json.loads(_b64url_decode(p_b64).decode("utf-8"))
        signature = _b64url_decode(s_b64)
    except Exception as exc:
        raise InvalidTokenError(f"Invalid JWT encoding: {exc}") from exc

    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise InvalidTokenError("Invalid JWT header or payload type")

    if header.get("alg") != "HS256":
        raise InvalidTokenError(f"Unsupported JWT algorithm: {header.get('alg')}")

    signing_input = f"{h_b64}.{p_b64}".encode("ascii")
    expected_sig = hmac.new(signing_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise InvalidTokenError("Signature verification failed")

    exp = payload.get("exp")
    if exp is None:
        raise InvalidTokenError("Token missing required 'exp' claim")
    if isinstance(exp, bool) or not isinstance(exp, (int, float)) or time.time() > float(exp) + leeway_seconds:
        raise TokenExpiredError("Token expired")

    if expected_issuer is not None:
        iss = payload.get("iss")
        if iss != expected_issuer:
            raise InvalidTokenError(f"Invalid issuer: {iss}")

    if expected_audience is not None:
        aud = payload.get("aud")
        if aud != expected_audience:
            raise InvalidTokenError(f"Invalid audience: {aud}")

    return payload


def verify_bearer_or_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, Any]:
    """
    Fail-closed authentication dependency for Insight ecosystem services.

    Accepts either:
      1. A valid HS256 JWT issued by InsightCore (aud="insight-bridge"), OR
      2. A configured service-to-service Bearer token (INSIGHT_EXECUTION_TOKEN / INSIGHT_ENFORCE_TOKEN).
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication Required")

    token = credentials.credentials
    configured_service_token = get_service_token()
    if configured_service_token and hmac.compare_digest(token, configured_service_token):
        return {"sub": "service-principal", "auth_type": "service_token"}

    try:
        claims = decode_hs256_jwt(token)
        claims["auth_type"] = "jwt"
        return claims
    except TokenExpiredError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc


def evaluate_policy(client_id: str, resource: str, action: str) -> Tuple[str, str]:
    """
    Deterministic policy evaluation preserved from InsightBridge /enforce.
    """
    if client_id == "guest" and action.lower() in {"write", "execute", "delete"}:
        return "DENY", f"Guest restricted from {action} operations on {resource}"
    return "ALLOW", "Policy matches"
