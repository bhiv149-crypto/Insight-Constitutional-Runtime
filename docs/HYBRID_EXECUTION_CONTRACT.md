# Hybrid Execution Contract

## Classification
- **Quantum execution:** `QUANTUM_LOCAL`
- **Classical execution:** `CLASSICAL`
- **Fallback execution:** `FALLBACK`

## Validation Process
The QCG contract validation is performed locally. Upon SDK invocation, the payload passes through:
1. `validate_manifest()` (stubbed/local validation)
2. `invoke_capability()`
3. It hits `MarineQuantumAdapter`, which processes the payload as `QUANTUM_LOCAL`.
