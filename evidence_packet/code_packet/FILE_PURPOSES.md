# File Purposes

## src/common/

base_participant.py

Purpose:
Base abstraction for Constitutional Runtime Participants.

---

models.py

Purpose:
Shared runtime models.

---

constants.py

Purpose:
Project-wide runtime constants.

---

## src/platform/

sdk_adapter.py

Purpose:
Thin wrapper around PlatformCapabilitySDK.

---

registry_adapter.py

Purpose:
Platform Registry integration.

---

runtime_adapter.py

Purpose:
Central runtime integration layer.

---

discovery_adapter.py

Purpose:
Capability discovery wrapper.

---

health_adapter.py

Purpose:
Platform health integration.

---

replay_adapter.py

Purpose:
Replay Registry integration.

---

telemetry_adapter.py

Purpose:
Platform observability integration.

---

imports.py

Purpose:
Centralized Platform imports with development fallbacks.

---

stubs.py

Purpose:
Development stubs used before official Platform Runtime integration.

---

## src/integration/

registration_builder.py

Purpose:
Builds Platform registration artifacts.

participant_registration.py

Purpose:
Registers runtime participants.

capability_discovery.py

Purpose:
Capability discovery workflow.

capability_invocation.py

Purpose:
Capability invocation workflow.

runtime_validation.py

Purpose:
Runtime readiness validation.