param(
    [switch]$SkipBicepBuild
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..").Path

Write-Host "Validating release assets" -ForegroundColor Cyan

$RequiredFiles = @(
    "agent/Dockerfile"
    "agent/requirements.txt"
    "infra/main.bicep"
    "infra/parameters.dev.json"
    "infra/apim/enterprise-agent-api.openapi.yaml"
    "infra/apim/enterprise-agent-api-policy.xml"
    "logicapps/standard-app/host.json"
    "logicapps/standard-app/mcpservers.json"
    ".github/workflows/ci.yml"
    ".github/workflows/release-dev.yml"
    ".github/workflows/rollback-agent.yml"
)

foreach ($RelativePath in $RequiredFiles) {
    $Path = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required release asset is missing: $RelativePath"
    }
}

Write-Host "[1/4] Validating PowerShell syntax..."
$PowerShellFiles = Get-ChildItem -Path (Join-Path $RepoRoot "infra/scripts") -Filter "*.ps1"
foreach ($File in $PowerShellFiles) {
    $Tokens = $null
    $ParseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile(
        $File.FullName,
        [ref]$Tokens,
        [ref]$ParseErrors
    )
    if ($ParseErrors.Count -gt 0) {
        throw "PowerShell syntax validation failed for $($File.Name): $ParseErrors"
    }
}

Write-Host "[2/4] Validating JSON assets..."
$JsonRoots = @(
    (Join-Path $RepoRoot "infra"),
    (Join-Path $RepoRoot "logicapps/workflows"),
    (Join-Path $RepoRoot "logicapps/standard-app")
)
$JsonFiles = foreach ($Root in $JsonRoots) {
    Get-ChildItem -Path $Root -Filter "*.json" -File -Recurse |
        Where-Object {
            $_.Name -ne "local.settings.json" -and
            $_.FullName -notmatch "workflow-designtime|__blobstorage__|__queuestorage__"
        }
}
foreach ($File in $JsonFiles) {
    try {
        Get-Content -Raw -LiteralPath $File.FullName | ConvertFrom-Json | Out-Null
    }
    catch {
        throw "JSON validation failed for $($File.FullName): $($_.Exception.Message)"
    }
}

Write-Host "[3/4] Validating MCP workflow registration..."
$McpConfig = Get-Content -Raw (Join-Path $RepoRoot "logicapps/standard-app/mcpservers.json") |
    ConvertFrom-Json
$RegisteredTools = @($McpConfig.mcpServers[0].tools.name)
foreach ($ToolName in $RegisteredTools) {
    $WorkflowFile = Join-Path $RepoRoot "logicapps/standard-app/$ToolName/workflow.json"
    if (-not (Test-Path -LiteralPath $WorkflowFile)) {
        throw "MCP tool '$ToolName' has no Standard workflow at $WorkflowFile"
    }
}

if ($SkipBicepBuild) {
    Write-Host "[4/4] Skipping Bicep build by request."
}
elseif (Get-Command az -ErrorAction SilentlyContinue) {
    Write-Host "[4/4] Building Bicep template..."
    az bicep build --file (Join-Path $RepoRoot "infra/main.bicep") --stdout | Out-Null
}
else {
    throw "Azure CLI is required for Bicep validation. Use -SkipBicepBuild only for local syntax checks."
}

Write-Host "Release asset validation passed." -ForegroundColor Green
