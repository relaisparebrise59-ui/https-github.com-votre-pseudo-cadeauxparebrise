@echo off
cd /d "%~dp0"
echo Demarrage du serveur local...
start "" cmd /c "timeout /t 1 >nul & start "" http://localhost:8080/"
py -m http.server 8080
