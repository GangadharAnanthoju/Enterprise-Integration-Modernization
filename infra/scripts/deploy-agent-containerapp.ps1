param(
    [string]$ResourceGroup = "rg-sysint-enterprise-integration-eus",
    [string]$Location = "eastus",
    [string]$AppName = "ca-sysint-enterprise-agent-eus",
    [string]$AcrName = "acrsysintcommoneus",
    [string]$AcaEnvironmentName = "aca-env-sysint-eus",
    [string]$AcaEnvironmentResourceGroup = "rg-sysint-common-eus",
    [string]$KeyVaultName = "kv-sysint-common-eus",
    [string]$ApplicationInsightsName = "appi-sysint-common-dev-eus",
    [string]$ApplicationInsightsResourceGroup = "rg-sysint-common-eus",
    [string]$StorageAccountName = "stsysintintegeus001",
    [string]$ImageName = "enterprise-integration-agent",
    [string]$ImageTag = "latest",
    [string]$AgentRuntimeMode = "foundry",
    [string]$FoundryProjectEndpoint = "https://ms-foundry-sysint-02.services.ai.azure.com/api/projects/proj-sysint-01",
    [string]$ModelDeploymentName = "gpt-4.1-mini",
    [string]$FoundryResourceGroup = "rg-sysint-ms-foundry",
    [string]$FoundryAccountName = "ms-foundry-sysint-02",
    [string]$FoundryProjectName = "proj-sysint-01",
    [string]$McpServerUrl = "https://la-sysint-enterprise-integration-eus.azurewebsites.net/api/mcpservers/enterpriseintegrationmcp/mcp",
    [switch]$SkipRoleAssignments,
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONUTF8 = "1"
$env:AZURE_CORE_NO_COLOR = "1"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$AgentDir = Join-Path $RepoRoot "agent"
$Image = "$AcrName.azurecr.io/${ImageName}:$ImageTag"
$SubscriptionId = az account show --query id --output tsv
$TenantId = az account show --query tenantId --output tsv
$AcaEnvironmentId = az containerapp env show `
    --name $AcaEnvironmentName `
    --resource-group $AcaEnvironmentResourceGroup `
    --query id `
    --output tsv
$KeyVaultId = az keyvault show `
    --name $KeyVaultName `
    --resource-group $AcaEnvironmentResourceGroup `
    --query id `
    --output tsv
$ApplicationInsightsId = az resource show `
    --name $ApplicationInsightsName `
    --resource-group $ApplicationInsightsResourceGroup `
    --resource-type "Microsoft.Insights/components" `
    --query id `
    --output tsv
$ApplicationInsightsConnectionString = az monitor app-insights component show `
    --app $ApplicationInsightsName `
    --resource-group $ApplicationInsightsResourceGroup `
    --query connectionString `
    --output tsv
$StorageAccountId = az storage account show `
    --name $StorageAccountName `
    --resource-group $ResourceGroup `
    --query id `
    --output tsv
$FoundryProjectId = "/subscriptions/$SubscriptionId/resourceGroups/$FoundryResourceGroup/providers/Microsoft.CognitiveServices/accounts/$FoundryAccountName/projects/$FoundryProjectName"

$EnvironmentVariables = @(
    "ENVIRONMENT=azure"
    "AGENT_RUNTIME_MODE=$AgentRuntimeMode"
    "FOUNDRY_PROJECT_ENDPOINT=$FoundryProjectEndpoint"
    "MODEL_DEPLOYMENT_NAME=$ModelDeploymentName"
    "FOUNDRY_AGENT_NAME=enterprise-integration-agent"
    "AZURE_TENANT_ID=$TenantId"
    "AZURE_SUBSCRIPTION_ID=$SubscriptionId"
    "AZURE_RESOURCE_GROUP=$FoundryResourceGroup"
    "AZURE_AI_ACCOUNT_NAME=$FoundryAccountName"
    "AZURE_AI_PROJECT_NAME=$FoundryProjectName"
    "MCP_EXECUTION_MODE=remote"
    "MOCK_MCP=false"
    "MCP_SERVER_NAME=enterpriseintegrationmcp"
    "MCP_SERVER_URL=$McpServerUrl"
    "MCP_TIMEOUT_SECONDS=30"
    "SECRET_PROVIDER=key_vault"
    "KEY_VAULT_URL=https://$KeyVaultName.vault.azure.net/"
    "MCP_API_KEY_SECRET_NAME=logic-apps-mcp-api-key"
    "PERSISTENCE_MODE=azure_table"
    "STORAGE_ACCOUNT_URL=https://$StorageAccountName.table.core.windows.net"
    "AUDIT_TABLE_NAME=AgentAuditEvents"
    "APPROVAL_REQUESTS_TABLE_NAME=AgentApprovalRequests"
    "APPROVAL_DECISIONS_TABLE_NAME=AgentApprovalDecisions"
    "APPLICATIONINSIGHTS_CONNECTION_STRING=$ApplicationInsightsConnectionString"
    "PORT=8000"
)

Write-Host ""
Write-Host "Enterprise Integration Agent - Container Apps deployment" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Mode:             $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host "Container App:    $AppName"
Write-Host "Resource group:   $ResourceGroup"
Write-Host "ACA environment:  $AcaEnvironmentName ($AcaEnvironmentResourceGroup)"
Write-Host "Image:            $Image"
Write-Host "Runtime mode:     $AgentRuntimeMode"
Write-Host "MCP server:       $McpServerUrl"
Write-Host ""
Write-Host "Managed identity roles:" -ForegroundColor Yellow
Write-Host "  Key Vault Secrets User -> $KeyVaultName"
Write-Host "  Storage Table Data Contributor -> $StorageAccountName"
Write-Host "  Azure AI Developer -> $FoundryProjectName"
Write-Host "  Monitoring Metrics Publisher -> $ApplicationInsightsName"
Write-Host ""

if (-not $Execute) {
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Run again with -Execute after reviewing this plan." -ForegroundColor Green
    exit 0
}

Write-Host "[1/6] Building image in Azure Container Registry..." -ForegroundColor Yellow
az acr build `
    --registry $AcrName `
    --image "${ImageName}:$ImageTag" `
    --file "$AgentDir\Dockerfile" `
    --no-logs `
    $RepoRoot

Write-Host "[2/6] Ensuring the project resource group exists..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none

$AppExists = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query name `
    --output tsv 2>$null

if ($AppExists) {
    Write-Host "[3/6] Updating Container App..." -ForegroundColor Yellow
    az containerapp update `
        --name $AppName `
        --resource-group $ResourceGroup `
        --image $Image `
        --set-env-vars $EnvironmentVariables `
        --output none
} else {
    Write-Host "[3/6] Creating Container App..." -ForegroundColor Yellow
    az containerapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --environment $AcaEnvironmentId `
        --image $Image `
        --registry-server "$AcrName.azurecr.io" `
        --ingress external `
        --target-port 8000 `
        --min-replicas 0 `
        --max-replicas 2 `
        --cpu 0.5 `
        --memory 1.0Gi `
        --system-assigned `
        --env-vars $EnvironmentVariables `
        --output none
}

$PrincipalId = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query identity.principalId `
    --output tsv

if ($SkipRoleAssignments) {
    Write-Host "[4/6] Reusing existing managed identity role assignments..." -ForegroundColor Yellow
}
else {
    Write-Host "[4/6] Assigning managed identity roles..." -ForegroundColor Yellow
    az role assignment create `
        --assignee-object-id $PrincipalId `
        --assignee-principal-type ServicePrincipal `
        --role "Key Vault Secrets User" `
        --scope $KeyVaultId `
        --output none
    az role assignment create `
        --assignee-object-id $PrincipalId `
        --assignee-principal-type ServicePrincipal `
        --role "Storage Table Data Contributor" `
        --scope $StorageAccountId `
        --output none
    az role assignment create `
        --assignee-object-id $PrincipalId `
        --assignee-principal-type ServicePrincipal `
        --role "Azure AI Developer" `
        --scope $FoundryProjectId `
        --output none
    az role assignment create `
        --assignee-object-id $PrincipalId `
        --assignee-principal-type ServicePrincipal `
        --role "Monitoring Metrics Publisher" `
        --scope $ApplicationInsightsId `
        --output none
}

Write-Host "[5/6] Restarting the active revision after RBAC assignment..." -ForegroundColor Yellow
$RevisionName = az containerapp revision list `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query "[?properties.active].name | [0]" `
    --output tsv
az containerapp revision restart `
    --name $AppName `
    --resource-group $ResourceGroup `
    --revision $RevisionName `
    --output none

Write-Host "[6/6] Fetching the live endpoint..." -ForegroundColor Yellow
$Fqdn = az containerapp show `
    --name $AppName `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv

Write-Host ""
Write-Host "Deployment complete." -ForegroundColor Green
Write-Host "Health endpoint: https://$Fqdn/health" -ForegroundColor White
Write-Host "Chat endpoint:   https://$Fqdn/agent/chat" -ForegroundColor White
