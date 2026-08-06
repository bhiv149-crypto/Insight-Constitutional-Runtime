import sys
from pathlib import Path

# Add project root and reference root to python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
copy_of_main_path = Path("C:/Ganesh_149/Bhiv QCG works/copy of main/bhiv-QCG-main")
if copy_of_main_path.exists() and str(copy_of_main_path) not in sys.path:
    sys.path.insert(0, str(copy_of_main_path))

# First load our imports to ensure config patch is registered in-memory
import src.platform.imports

from src.integration.platform_integration_service_local import PlatformIntegrationService

def main():
    service = PlatformIntegrationService()
    result = service.integrate(local_runtime=True)
    print("Live Platform integration test completed successfully.")
    print("Result:", result)

if __name__ == "__main__":
    main()