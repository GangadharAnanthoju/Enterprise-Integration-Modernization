param(
    [string]$ResourceGroupName = "rg-sysint-enterprise-integration-eus",
    [string]$Location = "swedencentral",
    [string]$TemplateFile = "$PSScriptRoot/../main.bicep",
    [string]$ParametersFile = "$PSScriptRoot/../parameters.dev.json"
)

Write-Host "Deploying disposable Logic Apps Standard learning environment"
Write-Host "Resource group: $ResourceGroupName"
Write-Host "Location: $Location"

az group show --name $ResourceGroupName --output none

az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters "@$ParametersFile" `
    --parameters location=$Location
