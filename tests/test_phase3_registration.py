import os
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Force the INSIGHT_SERVICE_URL
os.environ["INSIGHT_SERVICE_URL"] = "https://loose-books-beam.loca.lt"

from src.platform.live_platform_client import LivePlatformClient
from src.integration.registration_builder import RegistrationBuilder

from src.participants.insightflow.participant import InsightFlowParticipant
from src.participants.insightbridge.participant import InsightBridgeParticipant
from src.participants.insightcore.participant import InsightCoreParticipant

def run_phase3():
    client = LivePlatformClient()
    
    participants = [
        InsightFlowParticipant(),
        InsightBridgeParticipant(),
        InsightCoreParticipant(),
    ]
    
    # 1. Register Runtime
    print("--- REGISTRATION ---")
    for p in participants:
        record = RegistrationBuilder.build_service_record(p.participant)
        print(f"Registering {p.participant.runtime_identity}...")
        resp = client.register_runtime(record)
        print(f"Response: {resp}")

    # 2. Register Capability
    print("\n--- CAPABILITY REGISTRATION ---")
    for p in participants:
        manifest = RegistrationBuilder.build_capability_manifest(p.participant)
        print(f"Registering capability {p.participant.runtime_identity}...")
        resp = client.register_capability(manifest)
        print(f"Response: {resp}")

    # 3. Discovery
    print("\n--- DISCOVERY ---")
    services = client.list_services().get("services", [])
    for svc in services:
        if "insight" in svc.get("platform_service_id", ""):
            print(json.dumps(svc, indent=2))
            
if __name__ == "__main__":
    run_phase3()
