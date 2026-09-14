param([string]$ProcName = "nlnotes")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class ZF2 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int n);
    [DllImport("user32.dll")] public static extern bool SwitchToThisWindow(IntPtr hWnd, bool fAltTab);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$p = Get-Process -Name $ProcName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
if (-not $p) { Write-Output "NO_WINDOW"; exit 1 }
$h = $p.MainWindowHandle

$fg0 = [ZF2]::GetForegroundWindow()
if ($fg0 -ne $h) {
  # minimize whatever is foreground (likely Excel/Word)
  $null = [ZF2]::ShowWindow($fg0, 6)   # SW_MINIMIZE
  Start-Sleep -Milliseconds 500
}
if ([ZF2]::IsIconic($h)) { $null = [ZF2]::ShowWindow($h, 4) }  # SW_RESTORE
Start-Sleep -Milliseconds 200
$null = [ZF2]::SwitchToThisWindow($h, $true)
Start-Sleep -Milliseconds 300
$null = [ZF2]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 500

$fg = [ZF2]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 200
[ZF2]::GetWindowText($fg, $sb, 200) | Out-Null
$r = New-Object ZF2+RECT
[ZF2]::GetWindowRect($h, [ref]$r) | Out-Null
Write-Output "notesHwnd=$h notesRect=[$($r.Left),$($r.Top)-$($r.Right),$($r.Bottom)] iconic=$([ZF2]::IsIconic($h))"
Write-Output "fg=$fg match=$($fg -eq $h) fgTitle='$($sb.ToString())'"