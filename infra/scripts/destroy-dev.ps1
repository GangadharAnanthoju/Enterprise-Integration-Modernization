param(
    [string]$ResourceGroupName = "rg-sysint-enterprise-integration-eus",
    [string]$LogicAppName = "la-sysint-enterprise-integration-eus",
    [string]$AppServicePlanName = "asp-sysint-enterprise-integration-eus",
    [string]$StorageAccountName = "stsysintintegeus001"
)

Write-Host "This deletes the disposable Logic Apps Standard learning resources."
Write-Host "Resource group: $ResourceGroupName"
Write-Host "Logic App: $LogicAppName"
Write-Host "App Service plan: $AppServicePlanName"
Write-Host "Storage account: $StorageAccountName"

$confirmation = Read-Host "Type DELETE to continue"
if ($confirmation -ne "DELETE") {
    Write-Host "Delete cancelled."
    exit 0
}

az resource delete `
    --resource-group $ResourceGroupName `
    --resource-type "Microsoft.Web/sites" `
    --name $LogicAppName

az resource delete `
    --resource-group $ResourceGroupName `
    --resource-type "Microsoft.Web/serverfarms" `
    --name $AppServicePlanName

az resource delete `
    --resource-group $ResourceGroupName `
    --resource-type "Microsoft.Storage/storageAccounts" `
    --name $StorageAccountName
