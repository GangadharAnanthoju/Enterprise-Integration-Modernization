param(
    [string]$ProjectResourceGroup = "rg-sysint-enterprise-integration-eus",
    [string]$SharedResourceGroup = "rg-sysint-common-eus",
    [string]$ContainerAppName = "ca-sysint-enterprise-agent-eus",
    [string]$ApimName = "apim-sysint-common-eus",
    [string]$ApimApiId = "enterprise-integration-agent",
    [string]$ApimProductId = "enterprise-integration-agents"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Enterprise Integration Modernization - Azure cost posture" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Project-owned resources:" -ForegroundColor Yellow
az resource list `
    --resource-group $ProjectResourceGroup `
    --query "[].{name:name,type:type,location:location,sku:sku.name}" `
    --output table

Write-Host ""
Write-Host "Container App scale configuration:" -ForegroundColor Yellow
az containerapp show `
    --name $ContainerAppName `
    --resource-group $ProjectResourceGroup `
    --query "{name:name,minReplicas:properties.template.scale.minReplicas,maxReplicas:properties.template.scale.maxReplicas,runningStatus:properties.runningStatus}" `
    --output table

Write-Host ""
Write-Host "Project-specific APIM artifacts in shared APIM:" -ForegroundColor Yellow
az apim api list `
    --service-name $ApimName `
    --resource-group $SharedResourceGroup `
    --query "[?name=='$ApimApiId'].{name:name,path:path,subscriptionRequired:subscriptionRequired}" `
    --output table
az apim product list `
    --service-name $ApimName `
    --resource-group $SharedResourceGroup `
    --query "[?name=='$ApimProductId'].{name:name,state:state,subscriptionRequired:subscriptionRequired}" `
    --output table

Write-Host ""
Write-Host "Cost interpretation:" -ForegroundColor Yellow
Write-Host "  WS1 Workflow Standard plan: bills while it exists; delete it for real idle savings."
Write-Host "  Container App: configured for minReplicas=0; idle compute can scale to zero."
Write-Host "  Storage: low ongoing storage/transaction cost; deleting loses audit and approval data."
Write-Host "  Shared APIM/ACR/Key Vault/Foundry/monitoring: do not delete from this project."
