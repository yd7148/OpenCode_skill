param([string]$OutPng)
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class FS2 { [DllImport("user32.dll")] public static extern int GetSystemMetrics(int i); }'
$w = [FS2]::GetSystemMetrics(0); $ht = [FS2]::GetSystemMetrics(1)
$bmp = New-Object System.Drawing.Bitmap($w, $ht)
$g = [System.Drawing.Graphics]::FromImage($bmp)
try {
  $g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
  Write-Output "copied $w x $ht"
} catch {
  Write-Output "CopyFromScreen failed: $($_.Exception.Message)"
}
$bmp.Save($OutPng, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "saved to $OutPng"