@echo off
title CogitOS Launcher
echo.
echo  [1/2] Uruchamianie rdzenia kognitywnego (server.py)...
echo.

:: Zamkniecie ewentualnie wiszacych procesow Pythona (czyszczenie RAM)
taskkill /f /im python.exe /t >nul 2>&1

:: Uruchomienie serwera w nowym oknie
start "CogitOS Backend Server" cmd /k "python server.py"

:: Oczekiwanie na start serwera (3 sekundy)
timeout /t 3 /nobreak > nul

echo  [2/2] Otwieranie interfejsu CogitOS...
echo.

:: Otwarcie przegladarki na adresie serwera
start http://127.0.0.1:8800

echo Gotowe. Mozesz teraz zamknac to okno (serwer pracuje w tle).
pause
