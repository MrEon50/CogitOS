@echo off
title CogitOS Launcher
echo.
echo  [1/2] Uruchamianie rdzenia kognitywnego (server.py)...
echo.

rem Zamykamy ewentualne stare okno serwera po tytule, by uniknąć konfliktów portu
taskkill /f /fi "WINDOWTITLE eq CogitOS Backend Server*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Administrator: CogitOS Backend Server*" >nul 2>&1

rem Uruchomienie serwera w nowym oknie z określonym tytułem
start "CogitOS Backend Server" cmd /c "python server.py"

rem Oczekiwanie na start serwera (3 sekundy)
ping -n 4 127.0.0.1 > nul

echo  [2/2] Otwieranie interfejsu CogitOS...
echo.

rem Otwarcie przeglądarki na adresie serwera
start http://127.0.0.1:8800

echo Gotowe. Mozesz teraz zamknac to okno (serwer pracuje w tle).
pause
