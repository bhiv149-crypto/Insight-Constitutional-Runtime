# Provider Classification

## Current Provider State
- **Identity:** Marine Quantum Runtime
- **Execution Mode:** `QUANTUM_LIVE` (using simulated quantum providers)
- **Live Simulator Available:** TRUE (`local_simulator` and `aer`)
- **Live Hardware Available:** FALSE (BLOCKED due to missing credentials/SDKs)

*Evidence: `MarineQuantumAdapter` correctly routes to `https://marine-quantum-runtime-final.onrender.com` in LIVE mode, which responds with `local_simulator` capabilities.*
