<#
.SYNOPSIS
    Installs the Hermes Cognition skill for Google Antigravity and Agentic LLM systems.

.DESCRIPTION
    Copies the hermes-cognition skill directory to the Antigravity global skill directory
    ($env:USERPROFILE\.gemini\config\skills) or a local project workspace (.agents\skills).

.PARAMETER Global
    Installs globally to $env:USERPROFILE\.gemini\config\skills\hermes-cognition (Default: $true).

.PARAMETER ProjectPath
    Path to a target project repository if installing locally into .agents\skills\.

.EXAMPLE
    .\scripts\install.ps1
    Installs hermes-cognition globally for all Antigravity workspaces.

.EXAMPLE
    .\scripts\install.ps1 -Global:$false -ProjectPath "C:\Projects\my-app"
    Installs hermes-cognition locally to the specified project.
#>

[CmdletBinding()]
param(
    [switch]$Global = $true,
    [string]$ProjectPath = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Join-Path (Split-Path -Parent $ScriptDir) "skills\hermes-cognition"

if (-not (Test-Path $SourceDir)) {
    Write-Error "Source skill directory not found at '$SourceDir'."
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GEMINI X HERMES - Autonomous Skill Installer (Windows)  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Global -and [string]::IsNullOrWhiteSpace($ProjectPath)) {
    $TargetBase = Join-Path $env:USERPROFILE ".gemini\config\skills"
    $TargetDir = Join-Path $TargetBase "hermes-cognition"
    Write-Host "[+] Target: Global Antigravity Config" -ForegroundColor Yellow
} else {
    if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
        $ProjectPath = Get-Location
    }
    $TargetBase = Join-Path $ProjectPath ".agents\skills"
    $TargetDir = Join-Path $TargetBase "hermes-cognition"
    Write-Host "[+] Target: Project Workspace ($ProjectPath)" -ForegroundColor Yellow
}

Write-Host "[*] Source path: $SourceDir"
Write-Host "[*] Destination: $TargetDir"

if (-not (Test-Path $TargetBase)) {
    Write-Host "[*] Creating target directory: $TargetBase"
    New-Item -ItemType Directory -Path $TargetBase -Force | Out-Null
}

if (Test-Path $TargetDir) {
    Write-Host "[!] Existing installation found. Updating files..." -ForegroundColor Yellow
}

Copy-Item -Path $SourceDir -Destination $TargetBase -Recurse -Force

if (Test-Path (Join-Path $TargetDir "SKILL.md")) {
    Write-Host "`n[SUCCESS] Hermes Cognition skill installed successfully!" -ForegroundColor Green
    Write-Host "Location: $TargetDir" -ForegroundColor Green
    Write-Host "`nAntigravity will now automatically discover 'hermes-cognition' on startup." -ForegroundColor Cyan
} else {
    Write-Error "Installation verification failed. SKILL.md not found in $TargetDir."
    exit 1
}
