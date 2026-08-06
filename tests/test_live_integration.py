import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.integration.platform_integration_service import PlatformIntegrationService


def main():
    service = PlatformIntegrationService()

    result = service.integrate()

    print("Live Platform integration completed successfully.")
    print(result)


if __name__ == "__main__":
    main()