param(
    [int]$ApiPort = 8000,
    [int]$UiPort = 8501
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

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

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run: uv sync --all-extras --dev"
}

$resolvedApiPort = Find-FreePort -PreferredPort $ApiPort
$resolvedUiPort = Find-FreePort -PreferredPort $UiPort

if ($resolvedApiPort -ne $ApiPort) {
    Write-Warning "API port $ApiPort is occupied. Using $resolvedApiPort instead."
}
if ($resolvedUiPort -ne $UiPort) {
    Write-Warning "UI port $UiPort is occupied. Using $resolvedUiPort instead."
}

$apiJob = Start-Job -ScriptBlock {
    param($Root, $Python, $Port)
    Set-Location $Root
    $env:PYTHONPATH = Join-Path $Root "src"
    & $Python -m uvicorn docqa.api.main:app --host 127.0.0.1 --port $Port
} -ArgumentList $projectRoot, $python, $resolvedApiPort

try {
    $env:DOCQA_API_BASE_URL = "http://127.0.0.1:$resolvedApiPort"
    Write-Host "Starting DocQA T12 at http://127.0.0.1:$resolvedUiPort"
    Write-Host "Keep this terminal open. Press Ctrl+C to stop the API and UI."
    & $python -m streamlit run (Join-Path $projectRoot "ui\app.py") `
        --server.port $resolvedUiPort `
        --server.address 127.0.0.1
}
finally {
    Stop-Job $apiJob -ErrorAction SilentlyContinue
    Remove-Job $apiJob -Force -ErrorAction SilentlyContinue
}
