param(
    [Parameter(Mandatory = $true)]
    [string]$ImageTag,
    [string]$ResourceGroup = "rg-sysint-enterprise-integration-eus",
    [string]$ContainerAppName = "ca-sysint-enterprise-agent-eus",
    [string]$AcrName = "acrsysintcommoneus",
    [string]$ImageName = "enterprise-integration-agent",
    [switch]$Execute,
    [string]$Confirmation
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$ExpectedConfirmation = "ROLLBACK AGENT"
$Image = "$AcrName.azurecr.io/${ImageName}:$ImageTag"

Write-Host ""
Write-Host "Enterprise Integration Agent - Container App rollback" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Mode:          $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host "Container App: $ContainerAppName"
Write-Host "Target image:  $Image"

if (-not $Execute) {
    Write-Host ""
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Execute only with -Execute -Confirmation `"$ExpectedConfirmation`"."
    exit 0
}

if ($Confirmation -ne $ExpectedConfirmation) {
    throw "Confirmation must exactly match: $ExpectedConfirmation"
}

$ImageExists = az acr repository show-tags `
    --name $AcrName `
    --repository $ImageName `
    --query "[?@=='$ImageTag'] | [0]" `
    --output tsv
if (-not $ImageExists) {
    throw "Rollback image tag does not exist in ACR: $Image"
}

az containerapp update `
    --name $ContainerAppName `
    --resource-group $ResourceGroup `
    --image $Image `
    --output none

$Fqdn = az containerapp show `
    --name $ContainerAppName `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv

$Health = Invoke-RestMethod -Method Get -Uri "https://$Fqdn/health"
if ($Health.status -ne "ok") {
    throw "Rollback health check failed."
}

Write-Host "Rollback completed and health check passed." -ForegroundColor Green
