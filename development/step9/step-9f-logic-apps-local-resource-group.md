# Step 9F: Logic Apps Local Resource Group Setting

## Goal

Record where the Logic Apps Standard designer stores the Azure resource group used for local workflow authoring.

## Resource Group

The current Azure resource group is:

```text
rg-sysint-enterprise-integration-eus
```

## Where It Is Configured

For the local Logic Apps Standard project, update:

```text
logicapps/standard-app/local.settings.json
```

The key is:

```json
"WORKFLOWS_RESOURCE_GROUP_NAME": "rg-sysint-enterprise-integration-eus"
```

`local.settings.json` is ignored by git because it can contain local environment and Azure account details.

The committed template is:

```text
logicapps/standard-app/local.settings.json.example
```

## Why This Matters

The Logic Apps designer uses these local workflow settings to know which Azure subscription, resource group, and location to use while authoring or connecting workflows.

## Interview Talking Point

I kept Azure designer settings local and documented the non-secret resource group in the template. Real local settings remain ignored so subscription and tenant-specific values are not accidentally committed.
