"""
Integration Readiness Test

Purpose
-------
Verify that the Insight Runtime repository is internally consistent
and ready for Platform Runtime integration.

This test DOES NOT require the Platform Runtime repository.
"""
import sys
from pathlib import Path
import importlib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

ROOT = PROJECT_ROOT

def print_result(name, success):
    symbol = "✓" if success else "✗"
    print(f"{symbol} {name}")


def module_exists(module_name):
    try:
        importlib.import_module(module_name)
        return True, None
    except Exception as e:
        return False, repr(e)


def file_exists(relative_path):
    return (ROOT / relative_path).exists()


def main():

    print("=" * 70)
    print("Insight Runtime Integration Readiness")
    print("=" * 70)

    checks = []

    # ------------------------------------------------------------
    # Folder checks
    # ------------------------------------------------------------

    folders = [
        ("Platform package", "src/platform"),
        ("Participants package", "src/participants"),
        ("Integration package", "src/integration"),
        ("Common package", "src/common"),
    ]

    for name, folder in folders:
        checks.append(
            (
                name,
                file_exists(folder),
                None,
            )
        )

    # ------------------------------------------------------------
    # Module checks
    # ------------------------------------------------------------

    modules = [
        "src.common.base_participant",

        "src.platform.sdk_adapter",
        "src.platform.registry_adapter",
        "src.platform.discovery_adapter",
        "src.platform.health_adapter",
        "src.platform.runtime_adapter",

        "src.integration.participant_registration",
        "src.integration.capability_discovery",
        "src.integration.capability_invocation",
        "src.integration.runtime_validation",

        "src.participants.insightflow",
        "src.participants.insightcore",
        "src.participants.insightbridge",
    ]

    for module in modules:

        success, error = module_exists(module)

        checks.append(
            (
                f"Import {module}",
                success,
                error,
            )
        )

    # ------------------------------------------------------------
    # Results
    # ------------------------------------------------------------

    passed = 0

    print()

    for name, success, error in checks:

        print_result(name, success)

        if success:
            passed += 1
        elif error:
            print(f"    -> {error}")

    print()
    print("-" * 70)

    print(f"Passed : {passed}")
    print(f"Failed : {len(checks) - passed}")
    print(f"Total  : {len(checks)}")

    print("-" * 70)

    if passed == len(checks):
        print("\nRepository is internally ready for Platform integration.")
    else:
        print("\nResolve the failed imports before Runtime integration.")


if __name__ == "__main__":
    main()