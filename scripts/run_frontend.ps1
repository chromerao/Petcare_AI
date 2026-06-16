param(
    [int]$Port = 5173
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "frontend"

if (-not (Test-Path $frontendRoot)) {
    throw "Frontend directory not found: $frontendRoot"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm was not found. Install Node.js 20+ and rerun: npm install"
}

Set-Location $frontendRoot

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    npm install
}

$env:VITE_DOCQA_API_BASE_URL = $env:VITE_DOCQA_API_BASE_URL
if (-not $env:VITE_DOCQA_API_BASE_URL) {
    $env:VITE_DOCQA_API_BASE_URL = "http://127.0.0.1:8000"
}

Write-Host "Starting PetCare AI frontend at http://127.0.0.1:$Port"
npm run dev -- --host 127.0.0.1 --port $Port
