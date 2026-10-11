@echo off
echo ===================================================
echo Starting Wealth Advisor Assistant - Backend (FastAPI)
echo URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo ===================================================
call venv\Scripts\activate.bat
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
