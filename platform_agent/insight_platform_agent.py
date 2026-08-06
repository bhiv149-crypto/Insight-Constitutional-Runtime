import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.integration.platform_integration_service import (
    PlatformIntegrationService,
)

app = FastAPI(
    title="Insight Platform Agent",
    description="Platform integration agent for the Insight Runtime.",
    version="2.0.0",
)


@app.post("/platform/integrate")
def integrate():
    """
    Execute the complete Insight Runtime integration
    against the live BHIV Platform.
    """

    service = PlatformIntegrationService()

    result = service.integrate()

    return JSONResponse(content=result)


@app.get("/health")
def health():
    """
    Agent health endpoint.
    """

    return {
        "status": "UP",
        "agent": "Insight Platform Agent",
        "runtime": "Insight Runtime",
        "platform": "BHIV Constitutional Runtime",
        "version": "2.0.0",
    }


@app.get("/")
def root():
    """
    Root endpoint.
    """

    return {
        "service": "Insight Platform Agent",
        "status": "READY",
        "integration": "Live BHIV Platform",
        "endpoint": "/platform/integrate",
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
    )