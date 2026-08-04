"""
Shared data models for runtime participants.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RuntimeParticipant:
    """Represents a Constitutional Runtime Participant."""

    participant_name: str
    runtime_identity: str
    version: str
    constitutional_layer: str
    runtime_type: str
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)