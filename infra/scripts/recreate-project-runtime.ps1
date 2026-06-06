param(
    [string]$ContainerImageTag = "recreated",
    [switch]$Execute
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

Write-Host ""
Write-Host "Enterprise Integration Modernization - Runtime recreation" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host ""
Write-Host "Recreation order:" -ForegroundColor Yellow
Write-Host "  1. Deploy Logic Apps Standard infrastructure from Bicep"
Write-Host "  2. Publish Logic Apps workflows and MCP server metadata"
Write-Host "  3. Verify or regenerate the Logic Apps MCP API key in Key Vault"
Write-Host "  4. Deploy FastAPI Container App with managed identity"
Write-Host "  5. Deploy APIM API, policy, product, and learning subscription"
Write-Host "  6. Run the APIM end-to-end verification"

if (-not $Execute) {
    Write-Host ""
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Run again with -Execute after confirming the MCP API key strategy." -ForegroundColor Green
    exit 0
}

Push-Location $RepoRoot
try {
    & "$PSScriptRoot\deploy-dev.ps1"
    & "$PSScriptRoot\publish-logicapps.ps1"

    Write-Host ""
    Write-Host "Manual checkpoint required." -ForegroundColor Yellow
    Write-Host "Confirm the recreated Logic Apps MCP API key is stored in Key Vault secret:"
    Write-Host "  logic-apps-mcp-api-key"
    $Confirmation = Read-Host "Type MCP KEY READY to continue"
    if ($Confirmation -ne "MCP KEY READY") {
        throw "Recreation stopped before Container App deployment."
    }

    & "$PSScriptRoot\deploy-agent-containerapp.ps1" `
        -Execute `
        -ImageTag $ContainerImageTag
    & "$PSScriptRoot\deploy-agent-apim.ps1" -Execute
    & "$PSScriptRoot\test-agent-apim.ps1"
}
finally {
    Pop-Location
}
