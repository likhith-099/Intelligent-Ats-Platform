@echo off
REM Start FastAPI using Python module syntax (works without virtual env issues)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload