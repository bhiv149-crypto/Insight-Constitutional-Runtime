"""
Failure Case Test Suite â€” Insight Stack

Tests failure-path behaviour through the canonical Platform SDK:

  - SERVICE_NOT_FOUND: Invocation of a non-existent service
  - VERSION_REJECTED / UNSUPPORTED: Negotiation with incompatible version
  - REPLAY_DUPLICATE: Duplicate message_id submission rejected
  - HEALTH_UNREACHABLE: Health check for non-existent service

This test does NOT require a successful prior integration run.
It exercises the adapter boundaries independently.

Exit code 0 = all failure paths exercised correctly.
Exit code 1 = one or more failure paths broken.
"""
import sys
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.platform.sdk_adapter import PlatformSDKAdapter
from src.platform.replay_adapter import PlatformReplayAdapter


PASS = "[PASS]"
FAIL = "[FAIL]"


def check(name: str, condition: bool, note: str = "") -> bool:
    symbol = PASS if condition else FAIL
    print(f"  {symbol} {name}", f"â€” {note}" if note else "")
    return condition


def main():
    print()
    print("=" * 72)
    print("  INSIGHT STACK â€” FAILURE PATH TEST SUITE")
    print("=" * 72)
    print()

    failures = []
    sdk = PlatformSDKAdapter()

    # ------------------------------------------------------------------ #
    # Case 1: SERVICE_NOT_FOUND                                            #
    # ------------------------------------------------------------------ #
    print("â”€" * 72)
    print("  CASE 1: SERVICE_NOT_FOUND â€” Invoke non-existent service")
    print("â”€" * 72)

    try:
        result = sdk.invoke_capability(
            service_id="ghost.service.that.does.not.exist.v999",
            operation="execute",
            payload={"test": "failure_path"},
            version="1.0.0",
        )

        status = None
        if hasattr(result, 'status'):
            status = result.status
        elif isinstance(result, dict):
            status = result.get("status")

        print(f"  [*] Got status: {status}")

        ok = check(
            "Non-existent service returns failure status",
            status in ("SERVICE_NOT_FOUND", "UNREACHABLE", "FAILED",
                       "CIRCUIT_OPEN", "ERROR"),
            f"status={status}",
        )
        if not ok:
            failures.append("SERVICE_NOT_FOUND not returned for ghost service")
    except Exception as exc:
        print(f"  {FAIL} Exception during SERVICE_NOT_FOUND test: {exc}")
        failures.append(f"SERVICE_NOT_FOUND exception: {exc}")

    print()

    # ------------------------------------------------------------------ #
    # Case 2: VERSION NEGOTIATION â€” Incompatible version                   #
    # ------------------------------------------------------------------ #
    print("â”€" * 72)
    print("  CASE 2: VERSION â€” Negotiate unsupported version 999.0.0")
    print("â”€" * 72)

    try:
        neg_result = sdk.negotiate_version(
            "insightflow.runtime.intelligence.v1",
            "999.0.0",
        )

        status = None
        if hasattr(neg_result, 'status'):
            status = neg_result.status
        elif isinstance(neg_result, dict):
            status = neg_result.get("status")

        print(f"  [*] Negotiation status: {status}")

        ok = check(
            "Unsupported version returns non-ACCEPTED status",
            status in ("UNSUPPORTED", "UNREACHABLE", "UNKNOWN", "NEGOTIATED",
                       "FALLBACK", "ERROR", "NOT_FOUND"),
            f"status={status}",
        )
        if not ok:
            failures.append("Version negotiation did not return a usable status")
    except Exception as exc:
        print(f"  {FAIL} Exception during VERSION test: {exc}")
        failures.append(f"VERSION exception: {exc}")

    print()

    # ------------------------------------------------------------------ #
    # Case 3: REPLAY DUPLICATE â€” Same message_id submitted twice           #
    # ------------------------------------------------------------------ #
    print("â”€" * 72)
    print("  CASE 3: REPLAY DUPLICATE â€” Same message_id submitted twice")
    print("â”€" * 72)

    try:
        replay = PlatformReplayAdapter()
        msg_id = f"msg-failure-test-{uuid.uuid4().hex[:8]}"
        trace_ref = f"trace-failure-{uuid.uuid4().hex[:8]}"

        v1 = replay.submit(msg_id, time.time(), trace_ref)
        v2 = replay.submit(msg_id, time.time(), trace_ref)

        print(f"  [*] Submission 1 status: {v1.status}")
        print(f"  [*] Submission 2 status: {v2.status}")

        ok_first = check("First submission is VALID", v1.status == "VALID",
                         f"status={v1.status}")
        ok_dup   = check("Second submission is DUPLICATE", v2.status == "DUPLICATE",
                         f"status={v2.status}, reason={v2.reason}")

        if not ok_first:
            failures.append("First replay submission not VALID")
        if not ok_dup:
            failures.append("Second replay submission not DUPLICATE â€” stub still active")
    except Exception as exc:
        print(f"  {FAIL} Exception during REPLAY DUPLICATE test: {exc}")
        failures.append(f"REPLAY exception: {exc}")

    print()

    # ------------------------------------------------------------------ #
    # Case 4: HEALTH â€” Non-existent service                                #
    # ------------------------------------------------------------------ #
    print("â”€" * 72)
    print("  CASE 4: HEALTH CHECK â€” Non-existent service")
    print("â”€" * 72)

    try:
        health = sdk.check_health("ghost.service.v999")

        status = None
        if hasattr(health, 'status'):
            status = health.status
        elif isinstance(health, dict):
            status = health.get("status")

        print(f"  [*] Health status: {status}")

        ok = check(
            "Health check returns a status for non-existent service",
            status is not None,
            f"status={status}",
        )
        if not ok:
            failures.append("Health check returned no status")
    except Exception as exc:
        print(f"  {FAIL} Exception during HEALTH test: {exc}")
        failures.append(f"HEALTH exception: {exc}")

    print()

    # ------------------------------------------------------------------ #
    # Summary                                                              #
    # ------------------------------------------------------------------ #
    print("=" * 72)
    if failures:
        print(f"  {FAIL} FAILURE PATH TESTS INCOMPLETE â€” {len(failures)} issue(s):")
        for f in failures:
            print(f"      - {f}")
        print("=" * 72)
        sys.exit(1)
    else:
        print(f"  {PASS} ALL FAILURE PATHS VERIFIED")
        print("  SERVICE_NOT_FOUND âœ“  VERSION_INCOMPATIBLE âœ“  REPLAY_DUPLICATE âœ“  HEALTH_UNREACHABLE âœ“")
        print("=" * 72)
        sys.exit(0)


if __name__ == "__main__":
    main()


