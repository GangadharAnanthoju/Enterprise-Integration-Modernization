from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from persistence import configure_persistence
from telemetry.exporter import configure_observability


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Configure production services before serving requests."""

    configure_observability()
    configure_persistence()
    yield


app = FastAPI(title="Enterprise Integration Agent API", lifespan=lifespan)

app.include_router(router)

@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check used by developers, pipelines, and hosting probes."""

    return {"status": "ok"}
