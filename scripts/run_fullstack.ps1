param(
    [int]$ApiPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendRoot = Join-Path $projectRoot "frontend"
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$npm = "npm"

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run: uv sync --all-extras --dev"
}

if (-not (Get-Command $npm -ErrorAction SilentlyContinue)) {
    $nodeInstall = "C:\Program Files\nodejs"
    if (Test-Path (Join-Path $nodeInstall "npm.cmd")) {
        $env:Path = "$nodeInstall;$env:Path"
        $npm = Join-Path $nodeInstall "npm.cmd"
    }
    else {
        throw "npm was not found. Install Node.js 20+ first."
    }
}

function Find-FreePort {
    param(
        [int]$PreferredPort,
        [int]$SearchLimit = 20
    )

    for ($candidate = $PreferredPort; $candidate -lt ($PreferredPort + $SearchLimit); $candidate++) {
        $occupied = Get-NetTCPConnection `
            -LocalPort $candidate `
            -State Listen `
            -ErrorAction SilentlyContinue
        if (-not $occupied) {
            return $candidate
        }
    }

    throw "No free port found from $PreferredPort to $($PreferredPort + $SearchLimit - 1)."
}

$resolvedApiPort = Find-FreePort -PreferredPort $ApiPort
$resolvedFrontendPort = Find-FreePort -PreferredPort $FrontendPort

if ($resolvedApiPort -ne $ApiPort) {
    Write-Warning "API port $ApiPort is occupied. Using $resolvedApiPort instead."
}
if ($resolvedFrontendPort -ne $FrontendPort) {
    Write-Warning "Frontend port $FrontendPort is occupied. Using $resolvedFrontendPort instead."
}

if (-not (Test-Path (Join-Path $frontendRoot "node_modules"))) {
    Write-Host "Installing frontend dependencies..."
    Push-Location $frontendRoot
    try {
        & $npm install
    }
    finally {
        Pop-Location
    }
}

$apiJob = Start-Job -ScriptBlock {
    param($Root, $Python, $Port)
    Set-Location $Root
    $env:PYTHONPATH = Join-Path $Root "src"
    & $Python -m uvicorn docqa.api.main:app --host 127.0.0.1 --port $Port
} -ArgumentList $projectRoot, $python, $resolvedApiPort

try {
    Push-Location $frontendRoot
    $env:VITE_DOCQA_API_BASE_URL = "http://127.0.0.1:$resolvedApiPort"
    Write-Host "API:      http://127.0.0.1:$resolvedApiPort"
    Write-Host "Frontend: http://127.0.0.1:$resolvedFrontendPort"
    Write-Host "Keep this terminal open. Press Ctrl+C to stop both servers."
    & $npm run dev -- --host 127.0.0.1 --port $resolvedFrontendPort
}
finally {
    Pop-Location
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
}
