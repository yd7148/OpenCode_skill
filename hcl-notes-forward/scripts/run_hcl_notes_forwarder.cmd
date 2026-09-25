@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" "%SCRIPT_DIR%hcl_notes_forwarder.py" %*
) else (
  python "%SCRIPT_DIR%hcl_notes_forwarder.py" %*
)
