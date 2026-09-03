
"""
Failure Path Test Suite - Insight Stack

Verifies failure behaviour through the canonical Platform SDK:

1. SERVICE_NOT_FOUND
   Invocation of a non-existent service must return a failure status.

2. VERSION_UNSUPPORTED
   Negotiation with an unsupported version must not be accepted.

4. HEALTH_UNKNOWN
   Health checks for a non-existent service must return an explicit status.

This suite is intentionally standalone and does not depend on a previous
successful integration run.

Exit code:
    0 = all failure paths verified
    1 = one or more failure paths failed
"""

import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.sdk_adapter import PlatformSDKAdapter


PASS = "[PASS]"
FAIL = "[FAIL]"


def check(name: str, condition: bool, note: str = "") -> bool:
    """Print a clean PASS/FAIL result and return the condition."""
    status = PASS if condition else FAIL
    suffix = f" - {note}" if note else ""
    print(f"  {status} {name}{suffix}")
    return condition


def separator():
    print("-" * 72)


def main():
    print()
    print("=" * 72)
    print("  INSIGHT STACK - FAILURE PATH TEST SUITE")
    print("=" * 72)
    print()

    failures = []
    sdk = PlatformSDKAdapter()

    # ------------------------------------------------------------------
    # Case 1: SERVICE_NOT_FOUND
    # ------------------------------------------------------------------
    separator()
    print("  CASE 1: SERVICE_NOT_FOUND - Non-existent service")
    separator()

    try:
        result = sdk.invoke_capability(
            service_id="ghost.service.that.does.not.exist.v999",
            operation="execute",
            payload={"test": "failure_path"},
            version="1.0.0",
        )

        status = (
            result.status
            if hasattr(result, "status")
            else result.get("status")
            if isinstance(result, dict)
            else None
        )

        print(f"  [INFO] Returned status: {status}")

        ok = check(
            "Non-existent service returns failure status",
            status in {
                "SERVICE_NOT_FOUND",
                "UNREACHABLE",
                "FAILED",
                "CIRCUIT_OPEN",
                "ERROR",
            },
            f"status={status}",
        )

        if not ok:
            failures.append("SERVICE_NOT_FOUND path failed")

    except Exception as exc:
        print(f"  {FAIL} SERVICE_NOT_FOUND raised an exception: {exc}")
        failures.append(f"SERVICE_NOT_FOUND exception: {exc}")

    print()

    # ------------------------------------------------------------------
    # Case 2: VERSION_UNSUPPORTED
    # ------------------------------------------------------------------
    separator()
    print("  CASE 2: VERSION_UNSUPPORTED - Unsupported version")
    separator()

    try:
        result = sdk.negotiate_version(
            "insightflow.runtime.intelligence.v1",
            "999.0.0",
        )

        status = (
            result.status
            if hasattr(result, "status")
            else result.get("status")
            if isinstance(result, dict)
            else None
        )

        print(f"  [INFO] Negotiation status: {status}")

        ok = check(
            "Unsupported version is rejected",
            status != "ACCEPTED",
            f"status={status}",
        )

        if not ok:
            failures.append("Unsupported version was incorrectly accepted")

    except Exception as exc:
        print(f"  {FAIL} VERSION test raised an exception: {exc}")
        failures.append(f"VERSION exception: {exc}")

    print()


    # ------------------------------------------------------------------
    # Case 4: HEALTH_UNKNOWN
    # ------------------------------------------------------------------
    separator()
    print("  CASE 4: HEALTH_UNKNOWN - Non-existent service")
    separator()

    try:
        result = sdk.check_health("ghost.service.v999")

        status = (
            result.status
            if hasattr(result, "status")
            else result.get("status")
            if isinstance(result, dict)
            else None
        )

        print(f"  [INFO] Health status: {status}")

        ok = check(
            "Unknown service returns an explicit health status",
            status is not None,
            f"status={status}",
        )

        if not ok:
            failures.append("Health check returned no status")

    except Exception as exc:
        print(f"  {FAIL} HEALTH test raised an exception: {exc}")
        failures.append(f"HEALTH exception: {exc}")

    print()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("=" * 72)

    if failures:
        print(f"  {FAIL} FAILURE PATHS INCOMPLETE - {len(failures)} issue(s)")
        for failure in failures:
            print(f"      - {failure}")
        print("=" * 72)
        sys.exit(1)

    print(f"  {PASS} ALL FAILURE PATHS VERIFIED")
    print()
    print("  SERVICE_NOT_FOUND      [PASS]")
    print("  VERSION_UNSUPPORTED    [PASS]")

    print("  HEALTH_UNKNOWN         [PASS]")
    print("=" * 72)

    sys.exit(0)


if __name__ == "__main__":
    main()
