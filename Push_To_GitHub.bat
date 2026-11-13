@echo off
title Push Project to GitHub
color 0A
set "PATH=%USERPROFILE%\mingit\cmd;%PATH%"
cd /d "%~dp0"

echo ========================================================
echo        FLI Legal Dashboard - Push to GitHub
echo ========================================================
echo.
echo Checking GitHub authentication...

gh auth status >nul 2>&1
if errorlevel 1 (
    echo [Step 1] Logging into GitHub...
    echo.
    echo A one-time code will appear below and your browser will open.
    echo Enter the code in your browser to authorize.
    echo.
    gh auth login -p https -w
    gh auth setup-git
)

echo.
echo [Step 2] Uploading project files to GitHub...
git remote set-url origin https://github.com/dtnpro10-eng/Meddiationbord-And-Legale-update.git
git add .
git commit -m "Upload FLI Legal Dashboard files" >nul 2>&1
git branch -M main
git push -u origin main

if errorlevel 0 (
    echo.
    echo ========================================================
    echo      SUCCESS! Project uploaded to GitHub:
    echo      https://github.com/dtnpro10-eng/Meddiationbord-And-Legale-update
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed. Please check your internet connection or login.
)

echo.
pause
