@echo off
TITLE TruthLens - Multimodal Digital Forensics System
COLOR 0A

echo ============================================================
echo         TRUTHLENS - DEEPFAKE DETECTION SYSTEM
echo         Member 3: Audio & Text Forensics Module
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python virtual environment...
if not exist "backend\.venv\Scripts\python.exe" (
    echo Error: Virtual environment not found at backend\.venv
    echo Please create it and install requirements: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [2/3] Starting FastAPI Backend on http://localhost:8000 ...
start "TruthLens Backend (FastAPI)" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Starting Streamlit Forensics UI on http://localhost:8501 ...
start "TruthLens Forensics UI (Streamlit)" cmd /k "backend\.venv\Scripts\python.exe -m streamlit run app_audio_forensics.py --server.port 8501"

echo.
echo ============================================================
echo All TruthLens servers started successfully!
echo.
echo   Forensics Dashboard: http://localhost:8501
echo   Backend API:         http://localhost:8000
echo   API Docs:            http://localhost:8000/docs
echo ============================================================
echo.
pause
