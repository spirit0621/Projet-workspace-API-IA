@echo off
set PYTHONPATH=%~dp0src;%PYTHONPATH%
python "%~dp0src\google_assistant.py" %*
