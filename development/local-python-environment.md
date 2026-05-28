# Local Python Environment

Use one virtual environment at the repository root while we are learning.

This keeps commands simple and works well for the current project structure.

## Create Environment

From the project root:

```powershell
cd C:\Data_AI\projects\Enterprise-Integration-Modernization
python -m venv .venv
```

## Activate Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal prompt should show `(.venv)`.

## Install Requirements

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The root `requirements.txt` points to `agent/requirements.txt`.

## Run Tests

```powershell
cd agent
python -m pytest
```

## Quick Smoke Test

From the repo root:

```powershell
python -m compileall agent\src agent\tests
```

Then:

```powershell
cd agent\src
python -c "from tools.risk_policy import ExecutionDecision, evaluate_tool_name; assert evaluate_tool_name('getOrderStatus').decision == ExecutionDecision.ALLOW; assert evaluate_tool_name('sendSupplierNotification').decision == ExecutionDecision.REQUIRE_APPROVAL; print('risk policy smoke check passed')"
```

## Why Root `.venv` Is OK

The repo currently has one Python service under `agent/`. A root `.venv` lets us use one environment for the whole project while we build step by step.

Later, if the project grows into multiple independently deployed Python apps, we can split environments by service.
