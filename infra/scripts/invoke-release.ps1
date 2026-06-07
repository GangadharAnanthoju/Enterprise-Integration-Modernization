param(
    [ValidateSet("all", "logic-apps", "agent", "apim", "smoke-test")]
    [string]$Component = "all",
    [string]$ImageTag = "latest",
    [switch]$Execute,
    [string]$Confirmation
)

$ErrorActionPreference = "Stop"
$ExpectedConfirmation = "RELEASE DEV"

Write-Host ""
Write-Host "Enterprise Integration Modernization - Controlled release" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Mode:       $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host "Component:  $Component"
Write-Host "Image tag:  $ImageTag"
Write-Host ""
Write-Host "Release sequence:" -ForegroundColor Yellow
Write-Host "  validate -> Logic Apps -> agent image/runtime -> APIM -> smoke test"

if (-not $Execute) {
    Write-Host ""
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Execute only with -Execute -Confirmation `"$ExpectedConfirmation`"."
    exit 0
}

if ($Confirmation -ne $ExpectedConfirmation) {
    throw "Confirmation must exactly match: $ExpectedConfirmation"
}

& "$PSScriptRoot\validate-release-assets.ps1"

if ($Component -in @("all", "logic-apps")) {
    & "$PSScriptRoot\deploy-dev.ps1"
    & "$PSScriptRoot\publish-logicapps.ps1"
}

if ($Component -in @("all", "agent")) {
    & "$PSScriptRoot\deploy-agent-containerapp.ps1" `
        -ImageTag $ImageTag `
        -SkipRoleAssignments `
        -Execute
}

if ($Component -in @("all", "apim")) {
    & "$PSScriptRoot\deploy-agent-apim.ps1" -Execute
}

if ($Component -in @("all", "smoke-test")) {
    & "$PSScriptRoot\test-agent-apim.ps1"
}

Write-Host ""
Write-Host "Controlled release completed." -ForegroundColor Green
