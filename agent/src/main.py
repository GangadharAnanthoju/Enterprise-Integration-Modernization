from fastapi import FastAPI

from api.routes import router

# This creates the FastAPI web application.
# Later, this same app will host the agent chat endpoint and MCP simulation endpoints.
app = FastAPI(title="Enterprise Integration Agent API")

# The router keeps endpoint definitions in api/routes.py instead of putting
# every API path in this startup file.
app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check used by developers, pipelines, and hosting probes."""

    return {"status": "ok"}
