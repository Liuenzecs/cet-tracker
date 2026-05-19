# CET Tracker — clean packaging script (Windows PowerShell)
# Run from project root: .\scripts\package_clean.ps1

$ErrorActionPreference = "Stop"
$OutputFile = "cet-tracker-clean.zip"
$ProjectRoot = (Get-Item .).FullName

Write-Host "CET Tracker — Clean Packaging" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot" -ForegroundColor Gray

# Remove old zip
if (Test-Path $OutputFile) {
    Remove-Item $OutputFile -Force
    Write-Host "Removed old $OutputFile" -ForegroundColor Gray
}

# Build exclusion list
$Exclude = @(
    ".git/*",
    ".claude/*",
    ".env",
    ".env.*",
    "!.env.example",
    "node_modules/*",
    ".venv/*",
    "venv/*",
    "__pycache__/*",
    ".pytest_cache/*",
    "dist/*",
    "apps/web/dist/*",
    "data/*.db",
    "data/*.sqlite",
    "data/*.sqlite3",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "Thumbs.db",
    "cet-tracker-clean.zip"
)

$Args = @("-r", $OutputFile, ".", "-x")
foreach ($e in $Exclude) {
    $Args += $e
}

# Try using 7z first, fallback to Compress-Archive
try {
    $7z = Get-Command "7z" -ErrorAction SilentlyContinue
    if ($7z) {
        & "$7z" a -tzip $OutputFile . -xr!.git -xr!.claude -xr!node_modules -xr!.venv -xr!__pycache__ -xr!.pytest_cache -xr!dist -xr!data/*.db -xr!.env -xr!*.pyc
        Write-Host "Packaged with 7z: $OutputFile" -ForegroundColor Green
        exit 0
    }
}
catch { }

# Fallback: Compress-Archive with individual file selection
Write-Host "Using Compress-Archive fallback..." -ForegroundColor Gray

$Files = Get-ChildItem -Recurse -File | Where-Object {
    $path = $_.FullName.Replace($ProjectRoot, "").Replace("\", "/")
    ($path -notmatch "/\.git/") -and
    ($path -notmatch "/\.claude/") -and
    ($path -notmatch "/node_modules/") -and
    ($path -notmatch "/\.venv/") -and
    ($path -notmatch "/venv/") -and
    ($path -notmatch "/__pycache__/") -and
    ($path -notmatch "/\.pytest_cache/") -and
    ($path -notmatch "/dist/") -and
    ($path -notmatch "/apps/web/dist/") -and
    ($path -notmatch "\.env$") -and
    ($path -notmatch "\.env\.") -and
    ($path -notmatch "\.db$") -and
    ($path -notmatch "\.sqlite$") -and
    ($path -notmatch "\.pyc$") -and
    ($path -notmatch "\.DS_Store$") -and
    ($path -notmatch "Thumbs\.db$")
}

Compress-Archive -Path $Files.FullName -DestinationPath $OutputFile -Force

Write-Host "Packaged: $OutputFile" -ForegroundColor Green
Write-Host "Size: $([math]::Round((Get-Item $OutputFile).Length / 1KB, 1)) KB" -ForegroundColor Gray
