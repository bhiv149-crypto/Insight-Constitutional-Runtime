"""
Insight Platform Runtime Imports

This module exposes the canonical Platform Runtime interfaces
required by Insight.

IMPORTANT:

- The copied bhiv-QCG-main repository is NOT loaded.
- No sys.path modification is performed.
- No local Platform Runtime is created.
- No SDK monkey-patching is performed.
- No parallel registry is implemented here.
- Live execution requires the canonical Platform SDK to be
  installed as a real dependency.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("insight.platform.imports")


# ---------------------------------------------------------------------------
# Canonical Platform SDK
# ---------------------------------------------------------------------------

try:
    from tantra_platform_sdk import (
        PlatformCapabilitySDK,
    )
except ImportError as exc:
    PlatformCapabilitySDK = None

    _SDK_IMPORT_ERROR = exc

    logger.error(
        "Canonical PlatformCapabilitySDK is not installed. "
        "Live Platform Runtime integration cannot execute until "
        "the official SDK dependency is installed."
    )
else:
    _SDK_IMPORT_ERROR = None


# ---------------------------------------------------------------------------
# Quantum trust provider
# ---------------------------------------------------------------------------

try:
    from tantra_platform_sdk._trust import (
        create_trust_provider,
    )
except ImportError as exc:
    create_trust_provider = None
    _TRUST_PROVIDER_IMPORT_ERROR = exc

    logger.warning(
        "Canonical SDK trust-provider functionality is unavailable."
    )
else:
    _TRUST_PROVIDER_IMPORT_ERROR = None

# ---------------------------------------------------------------------------
# Development-only registry data models
# ---------------------------------------------------------------------------
#
# These are metadata/data structures used by existing Insight-side code.
# They are NOT a Platform Runtime and MUST NOT be used as a live registry.
#

from .stubs import (
    PlatformServiceRegistry,
    PlatformServiceRecord,
    CapabilityManifest,
    OperationContract,
    ReplayRegistry,
    CanonicalReplayAuthority,
    TraceStore,
)


# ---------------------------------------------------------------------------
# Canonical SDK availability helpers
# ---------------------------------------------------------------------------

def require_platform_sdk():
    """
    Return the canonical PlatformCapabilitySDK.

    Raises a clear error if the official SDK is not installed.

    This prevents accidental execution through development stubs
    or the copied QCG repository.
    """

    if PlatformCapabilitySDK is None:
        raise RuntimeError(
            "Canonical PlatformCapabilitySDK is unavailable. "
            "Install the official Platform Runtime SDK dependency "
            "before attempting live runtime integration."
        ) from _SDK_IMPORT_ERROR

    return PlatformCapabilitySDK


def require_trust_provider():
    """
    Return the canonical quantum trust-provider factory.

    Raises a clear error if unavailable.
    """

    if create_trust_provider is None:
        raise RuntimeError(
            "Canonical quantum_trust_provider is unavailable. "
            "Install the required Platform/Quantum trust dependency."
        ) from _TRUST_PROVIDER_IMPORT_ERROR

    return create_trust_provider


def is_platform_sdk_available() -> bool:
    """
    Return whether the canonical Platform SDK is installed.
    """

    return PlatformCapabilitySDK is not None


def is_trust_provider_available() -> bool:
    """
    Return whether the canonical trust provider is installed.
    """

    return create_trust_provider is not None