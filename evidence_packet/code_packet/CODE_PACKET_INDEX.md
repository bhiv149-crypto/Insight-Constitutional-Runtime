# Code Packet Index

- `tests/test_live_platform.py`: Provides evidence of the SDK verification and replay execution, clearly documenting the QCG 422 Trust error while passing Replay.
- `src/platform/stubs.py`: Shows the mock TraceStore implementation proving transient persistence.
- `src/platform/quantum_adapter.py`: Shows fallback to local simulated execution (QUANTUM_LOCAL) and provider-ready support for `LIVE` mode. Explicitly handles 401 Unauthorized errors to accurately report an authentication failure as `BLOCKED`. Enriches result with runtime mode and provider source to maintain strict execution classification boundaries. Implements `PROVIDER_READY` integration, Failure Behavior (controlled rejection), and Provider Identity / Provenance (explicit `execution_classification`).
- `tests/test_quantum_adapter_live.py`: Automated tests to verify the newly added `LIVE` mode and the modified authentication error handling logic. Fulfills the Ganesh test matrix requirement (Live authentication failure -> BLOCKED).
- `scripts/generate_evidence.py`: Script to manually execute `MarineQuantumAdapter` in `LIVE` mode to collect health, capability, and execution responses. Fulfills the requirement for capturing genuine evidence.
