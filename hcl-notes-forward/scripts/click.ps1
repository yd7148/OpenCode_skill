param([int]$X, [int]$Y, [string]$Action = "click")
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Mouse {
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
}
"@
$null = [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($X, $Y)
Start-Sleep -Milliseconds 150
[Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
if ($Action -eq "dblclick") {
    Start-Sleep -Milliseconds 200
    [Mouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    [Mouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
}
Write-Output "clicked $X,$Y ($Action)"