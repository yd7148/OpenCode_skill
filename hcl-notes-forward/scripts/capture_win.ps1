Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W32 {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

$procName = if ($args.Count -gt 0) { $args[0] } else { "nlnotes" }
$outPng = if ($args.Count -gt 1) { $args[1] } else { "C:\Users\N00014~1\AppData\Local\Temp\opencode\notes_win.png" }
$ram = Get-Process -Name $procName -ErrorAction Stop | Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero } | Select-Object -First 1
if (-not $ram) { Write-Output "NO_WINDOW"; exit 1 }
$h = $ram.MainWindowHandle
if ([W32]::IsIconic($h)) { [W32]::ShowWindow($h, 9) | Out-Null; Start-Sleep -Milliseconds 800 }
[W32]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 700
$r = New-Object W32+RECT
[W32]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.Right - $r.Left; $ht = $r.Bottom - $r.Top
Write-Output "win $w x $ht at ($($r.Left),$($r.Top)) pid=$($ram.Id) title=$($ram.MainWindowTitle)"
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[W32]::PrintWindow($h, $hdc, 2) | Out-Null
$g.ReleaseHdc($hdc)
$bmp.Save($outPng, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "saved to $outPng"