param(
    [int]$Port = 8765
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run: uv sync --all-extras --dev"
}

$job = Start-Job -ScriptBlock {
    param($Root, $Python, $ApiPort)
    Set-Location $Root
    $env:PYTHONPATH = Join-Path $Root "src"
    & $Python -m uvicorn docqa.api.main:app --host 127.0.0.1 --port $ApiPort
} -ArgumentList $projectRoot, $python, $Port

try {
    $baseUrl = "http://127.0.0.1:$Port"
    $health = $null

    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        Start-Sleep -Milliseconds 500
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -TimeoutSec 2
            break
        }
        catch {
            # The API may still be starting.
        }
    }

    if ($null -eq $health) {
        throw "API server did not become ready."
    }

    $sources = Invoke-RestMethod -Uri "$baseUrl/api/v1/sources" -TimeoutSec 5
    $queryResponse = Invoke-RestMethod `
        -Uri "$baseUrl/api/v1/query" `
        -Method Post `
        -ContentType "application/json; charset=utf-8" `
        -Body '{"question":"\uC785\uC2E4 \uD655\uC778"}' `
        -TimeoutSec 5

    [pscustomobject]@{
        HealthStatus = $health.status
        Topic = $sources.topic_id
        SourceCount = $sources.sources.Count
        QueryStatus = 200
        QueryGrounded = $queryResponse.grounded
    } | Format-List

    if (
        $health.status -ne "ok" -or
        $sources.topic_id -ne "T12" -or
        $sources.sources.Count -lt 7 -or
        -not $queryResponse.grounded
    ) {
        throw "Smoke test returned an unexpected result."
    }

    Write-Host "Local smoke test passed. No paid API call was made."
}
finally {
    Stop-Job $job -ErrorAction SilentlyContinue
    Remove-Job $job -Force -ErrorAction SilentlyContinue
}
