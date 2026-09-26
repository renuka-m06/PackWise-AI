# PackWise AI - Automated Test Suite Runner (PowerShell)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Running PackWise AI Test Suite" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Run Python pytest suite
Write-Host "`n[1/3] Running Pytest Suite (Unit, Integration, Smoke)..." -ForegroundColor Yellow
python -m pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pytest suite failed!" -ForegroundColor Red
    exit 1
}

# 2. Run Verification script
Write-Host "`n[2/3] Running Verification Script..." -ForegroundColor Yellow
python scripts/verify_system.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "System verification checks failed!" -ForegroundColor Red
    exit 1
}

# 3. Run Frontend Build check
Write-Host "`n[3/3] Checking Frontend Production Build..." -ForegroundColor Yellow
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "ALL TESTS AND BUILDS COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
