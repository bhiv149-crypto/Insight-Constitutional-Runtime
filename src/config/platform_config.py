import os

PLATFORM_BASE_URL = os.getenv("PLATFORM_BASE_URL", "https://bhiv-qcg.onrender.com")

PLATFORM_REGISTRY = f"{PLATFORM_BASE_URL}/registry/platform"
CAPABILITY_REGISTRY = f"{PLATFORM_BASE_URL}/registry/capabilities"
PLATFORM_SDK = f"{PLATFORM_BASE_URL}/qcg"
EXTERNAL_RUNTIME = f"{PLATFORM_BASE_URL}/external"

# Vijay Deployed Services Config
INSIGHT_FLOW_BASE_URL = os.getenv("INSIGHT_FLOW_BASE_URL", "https://insight-flow-f5j4.onrender.com")
INSIGHT_BRIDGE_BASE_URL = os.getenv("INSIGHT_BRIDGE_BASE_URL", "https://insightbridge-phase-4-2-integration-demo.onrender.com")

# Dhiraj Marine Quantum Runtime Config
QUANTUM_RUNTIME_URL = os.getenv("QUANTUM_RUNTIME_URL", "https://marine-quantum-runtime-final.onrender.com")
QUANTUM_RUNTIME_MODE = os.getenv("QUANTUM_RUNTIME_MODE", "LIVE")
QUANTUM_RUNTIME_API_KEY = os.getenv("QUANTUM_RUNTIME_API_KEY", "dev-insecure-key")
PLATFORM_TIMEOUT = int(os.getenv("PLATFORM_TIMEOUT", "45"))