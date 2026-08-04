# Integration Architecture

Insight Runtime Participants integrate through the existing Constitutional Runtime.

InsightFlow
        │
        ▼
PlatformCapabilitySDK
        │
        ▼
CapabilityDiscoveryInterface
        │
        ▼
ExecutionValidatorInterface
        │
        ▼
ReplayVerifierInterface
        │
        ▼
HealthStatusInterface
        │
        ▼
Platform Runtime

---

## Runtime Responsibilities

Insight Participants

- Intelligence execution
- Capability consumption
- Runtime participation

Platform Services

- Discovery
- Registration
- Replay
- Trust Verification
- Runtime Execution
- Health Monitoring
- Evidence Generation