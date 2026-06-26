@echo off
echo ========================================
echo   AI Resume Screener - Startup Script
echo ========================================

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Download from https://python.org
    pause & exit /b 1
)

REM --- Check Node ---
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Download from https://nodejs.org
    pause & exit /b 1
)

echo [1/4] Setting up Python virtual environment...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo [2/4] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo [3/4] Downloading NLP models...
python -m spacy download en_core_web_sm
python ..\scripts\download_models.py

echo [4/4] Seeding database (admin user)...
python ..\scripts\seed_db.py

echo.
echo [OK] Backend ready. Starting FastAPI server...
start cmd /k "cd /d %~dp0backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [OK] Starting React frontend...
cd ..\frontend
if not exist node_modules (
    echo Installing frontend packages...
    npm install
)
start cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo ========================================
echo  App is starting!
echo  Backend:  http://localhost:8000/docs
echo  Frontend: http://localhost:3000
echo  Login:    admin / admin@123
echo ========================================
pause
