"""
Custom exceptions used throughout the Insight Constitutional Runtime.
"""


class RuntimeIntegrationError(Exception):
    """Raised when runtime integration fails."""


class RegistrationError(RuntimeIntegrationError):
    """Raised when participant registration fails."""


class DiscoveryError(RuntimeIntegrationError):
    """Raised when runtime discovery fails."""


class CapabilityError(RuntimeIntegrationError):
    """Raised when capability operations fail."""


class HealthCheckError(RuntimeIntegrationError):
    """Raised when health validation fails."""