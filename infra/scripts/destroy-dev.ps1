param(
    [switch]$DeleteStorage,
    [switch]$DeleteApimArtifacts,
    [switch]$Execute,
    [string]$Confirmation
)

Write-Warning "destroy-dev.ps1 now delegates to the guarded project runtime cleanup script."

& "$PSScriptRoot\remove-project-runtime.ps1" `
    -DeleteStorage:$DeleteStorage `
    -DeleteApimArtifacts:$DeleteApimArtifacts `
    -Execute:$Execute `
    -Confirmation $Confirmation
