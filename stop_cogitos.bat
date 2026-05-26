@echo off
title CogitOS Shutdown Sequence
echo.
echo  [!!!] ROZPOCZYNANIE PROCEDURY ZAMYKANIA COGITOS...
echo.

rem Zamykamy proces CogitOS po tytule okna
taskkill /f /fi "WINDOWTITLE eq CogitOS Backend Server*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Administrator: CogitOS Backend Server*" >nul 2>&1

echo.
echo  [OK] System CogitOS zostal zatrzymany.
echo.
pause
