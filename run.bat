@echo off
echo ========================================================
echo        SENTINEL — Research Engine & Dashboard
echo ========================================================
echo.

:: Start Backend in background
echo [1/2] Starting SENTINEL Backend on http://localhost:8000...
start "SENTINEL Backend" cmd /k "cd backend && ..\venv\Scripts\python.exe run_backend.py"

:: Wait 2 seconds
timeout /t 2 >nul

:: Start Frontend
echo [2/2] Starting SENTINEL Frontend on http://localhost:5173...
start "SENTINEL Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services are launching!
echo Backend:  http://localhost:8000 (Docs: http://localhost:8000/docs)
echo Frontend: http://localhost:5173
echo.
pause
