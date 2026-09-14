param([string]$ProcName = "nlnotes")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class ZF3 {
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int n);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$p = Get-Process -Name $ProcName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
if (-not $p) { Write-Output "NO_WINDOW"; exit 1 }
$h = $p.MainWindowHandle
$HWND_TOPMOST = New-Object System.IntPtr -ArgumentList -1
$HWND_NOTOPMOST = New-Object System.IntPtr -ArgumentList -2
# put on top of z-order so real mouse clicks hit it instead of PDF/Excel
$flags = 0x0001 -bor 0x0002 -bor 0x0040   # SWP_NOSIZE|SWP_NOMOVE|SWP_SHOWWINDOW
$null = [ZF3]::SetWindowPos($h, $HWND_TOPMOST, 0, 0, 0, 0, $flags)
Start-Sleep -Milliseconds 400
if ([ZF3]::IsIconic($h)) { $null = [ZF3]::ShowWindow($h, 4); Start-Sleep -Milliseconds 300 }
$null = [ZF3]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 400
# try to keep it above others: cycle topmost off/on is not needed; keep TOPMOST for now
$fg = [ZF3]::GetForegroundWindow()
$r = New-Object ZF3+RECT
[ZF3]::GetWindowRect($h, [ref]$r) | Out-Null
Write-Output "notesHwnd=$h topmost set rect=[$($r.Left),$($r.Top)-$($r.Right),$($r.Bottom)] fg=$fg match=$($fg -eq $h)"