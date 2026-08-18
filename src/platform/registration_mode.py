"""
Insight Platform Registration Mode

Controls whether live Platform Runtime registration is performed
automatically as part of the Insight lifecycle.

AUTO:
    Registration reconciliation is performed automatically.

MANUAL:
    No automatic registration is performed. Registration must be
    triggered explicitly by the existing registration workflow.
"""

import os


REGISTRATION_MODE = os.getenv(
    "INSIGHT_PLATFORM_REGISTRATION_MODE",
    "MANUAL",
).strip().upper()


AUTO_REGISTRATION_ENABLED = REGISTRATION_MODE == "AUTO"