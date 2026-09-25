@echo off
setlocal
cd /d "%~dp0"
if not exist "dist\index.html" (
  echo Build first using build-standalone.bat
  exit /b 1
)
start "" "%~dp0dist\index.html"
