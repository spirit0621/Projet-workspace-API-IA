@echo off
set PYTHONPATH=%~dp0..\src;%PYTHONPATH%
python "%~dp0..\src\google_assistant.py" %*
