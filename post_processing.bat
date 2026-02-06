@echo off

REM Use the Python inside the venv to run your script
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"

REM Keep the window open so you can see output/errors
pause
