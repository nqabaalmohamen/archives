$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PORT = 8002
$Version = "V10.0 FINAL"
Write-Host "Cleaning up..."
Stop-Process -Name cloudflared -Force
$Existing = Get-NetTCPConnection -LocalPort $PORT
if ($Existing) { Stop-Process -Id $Existing.OwningProcess -Force }
Write-Host "Starting Django..."
Start-Process python -ArgumentList "manage.py runserver 0.0.0.0:$PORT" -WindowStyle Minimized
Start-Sleep -Seconds 5
$TunnelLog = "$PSScriptRoot\cloudflare_temp_log.txt"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }
Write-Host "Connecting..."
$Exe = "$PSScriptRoot\cloudflare_tunnel\cloudflared.exe"
Start-Process $Exe -ArgumentList "tunnel --url http://127.0.0.1:$PORT" -RedirectStandardError $TunnelLog -WindowStyle Minimized
$NewURL = ""
for ($i=0; $i -lt 30; $i++) {
    if (Test-Path $TunnelLog) {
        $Line = Get-Content $TunnelLog | Select-String "https://[a-zA-Z0-9-]+\.trycloudflare\.com"
        if ($Line) { $NewURL = [regex]::Match($Line, "https://[a-zA-Z0-9-]+\.trycloudflare\.com").Value; break }
    }
    Start-Sleep 1
}
if (-not $NewURL) { Write-Host "Error"; pause; exit }
Write-Host "Link: $NewURL"
$Files = @("index.html", "track.html", "live.html", "archive_system\settings.py")
foreach ($f in $Files) {
    if (Test-Path $f) {
        $c = Get-Content $f -Raw
        $c = [regex]::Replace($c, "https://[a-zA-Z0-9-]+\.trycloudflare\.com", $NewURL)
        $c = [regex]::Replace($c, "V[0-9]+\.[0-9]+(\s*FINAL)?(\s*\([^\)]+\))?", $Version)
        Set-Content $f $c -Encoding UTF8
    }
}
git add .
git commit -m "V10.0 FINAL"
git push origin main --force
Write-Host "LIVE: $NewURL"
Read-Host "Press Enter to Stop"
Stop-Process -Name cloudflared -Force
