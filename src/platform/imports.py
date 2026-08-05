"""
Central Platform imports.

During development, fallback to local stub implementations when the
official Platform Runtime packages are unavailable.

Replace these imports with the official Platform Runtime packages
during integration.
"""
try:
    from quantum_trust_provider import create_trust_provider

    from replay_registry import ReplayRegistry
    from canonical_replay_authority import CanonicalReplayAuthority

    from platform_capability_sdk import PlatformCapabilitySDK

    from observability import TraceStore

    from platform_service_registry import (
        PlatformServiceRegistry,
        PlatformServiceRecord,
        CapabilityManifest,
        OperationContract,
    )

except ModuleNotFoundError:

    from .stubs import (
        PlatformCapabilitySDK,
        PlatformServiceRegistry,
        PlatformServiceRecord,
        CapabilityManifest,
        OperationContract,
        ReplayRegistry,
        CanonicalReplayAuthority,
        create_trust_provider,
        TraceStore,
    )