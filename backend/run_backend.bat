@echo off
echo ========================================
echo Starting Smart Camera Backend
echo ========================================
echo.
echo Backend will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --port 8000
