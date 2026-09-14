param([string]$ProcName = "nlnotes")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class ZF {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int n);
}
"@
$p = Get-Process -Name $ProcName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
if (-not $p) { Write-Output "NO_WINDOW"; exit 1 }
$h = $p.MainWindowHandle
if ([ZF]::IsIconic($h)) { [ZF]::ShowWindow($h, 9) | Out-Null; Start-Sleep -Milliseconds 400 }
$wshell = New-Object -ComObject WScript.Shell
$null = $wshell.AppActivate($h)
Start-Sleep -Milliseconds 600
# belt & suspenders
[ZF]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 400
$fg = [ZF]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 200
[ZF]::GetWindowText($fg, $sb, 200) | Out-Null
Write-Output "target=$h fg=$fg fgTitle='$($sb.ToString())' match=$($fg -eq $h)"
if ($fg -ne $h) { [ZF]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 400; $fg2 = [ZF]::GetForegroundWindow(); Write-Output "after2 fg=$fg2 match=$($fg2 -eq $h)" }