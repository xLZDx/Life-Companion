<#
.SYNOPSIS
    Local dev restart for Life Companion backend.
.DESCRIPTION
    Kills any running uvicorn or python processes for this project, ensures venv
    is present, then relaunches the FastAPI app with auto-reload on port 8000.
    Logs to logs/backend.log.
.NOTES
    ASCII-only body, UTF-8 with BOM per Windows script encoding rule.
    Run from the project root: .\restart.ps1
#>

param(
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "backend.log"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "[restart] Killing previous uvicorn processes (if any)..." -ForegroundColor Cyan
Get-Process -Name "python", "uvicorn" -ErrorAction SilentlyContinue |
    Where-Object {
        try { $_.Path -and $_.Path.StartsWith($ProjectRoot, [StringComparison]::OrdinalIgnoreCase) }
        catch { $false }
    } |
    ForEach-Object {
        Write-Host "[restart] Stopping PID $($_.Id) ($($_.Name))" -ForegroundColor Yellow
        try { Stop-Process -Id $_.Id -Force -ErrorAction Stop } catch {}
    }

if (-not (Test-Path $VenvPython)) {
    Write-Host "[restart] ERROR: venv missing. Create with:" -ForegroundColor Red
    Write-Host "    python -m venv venv" -ForegroundColor Yellow
    Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "    pip install -r requirements-dev.txt" -ForegroundColor Yellow
    exit 1
}

$uvicornArgs = @("-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "$Port")
if (-not $NoReload.IsPresent) { $uvicornArgs += "--reload" }

Write-Host "[restart] Starting uvicorn on port $Port (log: $LogFile)..." -ForegroundColor Green

$startArgs = @{
    FilePath = $VenvPython
    ArgumentList = $uvicornArgs
    WorkingDirectory = $ProjectRoot
    RedirectStandardOutput = $LogFile
    RedirectStandardError = (Join-Path $LogDir "backend.err.log")
    PassThru = $true
    WindowStyle = "Minimized"
}

$proc = Start-Process @startArgs
Write-Host "[restart] uvicorn started, PID $($proc.Id)" -ForegroundColor Green
Write-Host "[restart] Tail logs: Get-Content -Wait $LogFile" -ForegroundColor Cyan
