import os
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Force the INSIGHT_SERVICE_URL to the public deployed URL
os.environ["INSIGHT_SERVICE_URL"] = "https://slapstick-ditch-raving.ngrok-free.dev"

from src.integration.platform_integration_service import PlatformIntegrationService

def run_phase4():
    print("Starting Live Platform Integration (Phase 4)...")
    service = PlatformIntegrationService()
    try:
        result = service.integrate()
        print("Integration SUCCESS")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("Integration FAILED")
        print(str(e))

if __name__ == "__main__":
    run_phase4()
