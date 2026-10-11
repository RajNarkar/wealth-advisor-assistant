@echo off
echo ===================================================
echo Starting Wealth Advisor Assistant - Frontend (Streamlit)
echo URL: http://localhost:8501
echo ===================================================
call venv\Scripts\activate.bat
python -m streamlit run frontend/app.py --server.port 8501
pause
