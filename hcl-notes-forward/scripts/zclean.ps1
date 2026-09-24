param([string]$KeepProc = "nlnotes")
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class MIN {
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hInsert, int x,int y,int cx,int cy,uint f);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left,Top,Right,Bottom; }
}
"@
function Get-ProcName([uint32]$pidv) { $q = Get-Process -Id $pidv -ErrorAction SilentlyContinue; if($q){$q.ProcessName}else{""} }
$keep = Get-Process -Name $KeepProc -ErrorAction Stop | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
$keepH = $keep.MainWindowHandle
$minimized = @()
$script:ignoreProcs = @("explorer","OpenCode","node","python","powershell","conhost","cmd","Code","nlnotes","chrome","msedge","tnotify")
$cb = {
  param($h, $l)
  if (-not [MIN]::IsWindowVisible($h)) { return $true }
  if ($h -eq $keepH) { return $true }
  $r = New-Object MIN+RECT
  [MIN]::GetWindowRect($h, [ref]$r) | Out-Null
  if (($r.Right - $r.Left) -lt 50 -or ($r.Bottom - $r.Top) -lt 50) { return $true }
  $pidv = 0
  [MIN]::GetWindowThreadProcessId($h, [ref]$pidv) | Out-Null
  $pn = Get-Process -Id $pidv -ErrorAction SilentlyContinue
  if (-not $pn) { return $true }
  if ($script:ignoreProcs -contains $pn.ProcessName) { return $true }
  # only minimize big overlapping windows (Office/PDF viewers etc.)
  $null = [MIN]::ShowWindow($h, 6)  # SW_MINIMIZE
  $script:minimized += "$pn.ProcessName($pidv)"
  return $true
}
$script:minimized = @()
[MIN]::EnumWindows([MIN+EnumProc]$cb, [IntPtr]::Zero) | Out-Null
Start-Sleep -Milliseconds 600
# restore & topmost & foreground notes
$null = [MIN]::ShowWindow($keepH, 4)
$HWND_TOPMOST = New-Object System.IntPtr -ArgumentList -1
$null = [MIN]::SetWindowPos($keepH, $HWND_TOPMOST, 0,0,0,0, 0x0001 -bor 0x0002 -bor 0x0040)
Start-Sleep -Milliseconds 300
$null = [MIN]::SetForegroundWindow($keepH)
Start-Sleep -Milliseconds 400
$r2 = New-Object MIN+RECT
[MIN]::GetWindowRect($keepH, [ref]$r2) | Out-Null
Write-Output "minimized: $($script:minimized -join ', ')"
Write-Output "notes rect now=[$($r2.Left),$($r2.Top)-$($r2.Right),$($r2.Bottom)]"