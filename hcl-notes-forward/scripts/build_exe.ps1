param(
  [string]$PythonExe = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
  [string]$Name = "hcl-notes-forwarder"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Entry = Join-Path $ScriptDir "hcl_notes_forwarder.py"

if (-not (Test-Path -LiteralPath $PythonExe)) {
  $PythonExe = "python"
}

& $PythonExe -m pip install --upgrade pyinstaller pillow
& $PythonExe -m PyInstaller --onefile --name $Name $Entry

Write-Host "Built executable under: $(Join-Path (Get-Location) 'dist')"
