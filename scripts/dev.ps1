# CET Tracker Development Launcher (Windows PowerShell)
# Starts backend (FastAPI + uvicorn) and frontend (Vite) in separate windows.

Write-Host "🚀 Starting CET Tracker..."

# ---- Check prerequisites ----
$pythonOk = $false
try {
    $pyVer = python --version 2>&1
    Write-Host "  Python: $pyVer"
    $pythonOk = $true
} catch {
    Write-Host "  ERROR: Python not found on PATH" -ForegroundColor Red
}

$nodeOk = $false
try {
    $nodeVer = node --version 2>&1
    Write-Host "  Node.js: $nodeVer"
    $nodeOk = $true
} catch {
    Write-Host "  ERROR: Node.js not found on PATH" -ForegroundColor Red
}

if (-not $pythonOk -or -not $nodeOk) {
    Write-Host "Please install missing prerequisites and try again." -ForegroundColor Red
    exit 1
}

# ---- Resolve project root ----
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# ---- Start backend in a new window ----
Write-Host "Starting backend (FastAPI on http://127.0.0.1:8000) in new window..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\apps\api'; uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "  Backend window launched."

# ---- Brief pause to let backend start ----
Start-Sleep -Seconds 2

# ---- Start frontend in current window ----
$frontendPath = "$ProjectRoot\apps\web"

# Detect package manager
$usePnpm = $false
try { pnpm --version 2>&1 | Out-Null; $usePnpm = $true } catch {}

if ($usePnpm) {
    Write-Host "Starting frontend (Vite + pnpm) in current window..."
    Set-Location $frontendPath
    pnpm dev
} else {
    Write-Host "pnpm not found, falling back to npm..." -ForegroundColor Yellow
    Set-Location $frontendPath
    npm run dev
}
