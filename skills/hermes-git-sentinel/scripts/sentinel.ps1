<#
.SYNOPSIS
    Hermes Git Sentinel - Quality Gate Runner
.DESCRIPTION
    Runs Hermes Sentinel to audit staged or working tree changes before committing.
.EXAMPLE
    .\sentinel.ps1
    .\sentinel.ps1 -All
    .\sentinel.ps1 -InstallHook
#>
param (
    [string]$Repo = ".",
    [switch]$All,
    [double]$MinScore = 80.0,
    [switch]$InstallHook
)

$PythonExe = "C:\Users\purnomo\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
$SentinelPy = "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.py"

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

$Arguments = @($SentinelPy, "--repo", $Repo, "--min-score", $MinScore)

if ($All) {
    $Arguments += "--all"
} else {
    $Arguments += "--staged"
}

if ($InstallHook) {
    $Arguments += "--install-hook"
}

& $PythonExe $Arguments
exit $LASTEXITCODE
