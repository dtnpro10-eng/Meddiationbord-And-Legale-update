@echo off
title FLI - Legal and Recovery Online Dashboard
chcp 65001 >nul
cd /d "%~dp0"
python start_online.py
taskkill /f /im cloudflared.exe >nul 2>&1
pause
