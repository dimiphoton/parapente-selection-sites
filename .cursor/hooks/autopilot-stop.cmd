@echo off
setlocal
REM Sous Windows, l'environnement du hook n'a pas toujours `python` sur le PATH.
if exist "%~dp0autopilot-stop.py" (
  where py >nul 2>&1
  if %ERRORLEVEL%==0 (
    py -3 "%~dp0autopilot-stop.py"
    exit /b %ERRORLEVEL%
  )
  where python >nul 2>&1
  if %ERRORLEVEL%==0 (
    python "%~dp0autopilot-stop.py"
    exit /b %ERRORLEVEL%
  )
)
echo {}
exit /b 0
