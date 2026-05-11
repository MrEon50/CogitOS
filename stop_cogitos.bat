@echo off
title CogitOS Shutdown Sequence
echo.
echo  [!!!] ROZPOCZYNANIE PROCEDURY ZAMYKANIA COGITOS...
echo.

:: 1. Zamkniecie serwera Pythona
echo  [-] Zamykanie rdzenia kognitywnego (Python)...
taskkill /f /im python.exe /t >nul 2>&1

:: 2. Zamkniecie okien CMD o konkretnych tytulach (jesli istnieja)
echo  [-] Zamykanie terminali...
taskkill /f /fi "windowtitle eq CogitOS Backend Server" >nul 2>&1

:: 3. Zamkniecie przegladarek (Chrome, Edge, Firefox)
echo  [-] Zamykanie przegladarek (czyszczenie interfejsu)...
taskkill /f /im chrome.exe >nul 2>&1
taskkill /f /im msedge.exe >nul 2>&1
taskkill /f /im firefox.exe >nul 2>&1

echo.
echo  [OK] System zostal w pelni zatrzymany. RAM wyczyszczony.
echo.
pause
