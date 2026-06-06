param(
    [string]$ApimName = "apim-sysint-common-eus",
    [string]$ApimResourceGroup = "rg-sysint-common-eus",
    [string]$ApiId = "enterprise-integration-agent",
    [string]$ApiDisplayName = "Enterprise Integration Agent API",
    [string]$ApiPath = "enterprise-integration-agent",
    [string]$ProductId = "enterprise-integration-agents",
    [string]$ProductDisplayName = "Enterprise Integration Agents",
    [string]$SubscriptionName = "enterprise-integration-agent-learning",
    [string]$BackendUrl = "https://ca-sysint-enterprise-agent-eus.kindmushroom-93329cd8.eastus.azurecontainerapps.io",
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$env:PYTHONUTF8 = "1"
$env:AZURE_CORE_NO_COLOR = "1"

$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path
$OpenApiFile = Join-Path $RepoRoot "infra\apim\enterprise-agent-api.openapi.yaml"
$PolicyFile = Join-Path $RepoRoot "infra\apim\enterprise-agent-api-policy.xml"
$SubscriptionId = az account show --query id --output tsv
$ApimResourceId = az apim show `
    --name $ApimName `
    --resource-group $ApimResourceGroup `
    --query id `
    --output tsv
$GatewayUrl = az apim show `
    --name $ApimName `
    --resource-group $ApimResourceGroup `
    --query gatewayUrl `
    --output tsv
$ApiResourceId = "$ApimResourceId/apis/$ApiId"
$PolicyUri = "https://management.azure.com$ApiResourceId/policies/policy?api-version=2024-05-01"
$ProductApiUri = "https://management.azure.com$ApimResourceId/products/$ProductId/apis/${ApiId}?api-version=2024-05-01"
$LearningSubscriptionId = "enterprise-integration-agent-learning"
$LearningSubscriptionUri = "https://management.azure.com$ApimResourceId/subscriptions/${LearningSubscriptionId}?api-version=2024-05-01"
$ManagementToken = az account get-access-token `
    --resource https://management.azure.com/ `
    --query accessToken `
    --output tsv
$ManagementHeaders = @{
    Authorization = "Bearer $ManagementToken"
}

function Invoke-AzureManagementPut {
    param(
        [string]$Uri,
        [string]$Body = ""
    )

    $Parameters = @{
        Method = "Put"
        Uri = $Uri
        Headers = $ManagementHeaders
        ContentType = "application/json"
    }
    if ($Body) {
        $Parameters.Body = $Body
    }
    Invoke-RestMethod @Parameters | Out-Null
}

Write-Host ""
Write-Host "Enterprise Integration Agent - APIM deployment" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Mode:             $(if ($Execute) { 'EXECUTE' } else { 'PLAN ONLY' })"
Write-Host "APIM:             $ApimName"
Write-Host "API:              $ApiDisplayName ($ApiId)"
Write-Host "Gateway path:     /$ApiPath"
Write-Host "Backend:          $BackendUrl"
Write-Host "Product:          $ProductDisplayName ($ProductId)"
Write-Host "Subscription:     $SubscriptionName"
Write-Host ""
Write-Host "Policies:" -ForegroundColor Yellow
Write-Host "  Subscription key required"
Write-Host "  Consumption-compatible rate limit: 30 calls per minute per subscription"
Write-Host "  APIM subscription key removed before backend forwarding"
Write-Host "  X-Content-Type-Options response header"
Write-Host ""
Write-Host "Gateway URL: $GatewayUrl/$ApiPath" -ForegroundColor White
Write-Host ""

if (-not $Execute) {
    Write-Host "No Azure resources were changed." -ForegroundColor Green
    Write-Host "Run again with -Execute after reviewing this plan." -ForegroundColor Green
    exit 0
}

Write-Host "[1/5] Importing curated OpenAPI contract..." -ForegroundColor Yellow
az apim api import `
    --resource-group $ApimResourceGroup `
    --service-name $ApimName `
    --api-id $ApiId `
    --display-name $ApiDisplayName `
    --path $ApiPath `
    --protocols https `
    --service-url $BackendUrl `
    --specification-format OpenApi `
    --specification-path $OpenApiFile `
    --subscription-required true `
    --output none

Write-Host "[2/5] Applying API policy..." -ForegroundColor Yellow
$PolicyBody = @{
    properties = @{
        format = "rawxml"
        value = Get-Content -Raw $PolicyFile
    }
} | ConvertTo-Json -Depth 10 -Compress
Invoke-AzureManagementPut -Uri $PolicyUri -Body $PolicyBody

Write-Host "[3/5] Creating or updating the APIM product..." -ForegroundColor Yellow
$ProductExists = az apim product list `
    --resource-group $ApimResourceGroup `
    --service-name $ApimName `
    --query "[?name=='$ProductId'].name | [0]" `
    --output tsv 2>$null
if ($ProductExists) {
    az apim product update `
        --resource-group $ApimResourceGroup `
        --service-name $ApimName `
        --product-id $ProductId `
        --product-name $ProductDisplayName `
        --state published `
        --subscription-required true `
        --output none
} else {
    az apim product create `
        --resource-group $ApimResourceGroup `
        --service-name $ApimName `
        --product-id $ProductId `
        --product-name $ProductDisplayName `
        --state published `
        --subscription-required true `
        --output none
}

Write-Host "[4/5] Linking API to product..." -ForegroundColor Yellow
Invoke-AzureManagementPut -Uri $ProductApiUri

Write-Host "[5/5] Ensuring a learning subscription exists..." -ForegroundColor Yellow
$SubscriptionBody = @{
    properties = @{
        displayName = $SubscriptionName
        scope = "/products/$ProductId"
        state = "active"
    }
} | ConvertTo-Json -Depth 10 -Compress
Invoke-AzureManagementPut -Uri $LearningSubscriptionUri -Body $SubscriptionBody

Write-Host ""
Write-Host "APIM deployment complete." -ForegroundColor Green
Write-Host "Gateway health: $GatewayUrl/$ApiPath/health" -ForegroundColor White
Write-Host "Gateway chat:   $GatewayUrl/$ApiPath/agent/chat" -ForegroundColor White
Write-Host "Subscription keys were not printed." -ForegroundColor DarkGray
