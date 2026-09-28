<#
.SYNOPSIS
    Installs Hermes Cognition and Switch-AGY skills for Google Antigravity and Agentic LLM systems.

.DESCRIPTION
    Copies skill directories to the Antigravity global skill directory
    ($env:USERPROFILE\.gemini\config\skills) or a local project workspace (.agents\skills),
    and installs CLI binaries to $env:LOCALAPPDATA\agy\bin.

.PARAMETER Global
    Installs globally to $env:USERPROFILE\.gemini\config\skills (Default: $true).

.PARAMETER ProjectPath
    Path to a target project repository if installing locally into .agents\skills\.

.EXAMPLE
    .\scripts\install.ps1
    Installs all skills globally for all Antigravity workspaces.
#>

[CmdletBinding()]
param(
    [switch]$Global = $true,
    [string]$ProjectPath = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$SkillsSource = Join-Path $RepoRoot "skills"

if (-not (Test-Path $SkillsSource)) {
    Write-Error "Source skills directory not found at '$SkillsSource'."
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   GEMINI X HERMES - Autonomous Skill Installer (Windows)  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Global -and [string]::IsNullOrWhiteSpace($ProjectPath)) {
    $TargetBase = Join-Path $env:USERPROFILE ".gemini\config\skills"
    Write-Host "[+] Target: Global Antigravity Config ($TargetBase)" -ForegroundColor Yellow
} else {
    if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
        $ProjectPath = Get-Location
    }
    $TargetBase = Join-Path $ProjectPath ".agents\skills"
    Write-Host "[+] Target: Project Workspace ($ProjectPath)" -ForegroundColor Yellow
}

if (-not (Test-Path $TargetBase)) {
    Write-Host "[*] Creating target directory: $TargetBase"
    New-Item -ItemType Directory -Path $TargetBase -Force | Out-Null
}

# Install each skill from skills/
Get-ChildItem -Path $SkillsSource -Directory | ForEach-Object {
    $skillName = $_.Name
    $destDir = Join-Path $TargetBase $skillName
    Write-Host "[*] Installing skill: $skillName -> $destDir"
    Copy-Item -Path $_.FullName -Destination $TargetBase -Recurse -Force
}

# Also ensure switch-agy CLI tools are placed in agy bin directory
$AgyBin = Join-Path $env:LOCALAPPDATA "agy\bin"
$SwitchAgyScripts = Join-Path $SkillsSource "switch-agy\scripts"
if (Test-Path $SwitchAgyScripts) {
    if (-not (Test-Path $AgyBin)) {
        New-Item -ItemType Directory -Path $AgyBin -Force | Out-Null
    }
    Write-Host "[*] Installing switch-agy CLI binaries to $AgyBin" -ForegroundColor Yellow
    Copy-Item -Path "$SwitchAgyScripts\*" -Destination $AgyBin -Force
}

Write-Host "`n[SUCCESS] All skills installed successfully!" -ForegroundColor Green
Write-Host "Antigravity will now automatically discover 'hermes-cognition' and 'switch-agy'." -ForegroundColor Cyan
