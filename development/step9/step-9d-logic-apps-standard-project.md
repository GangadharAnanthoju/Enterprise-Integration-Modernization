# Step 9D: Logic Apps Standard Project Structure

## Goal

Create a separate Logic Apps Standard project folder that can be opened independently in VS Code for designer work.

The repository root is still the main project. The Logic Apps designer can be pointed at:

```text
logicapps/standard-app
```

## What Changed

- Added `logicapps/standard-app/host.json`.
- Added `logicapps/standard-app/local.settings.json.example`.
- Added `logicapps/standard-app/connections.json`.
- Added `logicapps/standard-app/parameters.json`.
- Added `logicapps/standard-app/getOrderStatus/workflow.json`.
- Added a test to ensure the designer-friendly workflow copy matches the source workflow.

## Why This Matters

The source workflow contract remains under:

```text
logicapps/workflows/getOrderStatus
```

The designer-friendly Logic Apps Standard project lives under:

```text
logicapps/standard-app
```

That means we do not have to open the repository root as a Logic Apps project. Later, you can open only `logicapps/standard-app` in VS Code and use the Logic Apps Standard designer there.

## Interview Talking Point

I kept source contracts and designer workspace concerns separate. The repo can stay organized for backend code and documentation, while the Logic Apps Standard project can be opened independently for workflow design.
