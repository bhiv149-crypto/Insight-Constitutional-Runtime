"""
Platform Runtime configuration.

Values mirror the Platform Runtime configuration and may be
overridden during deployment.
"""
from dotenv import load_dotenv

load_dotenv()

from src.platform.imports import create_trust_provider

# Discovery — Live BHIV Platform Runtime
DISCOVERY_URLS = [
    "https://bhiv-qcg.onrender.com/registry",
]

DISCOVERY_PORT_BASE = 9010
DISCOVERY_NODE_COUNT = 3

# Registry
REGISTRY_HOST = "bhiv-qcg.onrender.com"
REGISTRY_PORT = 443

# Replay
REPLAY_REGISTRY_PATH = "replay_registry.json"
REPLAY_TTL_SECONDS = 300.0
REPLAY_MAX_SEQUENCE_GAP = 10

# Federation
FEDERATION_ENABLED = True
FEDERATION_SYNC_INTERVAL = 30.0

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"

# Runtime Identity
SERVICE_ID = "INSIGHT-RUNTIME-001"

# Trust
TRUST_PROVIDER = None

if create_trust_provider is not None:
    TRUST_PROVIDER = create_trust_provider("CLASSICAL")

SDK_CONFIG = {
    "discovery_urls": DISCOVERY_URLS,
    "trust_provider": TRUST_PROVIDER,
    "service_id": SERVICE_ID,
}