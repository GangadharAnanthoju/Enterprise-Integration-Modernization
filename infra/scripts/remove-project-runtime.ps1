param(
    [string]$ProjectResourceGroup = "rg-sysint-enterprise-integration-eus",
    [string]$LogicAppName = "la-sysint-enterprise-integration-eus",
    [string]$AppServicePlanName = "asp-sysint-enterprise-integration-eus",
    [string]$StorageAccountName = "stsysintintegeus001",
    [string]$ContainerAppName = "ca-sysint-enterprise-agent-eus",
    [string]$SharedResourceGroup = "rg-sysint-common-eus",
    [string]$ApimName = "apim-sysint-common-eus",
    [string]$ApimApiId = "enterprise-integration-agent",
    [string]$ApimProductId = "enterprise-integration-agents",
    [string]$ApimSubscriptionId = "enterprise-integration-agent-learning",
    [switch]$DeleteStorage,
    [switch]$DeleteApimArtifacts,
    [switch]$Execute,
    [string]$Confirmation
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$ExpectedConfirmation = "DELETE PROJECT RUNTIME"

Write-Host ""
Write-Host "Enterprise Integration Modernization - Runtime cleanup" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host ""
Write-Host "Always delete project-owned runtime compute:" -ForegroundColor Yellow
Write-Host "  Container App: $ContainerAppName"
Write-Host "  Logic App: $LogicAppName"
Write-Host "  WS1 plan: $AppServicePlanName"
Write-Host ""
Write-Host "Storage account: $StorageAccountName"
Write-Host "  Action: $(if ($DeleteStorage) { 'DELETE - durable audit and approval data will be lost' } else { 'KEEP' })"
Write-Host ""
Write-Host "Project-specific artifacts inside shared APIM: $ApimApiId / $ApimProductId"
Write-Host "  Action: $(if ($DeleteApimArtifacts) { 'DELETE artifacts only; shared APIM service remains' } else { 'KEEP' })"
Write-Host ""
Write-Host "Never deleted by this script:" -ForegroundColor Green
Write-Host "  Shared ACA environment, ACR, Key Vault, Foundry, App Insights, Log Analytics, APIM service"

if (-not $Execute) {
    Write-Host ""
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Execute only with:" -ForegroundColor Green
    Write-Host "  .\infra\scripts\remove-project-runtime.ps1 -Execute -Confirmation `"$ExpectedConfirmation`""
    exit 0
}

if ($Confirmation -ne $ExpectedConfirmation) {
    throw "Confirmation must exactly match: $ExpectedConfirmation"
}

if ($DeleteApimArtifacts) {
    Write-Host "[1/4] Removing project-specific APIM artifacts..." -ForegroundColor Yellow
    $AzureSubscriptionId = az account show --query id --output tsv
    $Token = az account get-access-token `
        --resource https://management.azure.com/ `
        --query accessToken `
        --output tsv
    $ManagementHeaders = @{ Authorization = "Bearer $Token" }
    $ApimResourceUrl = (
        "https://management.azure.com/subscriptions/$AzureSubscriptionId/" +
        "resourceGroups/$SharedResourceGroup/providers/Microsoft.ApiManagement/service/$ApimName"
    )
    Invoke-WebRequest `
        -Method Delete `
        -Uri "${ApimResourceUrl}/subscriptions/${ApimSubscriptionId}?api-version=2024-05-01" `
        -Headers $ManagementHeaders `
        -SkipHttpErrorCheck | Out-Null
    $ProductExists = az apim product list `
        --resource-group $SharedResourceGroup `
        --service-name $ApimName `
        --query "[?name=='$ApimProductId'].name | [0]" `
        --output tsv
    if ($ProductExists) {
        az apim product delete `
            --resource-group $SharedResourceGroup `
            --service-name $ApimName `
            --product-id $ApimProductId `
            --delete-subscriptions true `
            --yes `
            --output none
    }
    $ApiExists = az apim api list `
        --resource-group $SharedResourceGroup `
        --service-name $ApimName `
        --query "[?name=='$ApimApiId'].name | [0]" `
        --output tsv
    if ($ApiExists) {
        az apim api delete `
            --resource-group $SharedResourceGroup `
            --service-name $ApimName `
            --api-id $ApimApiId `
            --yes `
            --output none
    }
} else {
    Write-Host "[1/4] Keeping APIM artifacts." -ForegroundColor DarkGray
}

Write-Host "[2/4] Removing project Container App..." -ForegroundColor Yellow
$ContainerAppExists = az containerapp list `
    --resource-group $ProjectResourceGroup `
    --query "[?name=='$ContainerAppName'].name | [0]" `
    --output tsv
if ($ContainerAppExists) {
    $PrincipalId = az containerapp show `
        --name $ContainerAppName `
        --resource-group $ProjectResourceGroup `
        --query identity.principalId `
        --output tsv
    if ($PrincipalId) {
        az role assignment delete --assignee-object-id $PrincipalId
    }
    az containerapp delete `
        --name $ContainerAppName `
        --resource-group $ProjectResourceGroup `
        --yes `
        --output none
}

Write-Host "[3/4] Removing Logic App and WS1 plan..." -ForegroundColor Yellow
$LogicAppExists = az resource list `
    --resource-group $ProjectResourceGroup `
    --query "[?type=='Microsoft.Web/sites' && name=='$LogicAppName'].name | [0]" `
    --output tsv
if ($LogicAppExists) {
    az resource delete `
        --resource-group $ProjectResourceGroup `
        --resource-type "Microsoft.Web/sites" `
        --name $LogicAppName
}
$PlanExists = az resource list `
    --resource-group $ProjectResourceGroup `
    --query "[?type=='Microsoft.Web/serverfarms' && name=='$AppServicePlanName'].name | [0]" `
    --output tsv
if ($PlanExists) {
    az resource delete `
        --resource-group $ProjectResourceGroup `
        --resource-type "Microsoft.Web/serverfarms" `
        --name $AppServicePlanName
}

if ($DeleteStorage) {
    Write-Host "[4/4] Removing project storage and durable records..." -ForegroundColor Yellow
$StorageExists = az storage account list `
        --resource-group $ProjectResourceGroup `
        --query "[?name=='$StorageAccountName'].name | [0]" `
        --output tsv
    if ($StorageExists) {
        az storage account delete `
            --name $StorageAccountName `
            --resource-group $ProjectResourceGroup `
            --yes
    }
} else {
    Write-Host "[4/4] Keeping project storage and durable records." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Runtime cleanup complete." -ForegroundColor Green
