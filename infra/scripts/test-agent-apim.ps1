param(
    [string]$ApimName = "apim-sysint-common-eus",
    [string]$ApimResourceGroup = "rg-sysint-common-eus",
    [string]$SubscriptionId = "enterprise-integration-agent-learning",
    [string]$GatewayUrl = "https://apim-sysint-common-eus.azure-api.net/enterprise-integration-agent"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$AzureSubscriptionId = az account show --query id --output tsv
$Token = az account get-access-token `
    --resource https://management.azure.com/ `
    --query accessToken `
    --output tsv
$ManagementHeaders = @{
    Authorization = "Bearer $Token"
}
$SubscriptionResourceUrl = (
    "https://management.azure.com/subscriptions/$AzureSubscriptionId/" +
    "resourceGroups/$ApimResourceGroup/providers/Microsoft.ApiManagement/" +
    "service/$ApimName/subscriptions/$SubscriptionId"
)
$Secrets = Invoke-RestMethod `
    -Method Post `
    -Uri "${SubscriptionResourceUrl}/listSecrets?api-version=2024-05-01" `
    -Headers $ManagementHeaders `
    -ContentType "application/json" `
    -Body "{}"
$GatewayHeaders = @{
    "Ocp-Apim-Subscription-Key" = $Secrets.primaryKey
}

$NoKeyResponse = Invoke-WebRequest `
    -Method Get `
    -Uri "$GatewayUrl/health" `
    -SkipHttpErrorCheck
$Health = Invoke-RestMethod `
    -Method Get `
    -Uri "$GatewayUrl/health" `
    -Headers $GatewayHeaders
$CorrelationId = "apim-test-$([guid]::NewGuid())"
$ChatBody = @{
    user_message = "Check order ORD-1001"
    correlation_id = $CorrelationId
    simulate_when_ready = $true
} | ConvertTo-Json
$Chat = Invoke-RestMethod `
    -Method Post `
    -Uri "$GatewayUrl/agent/chat" `
    -Headers $GatewayHeaders `
    -ContentType "application/json" `
    -Body $ChatBody

[pscustomobject]@{
    no_key_status = $NoKeyResponse.StatusCode
    health = $Health.status
    chat_status = $Chat.status
    selected_tool = $Chat.selected_tool
    execution_mode = $Chat.simulation_result.mode
    tool_status = $Chat.simulation_result.status
    correlation_id = $Chat.correlation_id
}
