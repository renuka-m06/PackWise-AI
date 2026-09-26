#!/usr/bin/env bash
# PackWise AI - Local Development Launcher (Bash)
set -e

echo "============================================================"
echo "Starting PackWise AI Local Development Environment"
echo "============================================================"

# Start Backend
echo "[1/2] Starting FastAPI backend on http://127.0.0.1:8000..."
(python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

# Start Frontend
echo "[2/2] Starting Vite React frontend on http://127.0.0.1:5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
