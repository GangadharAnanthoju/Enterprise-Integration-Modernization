# Step 2C: Tool Catalog API

## What We Built

We exposed the approved MCP tool catalog through the FastAPI service.

Before this step, the catalog existed only inside Python code. Now a user, UI, test, or future agent client can call the API and see the approved tools.

## New API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/tools` | Returns all approved MCP tools. |
| `GET` | `/tools/{tool_name}` | Returns one approved MCP tool by exact name. |

## Example URLs

When the API is running locally:

```text
http://127.0.0.1:8000/tools
http://127.0.0.1:8000/tools/sendSupplierNotification
```

## Files Changed

| File | Purpose |
|---|---|
| `agent/src/api/schemas.py` | Defines the API response shape for tool metadata. |
| `agent/src/api/routes.py` | Adds `/tools` and `/tools/{tool_name}` routes. |
| `agent/src/main.py` | Connects the API router to the FastAPI app. |
| `agent/tests/test_agent_flow.py` | Adds API tests for health, catalog, single tool, and unknown tool behavior. |

## Key Learning

This step makes the tool catalog visible outside the codebase.

For an Azure Integration specialist, this is similar to publishing a read-only catalog endpoint so other teams can discover available integration operations and their governance rules.

## How To Run Locally

From the repo root, after activating `agent\.venv` and installing `agent\requirements.txt`:

```powershell
cd agent\src
python -m uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

FastAPI will show an interactive API page.

## Next Step

Step 2D will expose risk decisions through the API so you can ask:

```text
Can this tool execute now, or does it require approval?
```
