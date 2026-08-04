"""
InsightFlow Runtime Lifecycle.

Lifecycle implementation aligned with the Constitutional Runtime.
"""

from enum import Enum


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class InsightFlowLifecycle:
    """
    Maintains the lifecycle state of the InsightFlow participant.
    """

    def __init__(self):
        self._state = LifecycleState.DRAFT

    @property
    def state(self):
        return self._state

    def activate(self):
        self._state = LifecycleState.ACTIVE

    def deprecate(self):
        self._state = LifecycleState.DEPRECATED

    def retire(self):
        self._state = LifecycleState.RETIRED

    def as_dict(self):
        return {
            "participant": "InsightFlow",
            "lifecycle": self._state.value,
        }