@echo off
title AgriSense AI Launcher
cd /d "%~dp0"
"C:\Users\OM\AppData\Local\Python\pythoncore-3.14-64\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
