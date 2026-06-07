from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

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


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """Open the operational chat console by default."""

    return RedirectResponse(url="/ui/")


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check used by developers, pipelines, and hosting probes."""

    return {"status": "ok"}


app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).resolve().parent / "ui", html=True),
    name="ui",
)
