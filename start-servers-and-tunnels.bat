@echo off
title YouTube APIs + Cloudflare Tunnels Launcher
cd /d "%~dp0"

set CLOUDFLARED="C:\Program Files (x86)\cloudflared\cloudflared.exe"

echo Starting Transcript API (FastAPI) on http://localhost:8000 ...
start "Transcript API - port 8000" cmd /k "cd /d "%~dp0" && python -m uvicorn main:app --reload --port 8000"

echo Starting Heatmap API (Express) on http://localhost:3000 ...
start "Heatmap API - port 3000" cmd /k "cd /d "%~dp0youtube-heatmap-api" && npm run dev"

echo Waiting a few seconds for both servers to come up...
timeout /t 5 >nul

echo Starting Cloudflare tunnel for Transcript API ...
start "Tunnel - Transcript API" cmd /k %CLOUDFLARED% tunnel --url http://localhost:8000

echo Starting Cloudflare tunnel for Heatmap API ...
start "Tunnel - Heatmap API" cmd /k %CLOUDFLARED% tunnel --url http://localhost:3000

echo.
echo Four windows just opened:
echo   1. Transcript API   (local)  - http://localhost:8000
echo   2. Heatmap API      (local)  - http://localhost:3000
echo   3. Tunnel for Transcript API - look for the *.trycloudflare.com URL inside it
echo   4. Tunnel for Heatmap API    - look for the *.trycloudflare.com URL inside it
echo.
echo Keep all 4 windows open while you use the APIs.
echo This window will close in 8 seconds...
timeout /t 8 >nul
