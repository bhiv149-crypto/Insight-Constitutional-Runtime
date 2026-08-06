import requests

from src.config.platform_config import (
    PLATFORM_REGISTRY,
    CAPABILITY_REGISTRY,
    PLATFORM_SDK,
)


class LivePlatformClient:
    """REST client for communicating with the live BHIV Platform."""

    DEFAULT_TIMEOUT = 20

    def __init__(self):
        self.registry = PLATFORM_REGISTRY
        self.capability = CAPABILITY_REGISTRY
        self.sdk = PLATFORM_SDK

    def server_health(self) -> dict:
        response = requests.get(
            f"{self.registry}/v1/health",
            timeout=self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def list_services(self) -> dict:
        response = requests.get(
            f"{self.registry}/v1/services",
            timeout=self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def register_runtime(self, record: dict) -> dict:

        payload = {
            "service_id": record.get("platform_service_id"),
            "record": record
        }

        url = f"{self.registry}/v1/register"

        print("\n" + "=" * 60)
        print("LIVE PLATFORM RUNTIME REGISTRATION")
        print("=" * 60)
        print("POST:", url)
        print("Payload:")
        print(payload)

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=20,
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            print("\nRuntime registration request timed out.")
            raise

        except requests.exceptions.RequestException as exc:
            print("\nRuntime registration failed.")
            print(exc)
            raise


    def register_capability(self, capability: dict) -> dict:

        url = f"{self.capability}/register"

        print("\n" + "=" * 60)
        print("LIVE CAPABILITY REGISTRATION")
        print("=" * 60)
        print("POST:", url)
        print("Payload:")
        print(capability)

        try:
            response = requests.post(
                url,
                json=capability,
                timeout=20,
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            print("\nCapability registration request timed out.")
            raise

        except requests.exceptions.RequestException as exc:
            print("\nCapability registration failed.")
            print(exc)
            raise

    def discover_capability(self, capability_name: str) -> dict:
        response = requests.get(
            f"{self.capability}/discover/{capability_name}",
            timeout=self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()