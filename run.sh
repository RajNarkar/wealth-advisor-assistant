#!/usr/bin/env bash
# Startup script for Wealth Advisor Assistant
set -e

echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

echo "Starting FastAPI backend in background..."
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Starting Streamlit frontend..."
python -m streamlit run frontend/app.py --server.port 8501

kill $BACKEND_PID
