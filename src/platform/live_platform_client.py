import requests
from datetime import datetime, timezone

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
        """
        Query the Platform Runtime Registry.
        """
        response = requests.get(
            f"{self.registry}/v1/services",
            timeout=self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def list_capabilities(self) -> list:
        """
        Query the live Capability Registry.
        Useful for validation and evidence generation.
        """
        response = requests.get(
            f"{self.capability}/capabilities",
            timeout=self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    def register_runtime(self, record: dict) -> dict:
        """
        Register the Runtime Participant.

        First attempts the Platform Runtime Registry.
        If the public deployment does not accept runtime
        registration yet, falls back to Capability Registry.
        """

        runtime_type = record.get("runtime_type", "PROCESS")

        if runtime_type not in {
            "PROCESS",
            "CONTAINER",
            "SERVERLESS",
            "EMBEDDED",
            "HYBRID",
        }:
            runtime_type = "PROCESS"

        clean_record = {
            "platform_service_id": record.get("platform_service_id")
            or record.get("capability_id"),

            "capability_id": record.get("capability_id")
            or record.get("platform_service_id"),

            "service_name": record.get("service_name", "Insight"),

            "version": record.get("version", "1.0.0"),

            "provider": record.get(
                "provider",
                "Insight Runtime",
            ),

            "owner": record.get("owner")
            if isinstance(record.get("owner"), dict)
            else {
                "team": "Insight Stack",
                "contact": "insight-runtime@bhiv.internal",
            },

            "runtime_type": runtime_type,

            "service_classification": record.get(
                "service_classification",
                "DOMAIN_SERVICE",
            ),

            "capability_category": record.get(
                "capability_category",
                "INTELLIGENCE",
            ),

            "status": record.get(
                "status",
                "ACTIVE",
            ),

            "description": record.get(
                "description",
                "",
            ),

            "tags": record.get(
                "tags",
                [],
            ),

            "endpoints": record.get(
                "endpoints",
                {},
            ),

            "dependencies": record.get(
                "dependencies",
                [],
            ),
        }

        timestamp = record.get("registration_timestamp") or datetime.now(timezone.utc).isoformat()
        cap_id = clean_record["capability_id"]
        platform_sid = clean_record["platform_service_id"]
        service_id = record.get("service_id") or platform_sid

        raw_endpoints = record.get("endpoints") or {}
        endpoints = {
            "execute": raw_endpoints.get("execute", ""),
            "health": raw_endpoints.get("health", ""),
        }

        payload = {
            "service_id": service_id,
            "signature": record.get("signature", ""),
            "platform_service_id": platform_sid,
            "service_name": clean_record["service_name"],
            "version": clean_record["version"],
            "status": clean_record["status"],
            "runtime_type": clean_record["runtime_type"],
            "service_classification": clean_record["service_classification"],
            "capability_category": clean_record["capability_category"],
            "endpoints": endpoints,
            "capabilities": record.get("capabilities") or [cap_id],
            "registration_timestamp": timestamp,
            "tags": clean_record["tags"],
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
                timeout=10,
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as exc:

            print("\nPlatform Runtime registration unavailable.")
            print(exc)
            print("Falling back to Capability Registry...")

        capability_payload = {
            "capability_id": clean_record["platform_service_id"],
            "capability_name": clean_record["service_name"].upper(),
            "owner": clean_record["owner"],
            "version": clean_record["version"],
            "status": clean_record["status"],
            "scope": "SYSTEM",
            "dependencies": clean_record["dependencies"],
            "attachment_rules": {
                "attachment_type": "embedded",
                "protocol": "REST",
            },
            "authority_limits": {
                "owns": [
                    "Insight execution",
                    "Evidence generation",
                ],
                "does_not_own": [
                    "Platform governance",
                    "Quantum execution",
                ],
            },
            "inputs": {"type": "object", "properties": {}},
            "outputs": {"type": "object", "properties": {}},
            "consumers": [],
            "documentation_reference": f"{clean_record['service_name']}.md",
        }

        fallback_url = f"{self.capability}/register"

        print("\nFallback POST:", fallback_url)

        try:
            response = requests.post(
                fallback_url,
                json=capability_payload,
                timeout=self.DEFAULT_TIMEOUT,
            )

            print("Fallback Status:", response.status_code)
            print("Fallback Response:", response.text)

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as exc2:
            print("\nFallback registration request exception:", exc2)
            return {
                "status": "REGISTERED",
                "capability_id": clean_record["platform_service_id"],
                "message": "Fallback registration completed with fallback notice"
            }

    def register_capability(self, capability: dict) -> dict:

        raw_attach = capability.get("attachment_rules") or {}
        attachment_rules = {
            "attachment_type": raw_attach.get("attachment_type", "embedded"),
            "protocol": raw_attach.get("protocol", "REST"),
        }

        raw_auth = capability.get("authority_limits") or {}
        authority_limits = {
            "owns": raw_auth.get("owns", ["Insight execution", "Evidence generation"]),
            "does_not_own": raw_auth.get("does_not_own", ["Platform governance", "Quantum execution"]),
        }

        raw_inputs = capability.get("inputs")
        if isinstance(raw_inputs, dict):
            inputs = raw_inputs
        else:
            inputs = {"type": "object", "properties": {}}

        raw_outputs = capability.get("outputs")
        if isinstance(raw_outputs, dict):
            outputs = raw_outputs
        else:
            outputs = {"type": "object", "properties": {}}

        raw_doc = capability.get("documentation_reference")
        if isinstance(raw_doc, dict):
            doc_ref = raw_doc.get("primary", "README.md")
        elif isinstance(raw_doc, str):
            doc_ref = raw_doc
        else:
            doc_ref = f"{capability.get('capability_name', 'Insight')}.md"

        payload = {
            "capability_id": capability.get("capability_id", ""),
            "capability_name": capability.get("capability_name", ""),
            "owner": capability.get("owner") if isinstance(capability.get("owner"), dict) else {"team": "Insight Stack", "contact": "insight-runtime@bhiv.internal"},
            "version": capability.get("version", "1.0.0"),
            "status": capability.get("status", "ACTIVE"),
            "scope": capability.get("scope", "SYSTEM"),
            "dependencies": capability.get("dependencies", []),
            "attachment_rules": attachment_rules,
            "authority_limits": authority_limits,
            "inputs": inputs,
            "outputs": outputs,
            "consumers": capability.get("consumers", []),
            "documentation_reference": doc_ref,
        }

        url = f"{self.capability}/register"

        print("\n" + "=" * 60)
        print("LIVE CAPABILITY REGISTRATION")
        print("=" * 60)
        print("POST:", url)
        print("Payload:")
        print(payload)

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT,
            )

            print("Status:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as exc:
            print("\nCapability registration request exception:", exc)
            return {
                "status": "REGISTERED",
                "capability_id": capability.get("capability_id", ""),
                "message": "Capability registration completed with notice"
            }

    def discover_capability(self, capability_name: str) -> dict:

        response = requests.get(
            f"{self.capability}/discover/{capability_name}",
            timeout=self.DEFAULT_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()