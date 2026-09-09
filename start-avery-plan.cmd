@echo off
setlocal
title Avery Plan - keep this window open
cd /d "%~dp0"

rem Windows ships a "python" stub that only offers to install from the Store,
rem and it can win on PATH. So test each candidate actually runs before using it.
set "PY="
for %%C in ("%USERPROFILE%\anaconda3\python.exe" "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "%LOCALAPPDATA%\Programs\Python\Python311\python.exe") do (
  if not defined PY if exist %%C (
    %%C -c "pass" >nul 2>&1 && set "PY=%%C"
  )
)
if not defined PY ( py -3 -c "pass" >nul 2>&1 && set "PY=py -3" )
if not defined PY ( python -c "pass" >nul 2>&1 && set "PY=python" )
if not defined PY goto :nopython

if not exist "index.html" (
  echo Building the page...
  %PY% build-local.py || goto :failed
)

%PY% server.py --open
if errorlevel 1 goto :failed

echo.
echo Server stopped. Wi-Fi sharing is off until you open this again.
timeout /t 5 >nul
exit /b 0

:nopython
echo.
echo Could not find a working Python on this computer.
echo.
echo Install it from python.org and tick "Add python.exe to PATH" during
echo setup, then open this shortcut again.
echo.
pause
exit /b 1

:failed
echo.
echo Something went wrong. The message above says what.
pause
exit /b 1
