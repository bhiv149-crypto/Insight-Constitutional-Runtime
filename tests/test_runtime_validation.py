from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integration.runtime_validation import RuntimeValidation


def main():
    validator = RuntimeValidation()
    report = validator.validate()

    print("=" * 60)
    print("Runtime Validation Report")
    print("=" * 60)

    for key, value in report.items():
        print(f"{key:25} : {value}")


if __name__ == "__main__":
    main()