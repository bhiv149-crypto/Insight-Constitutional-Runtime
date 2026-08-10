"""
Project-wide constants for Insight Constitutional Runtime.

These constants define runtime identities, participant names,
versions, and shared metadata used across the Insight Stack.
"""

PROJECT_NAME = "Insight Constitutional Runtime"

PROJECT_VERSION = "1.0.2"

CONSTITUTIONAL_LAYER = "Intelligence Layer"

RUNTIME_TYPE = "Constitutional Runtime Participant"

PARTICIPANTS = {
    "INSIGHTFLOW": "InsightFlow",
    "INSIGHTBRIDGE": "InsightBridge",
    "INSIGHTCORE": "InsightCore",
}

RUNTIME_IDENTITIES = {
    "INSIGHTFLOW": "insightflow.runtime.intelligence.v1",
    "INSIGHTBRIDGE": "insightbridge.runtime.intelligence.v1",
    "INSIGHTCORE": "insightcore.runtime.intelligence.v1",
}

STATUS = {
    "DRAFT": "Draft",
    "ACTIVE": "Active",
    "REGISTERED": "Registered",
    "CERTIFIED": "Certified",
}