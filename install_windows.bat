@echo off
setlocal
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

echo [ZestVoice] Starting Windows setup...

if exist "%VENV_PY%" (
  echo [ZestVoice] Existing virtual environment found.
) else (
  call :find_python || goto :error
  echo [ZestVoice] Creating virtual environment...
  call %PYTHON_EXE% %PYTHON_ARGS% -m venv .venv || goto :error
)

call "%VENV_PY%" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" || goto :python_version_error

echo [ZestVoice] Installing/updating dependencies...
call "%VENV_PY%" -m pip install --upgrade pip || goto :error
call "%VENV_PY%" -m pip install -r requirements.txt || goto :error

if not exist ".env" if exist ".env.example" (
  copy /Y ".env.example" ".env" >nul
  echo [ZestVoice] Created .env from .env.example.
  echo [ZestVoice] Set LEMONFOX_API_KEY in .env before first use.
)

echo [ZestVoice] Setup complete.
exit /b 0

:find_python
where py >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_EXE=py"
  set "PYTHON_ARGS=-3"
  exit /b 0
)

where python >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_EXE=python"
  set "PYTHON_ARGS="
  exit /b 0
)

echo [ZestVoice] Python 3.12+ was not found in PATH.
echo [ZestVoice] Install Python and re-run this script.
exit /b 1

:python_version_error
echo [ZestVoice] Python 3.12+ is required.
echo [ZestVoice] Recreate .venv with a supported Python version.
exit /b 1

:error
echo [ZestVoice] Setup failed.
exit /b 1
