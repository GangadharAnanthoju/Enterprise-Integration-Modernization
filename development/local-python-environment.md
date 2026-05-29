# Local Python Environment

Use one virtual environment under the `agent` service.

This keeps the Python runtime, dependencies, tests, and local settings together.

## Create Environment

From the project root:

```powershell
cd C:\Data_AI\projects\Enterprise-Integration-Modernization
python -m venv agent\.venv
```

## Activate Environment

```powershell
.\agent\.venv\Scripts\Activate.ps1
```

After activation, your terminal prompt should show `(.venv)`.

## Install Requirements

```powershell
python -m pip install --upgrade pip
python -m pip install -r agent\requirements.txt
```

`agent\requirements.txt` is the source of truth for Python dependencies.

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

## Why Agent `.venv` Is Preferred

The repo currently has one Python service under `agent/`. Keeping the virtual environment under `agent` makes that service self-contained and avoids confusion with Logic Apps, Foundry docs, and infrastructure folders.

Later, if the project grows into multiple independently deployed Python apps, we can split environments by service.
