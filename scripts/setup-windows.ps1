param(
    [string]$Namespace = "global",
    [int]$MaxChars = 6000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $RepoRoot ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

function Assert-NativeSuccess([string]$Step) {
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

if ($MaxChars -lt 0 -or $MaxChars -gt 100000) {
    throw "MaxChars must be between 0 and 100000."
}

if (-not (Test-Path $Python)) {
    $Launcher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $Launcher) {
        throw "Python launcher 'py' was not found. Install Python 3.11 or newer, then rerun."
    }
    & py -3 -m venv $Venv
    Assert-NativeSuccess "Creating the Python environment"
}

& $Python -m pip install -e $RepoRoot
Assert-NativeSuccess "Installing AiMemory"
& $Python -m aimemory install-opencode --global --update
Assert-NativeSuccess "Installing the OpenCode plugin"

$DataDirectory = Join-Path $env:LOCALAPPDATA "AiMemory"
$Database = Join-Path $DataDirectory "memory.sqlite3"
New-Item -ItemType Directory -Force -Path $DataDirectory | Out-Null

$Settings = @{
    AIMEMORY_PYTHON = $Python
    AIMEMORY_DB = $Database
    AIMEMORY_NAMESPACE = $Namespace
    AIMEMORY_MAX_CHARS = [string]$MaxChars
}

foreach ($Entry in $Settings.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($Entry.Key, $Entry.Value, "User")
    Set-Item -Path "Env:$($Entry.Key)" -Value $Entry.Value
}

& $Python -m aimemory doctor
Assert-NativeSuccess "AiMemory doctor"

$Plugin = Join-Path $env:USERPROFILE ".config\opencode\plugins\aimemory.js"
if (-not (Test-Path $Plugin)) {
    throw "Global OpenCode plugin was not installed."
}

Write-Host ""
Write-Host "AiMemory setup complete." -ForegroundColor Green
Write-Host "Plugin: $Plugin"
Write-Host "Database: $Database"
Write-Host "Namespace: $Namespace"
Write-Host "Close every OpenCode window, start OpenCode again, then send:"
Write-Host "#merken: AiMemory Funktionstest erfolgreich." -ForegroundColor Cyan
