"""
InsightBridge Runtime Lifecycle.

Maintains the constitutional lifecycle state of the
InsightBridge Runtime Participant.
"""

from enum import Enum


class LifecycleState(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class InsightBridgeLifecycle:
    """
    Lifecycle manager for the InsightBridge participant.
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
            "participant": "InsightBridge",
            "lifecycle": self._state.value,
        }