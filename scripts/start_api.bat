@echo off
echo ========================================================
echo Demarrage du Hub Google Workspace & Gemini (FastAPI)
echo Documentation Swagger : http://localhost:8000/docs
echo ========================================================
set PYTHONPATH=%~dp0..\src;%PYTHONPATH%
uvicorn src.server:app --reload --port 8000
