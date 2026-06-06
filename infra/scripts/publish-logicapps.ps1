param(
    [string]$ResourceGroupName = "rg-sysint-enterprise-integration-eus",
    [string]$LogicAppName = "la-sysint-enterprise-integration-eus",
    [string]$ProjectPath = "$PSScriptRoot/../../logicapps/standard-app",
    [string]$PackageRoot = "$PSScriptRoot/../../.azure",
    [string[]]$WorkflowNames = @(
        "checkShipmentStatus",
        "createApprovalRequest",
        "createServiceNowTicket",
        "getOrderStatus",
        "queryIntegrationRunStatus",
        "SendEmailNotification",
        "sendSupplierNotification",
        "validateInvoice"
    )
)

Write-Host "Publishing Logic Apps workflows"
Write-Host "Logic App: $LogicAppName"
Write-Host "Resource group: $ResourceGroupName"

if (-not (Test-Path $PackageRoot)) {
    New-Item -ItemType Directory -Path $PackageRoot | Out-Null
}

$staging = Join-Path $PackageRoot "logicapp-package"
if (Test-Path $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
}

New-Item -ItemType Directory -Path $staging | Out-Null

Copy-Item -Path `
    (Join-Path $ProjectPath "host.json"), `
    (Join-Path $ProjectPath "connections.json"), `
    (Join-Path $ProjectPath "parameters.json"), `
    (Join-Path $ProjectPath "mcpservers.json") `
    -Destination $staging

foreach ($name in $WorkflowNames) {
    $source = Join-Path (Join-Path $ProjectPath $name) "workflow.json"
    $target = Join-Path $staging $name
    New-Item -ItemType Directory -Path $target | Out-Null
    Copy-Item -Path $source -Destination $target
}

$zipPath = Join-Path $PackageRoot "logicapp-standard.zip"
if (Test-Path $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zipPath

az functionapp deployment source config-zip `
    --resource-group $ResourceGroupName `
    --name $LogicAppName `
    --src $zipPath
