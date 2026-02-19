@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"
set "VENV_PYW=.venv\Scripts\pythonw.exe"
set "FORCE_UPDATE=0"
set "USE_CONSOLE=0"

:parse_args
if "%~1"=="" goto :args_done
if /I "%~1"=="--update" set "FORCE_UPDATE=1"
if /I "%~1"=="--console" set "USE_CONSOLE=1"
shift
goto :parse_args

:args_done
if not exist "%VENV_PY%" (
  echo [ZestVoice] First run detected. Running setup...
  call "%~dp0install_windows.bat"
  if errorlevel 1 goto :error
)

if "%FORCE_UPDATE%"=="1" (
  call "%~dp0install_windows.bat"
  if errorlevel 1 goto :error
)

if "%USE_CONSOLE%"=="1" (
  call "%VENV_PY%" app.py
  exit /b %ERRORLEVEL%
)

if exist "%VENV_PYW%" (
  start "" "%VENV_PYW%" app.py
  exit /b 0
)

call "%VENV_PY%" app.py
exit /b %ERRORLEVEL%

:error
echo [ZestVoice] Could not start the application.
exit /b 1
