@echo off
title FII ^& DII Live Server
color 0A
echo.
echo  ======================================
echo    FII ^& DII Live Data Server
echo    Starting on http://localhost:5000
echo  ======================================
echo.
cd /d "%~dp0"
python server.py
if errorlevel 1 (
  echo.
  echo  [ERROR] Python not found. Please install Python from https://python.org
  pause
)
