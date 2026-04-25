@echo off
echo ==========================================
echo   Vibe Trading AI - Daily Scanner
echo ==========================================
echo.
echo Starting Python engine...
start "Vibe API" cmd /k "cd /d C:\Work\Developments\vercel-trading-app && python run_local_api.py"
timeout /t 3 /nobreak > nul
echo Starting Next.js dashboard...
start "Vibe Dashboard" cmd /k "cd /d C:\Work\Developments\vercel-trading-app && cmd /c npm run dev"
timeout /t 5 /nobreak > nul
echo Opening browser...
start "" "http://localhost:3000"
echo.
echo Done! Scanner is running at http://localhost:3000
echo Click "Run AI Scanner" to get today's setups.
pause
