#!/bin/bash
echo "========================================"
echo "  AI Resume Screener - Startup Script"
echo "========================================"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 not found. Install from https://python.org"; exit 1
fi

# Check Node
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js not found. Install from https://nodejs.org"; exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Backend setup
echo "[1/4] Setting up Python virtual environment..."
cd "$ROOT_DIR/backend"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "[2/4] Installing Python dependencies..."
pip install -r requirements.txt -q

echo "[3/4] Downloading NLP models..."
python -m spacy download en_core_web_sm
python "$ROOT_DIR/scripts/download_models.py"

echo "[4/4] Seeding database..."
python "$ROOT_DIR/scripts/seed_db.py"

# Start backend in background
echo "[OK] Starting FastAPI backend..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

sleep 2

# Frontend setup
echo "[OK] Setting up React frontend..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend packages (first time, takes ~2 min)..."
    npm install
fi

echo "[OK] Starting React frontend..."
npm start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo " App is running!"
echo " Backend:  http://localhost:8000/docs"
echo " Frontend: http://localhost:3000"
echo " Login:    admin / admin@123"
echo " Press Ctrl+C to stop both servers"
echo "========================================"

# Wait and handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" INT
wait
