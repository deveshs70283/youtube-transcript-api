@echo off
title YouTube APIs Launcher
cd /d "%~dp0"

echo Starting Transcript API (FastAPI) on http://localhost:8000 ...
start "Transcript API - port 8000" cmd /k "cd /d "%~dp0" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Heatmap API (Express) on http://localhost:3000 ...
start "Heatmap API - port 3000" cmd /k "cd /d "%~dp0youtube-heatmap-api" && npm run dev"

echo.
echo Both servers are starting in their own windows:
echo   Transcript API:  http://localhost:8000
echo   Heatmap API:     http://localhost:3000
echo.
echo Leave those two windows open while you use the APIs.
echo Close them (or press Ctrl+C inside them) to stop the servers.
echo.
echo This window will close in 5 seconds...
timeout /t 5 >nul
