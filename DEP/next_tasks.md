# Next Tasks

## Post-Integration Task List & Roadmap

## Immediate Operational Tasks

- [x] Enforce contract compliance for outgoing REST registration payloads in `LivePlatformClient`.
- [x] Verify live network integration against `https://bhiv-qcg.onrender.com`.
- [x] Run internal readiness test suite (`python tests/test_integration_readiness.py` — 17/17 passed).
- [x] Refine all engineering markdown documentation to production standards.

---

## Future Post-Handover Roadmap

1. **Production Cluster Deployment**: Deploy `Insight_Constitutional_Runtime` container instances within the official BHIV production cluster.
2. **OpenTelemetry Collector Attachment**: Route `PlatformTelemetryAdapter` trace spans to cluster OpenTelemetry collectors.
3. **Hardware Governance Certification**: Complete hardware-level governance certification once shared platform hardware services are available.

*Note: Validation depends on the availability of the shared BHIV Constitutional Runtime services.*