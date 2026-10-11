@echo off
echo ===================================================================
echo Starting Wealth Advisor Assistant (Backend + Frontend)
echo ===================================================================
start "Wealth Advisor Backend (FastAPI)" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "Wealth Advisor Frontend (Streamlit)" cmd /k "call venv\Scripts\activate.bat && python -m streamlit run frontend/app.py --server.port 8501"
echo Services launched!
echo - Backend:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo - Frontend: http://localhost:8501
