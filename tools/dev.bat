@echo off
echo [START] Starting ArbitrageWizard development environment...

REM Function to handle cleanup on Ctrl+C
setlocal EnableDelayedExpansion

echo [FRONTEND] Starting frontend development server...
cd /d "%~dp0..\apps\frontend"
start "Frontend" cmd /k "npm run dev"

echo [BACKEND] Starting backend development server...
cd /d "%~dp0..\apps\backend-api"
start "Backend" cmd /k "conda activate arbitrage-wizard-backend && python -m uvicorn app.main:app --reload --port 8000"

echo.
echo [SUCCESS] All services started in separate windows!
echo [WEB] Frontend: http://localhost:5173
echo [API] Backend: http://localhost:8000
echo [DOCS] API Docs: http://localhost:8000/docs
echo.
echo Close the individual command windows to stop services.
pause