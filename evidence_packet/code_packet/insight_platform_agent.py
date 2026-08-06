import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.integration.platform_integration_service_local import (
    PlatformIntegrationService,
)

app = FastAPI(
    title="Insight Platform Agent",
    version="1.0.0",
)

import os

@app.post("/platform/integrate")
def integrate(local_runtime: bool = False):
    # Default to False in production. Allow override via parameter or env var.
    env_local = os.environ.get("INSIGHT_LOCAL_RUNTIME", "false").lower() == "true"
    use_local = local_runtime or env_local

    service = PlatformIntegrationService()

    result = service.integrate(
        local_runtime=use_local,
    )

    return JSONResponse(result)


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
    )