import logging
import os
import warnings

logger = logging.getLogger("insight.config.platform_config")

PLATFORM_BASE_URL = os.getenv("PLATFORM_BASE_URL", "https://bhiv-qcg.onrender.com")

PLATFORM_REGISTRY = f"{PLATFORM_BASE_URL}/registry/platform"
CAPABILITY_REGISTRY = f"{PLATFORM_BASE_URL}/registry/capabilities"
PLATFORM_SDK = f"{PLATFORM_BASE_URL}/qcg"
EXTERNAL_RUNTIME = f"{PLATFORM_BASE_URL}/external"

_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off", ""}


def _parse_bool_env(val: str) -> bool:
    return val.strip().lower() in _TRUTHY


def is_http_services_mode() -> bool:
    """
    Determine whether ICR participants delegate to Insight microservices over HTTP.

    Precedence & Migration Policy:
      1. Canonical variable `INSIGHT_SERVICES_HTTP` takes precedence when set.
      2. Legacy alias `INSIGHT_OPTION_B_HTTP` (deprecated, removal in v2.0.0) is honored
         with a DeprecationWarning when `INSIGHT_SERVICES_HTTP` is unset.
      3. If both are set with conflicting boolean values, a warning is logged and
         `INSIGHT_SERVICES_HTTP` wins.
      4. Defaults to False (in-process execution) when neither is set.
    """
    canonical_raw = os.getenv("INSIGHT_SERVICES_HTTP")
    legacy_raw = os.getenv("INSIGHT_OPTION_B_HTTP")

    if canonical_raw is not None:
        canonical_val = _parse_bool_env(canonical_raw)
        if legacy_raw is not None:
            legacy_val = _parse_bool_env(legacy_raw)
            if canonical_val != legacy_val:
                logger.warning(
                    "Conflicting HTTP mode env vars: INSIGHT_SERVICES_HTTP=%r overrides "
                    "deprecated INSIGHT_OPTION_B_HTTP=%r.",
                    canonical_raw,
                    legacy_raw,
                )
        return canonical_val

    if legacy_raw is not None:
        warnings.warn(
            "INSIGHT_OPTION_B_HTTP is deprecated and scheduled for removal in v2.0.0; "
            "use INSIGHT_SERVICES_HTTP instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.warning(
            "INSIGHT_OPTION_B_HTTP is deprecated (removal in v2.0.0); use INSIGHT_SERVICES_HTTP."
        )
        return _parse_bool_env(legacy_raw)

    return False


def _resolve_service_url(canonical_var: str, legacy_var: str, default: str) -> str:
    val = os.getenv(canonical_var)
    if val:
        return val
    legacy_val = os.getenv(legacy_var)
    if legacy_val:
        return legacy_val
    return default


# Insight Ecosystem Service URLs (VM defaults: 8031 Workflow/Flow, 8029 Gateway/Bridge, 8030 Intelligence/Core)
INSIGHT_WORKFLOW_BASE_URL = _resolve_service_url(
    "INSIGHT_WORKFLOW_BASE_URL", "INSIGHT_FLOW_BASE_URL", "http://163.128.209.18:8031"
)
INSIGHT_GATEWAY_BASE_URL = _resolve_service_url(
    "INSIGHT_GATEWAY_BASE_URL", "INSIGHT_BRIDGE_BASE_URL", "http://163.128.209.18:8029"
)
INSIGHT_INTELLIGENCE_BASE_URL = _resolve_service_url(
    "INSIGHT_INTELLIGENCE_BASE_URL", "INSIGHT_CORE_BASE_URL", "http://163.128.209.18:8030"
)

# Backward-compatible constants
INSIGHT_FLOW_BASE_URL = INSIGHT_WORKFLOW_BASE_URL
INSIGHT_BRIDGE_BASE_URL = INSIGHT_GATEWAY_BASE_URL
INSIGHT_CORE_BASE_URL = INSIGHT_INTELLIGENCE_BASE_URL

# Marine Quantum Runtime Config
QUANTUM_RUNTIME_URL = os.getenv("QUANTUM_RUNTIME_URL", "https://marine-quantum-runtime-final.onrender.com")
QUANTUM_RUNTIME_MODE = os.getenv("QUANTUM_RUNTIME_MODE", "LIVE")
QUANTUM_RUNTIME_API_KEY = (
    os.getenv("Quantum_Runtime_Auth_Key")
    or os.getenv("QUANTUM_RUNTIME_API_KEY", "")
)
PLATFORM_TIMEOUT = int(os.getenv("PLATFORM_TIMEOUT", "45"))
