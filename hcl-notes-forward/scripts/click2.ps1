param([int]$WinX, [int]$WinY, [int]$WinLeft, [int]$WinTop, [string]$Action = "click")
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse2 {
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
}
"@
$absX = $WinLeft + $WinX
$absY = $WinTop + $WinY
$null = [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($absX, $absY)
Start-Sleep -Milliseconds 200
[Mouse2]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[Mouse2]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
if ($Action -eq "dblclick") {
    Start-Sleep -Milliseconds 250
    [Mouse2]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [Mouse2]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
}
Write-Output "clicked abs=$absX,$absY ($Action)"