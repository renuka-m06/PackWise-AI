# PackWise AI - Local Development Launcher (PowerShell)
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting PackWise AI Local Development Environment" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Start Backend in separate process or background
Write-Host "[1/2] Launching FastAPI Backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

# 2. Start Frontend in separate process or current
Write-Host "[2/2] Launching Vite React Frontend on http://localhost:5173..." -ForegroundColor Yellow
Set-Location frontend
npm run dev
