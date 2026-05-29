# Step 9E: Logic Apps Designer Workspace

## Goal

Make the Logic Apps Standard project easy to open separately in VS Code for designer work.

## What Changed

- Added `logicapps/standard-app/Enterprise-Integration-LogicApps.code-workspace`.
- Added `logicapps/standard-app/getOrderStatus/sample-request.json`.
- Updated `logicapps/standard-app/README.md` with open-designer instructions.
- Added `logicapps/standard-app/local.settings.json` to `.gitignore`.

## How To Open

Open this workspace in a separate VS Code window:

```text
C:\Data_AI\projects\Enterprise-Integration-Modernization\logicapps\standard-app\Enterprise-Integration-LogicApps.code-workspace
```

Then open:

```text
getOrderStatus/workflow.json
```

Right-click and choose:

```text
Open Designer
```

## Why This Matters

The main repository can stay organized for agent code, tests, docs, and infrastructure. The Logic Apps Standard workspace can be opened independently when we want designer behavior.

## Interview Talking Point

I separated the Logic Apps designer workspace from the rest of the repository. That keeps the workflow authoring experience clean without forcing the entire modernization repo to become a Logic Apps project.
