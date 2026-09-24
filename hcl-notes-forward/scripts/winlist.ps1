Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class EN {
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll")] public static extern uint GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int n);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@
$fg = [EN]::GetForegroundWindow()
$rows = foreach ($w in (Get-Process | Where-Object MainWindowHandle -ne 0 | Select-Object MainWindowHandle, ProcessName, Id)) {
    $h = $w.MainWindowHandle
    $r = New-Object EN+RECT
    [EN]::GetWindowRect($h, [ref]$r) | Out-Null
    $wdt = $r.Right - $r.Left; $hgt = $r.Bottom - $r.Top
    $sb = New-Object System.Text.StringBuilder 300
    [EN]::GetWindowText($h, $sb, 300) | Out-Null
    $title = $sb.ToString()
    $pid = 0
    [EN]::GetWindowThreadProcessId($h, [ref]$pid) | Out-Null
    [PSCustomObject]@{ Hwnd=$h; Proc=$w.ProcessName; Pid=$pid; W=$wdt; H=$hgt; Rect="[$($r.Left),$($r.Top)-$($r.Right),$($r.Bottom)]"; FG=($h -eq $fg); Title=$title }
}
$rows | Sort-Object { -$_.W * -$_.H } | Format-Table -AutoSize | Out-String -Width 250