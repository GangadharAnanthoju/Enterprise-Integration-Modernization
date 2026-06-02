from fastapi import FastAPI

from api.routes import router

app = FastAPI(title="Enterprise Integration Agent API")

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check used by developers, pipelines, and hosting probes."""

    return {"status": "ok"}
