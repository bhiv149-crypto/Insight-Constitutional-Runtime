import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.integration.platform_integration_service import PlatformIntegrationService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

def main():
    logger = logging.getLogger("register_runtime")
    logger.info("Initiating platform registration reconciliation...")
    try:
        service = PlatformIntegrationService()
        # _ensure_runtime_registration requires participants to be created. 
        # PlatformIntegrationService constructor already calls _create_participants().
        service._ensure_runtime_registration()
        logger.info("Registration lifecycle completed successfully.")
        
        # Output the registration results for live evidence
        import json
        print("\n--- REGISTRATION RESULTS ---")
        print(json.dumps(service.registration_results, indent=2, default=str))
        
    except Exception as e:
        logger.error(f"Registration lifecycle failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
