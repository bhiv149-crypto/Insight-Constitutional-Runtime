import sys
from pathlib import Path

# Add copy of main path to sys.path to locate platform packages
copy_of_main_path = Path("C:/Ganesh_149/Bhiv QCG works/copy of main/bhiv-QCG-main")
if copy_of_main_path.exists() and str(copy_of_main_path) not in sys.path:
    sys.path.insert(0, str(copy_of_main_path))

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