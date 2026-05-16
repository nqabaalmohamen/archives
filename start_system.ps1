# Standard Start Script V6.5
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$PORT = 8002

Write-Host "Cleaning up..."
$ExistingProcess = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
if ($ExistingProcess) {
    Stop-Process -Id $ExistingProcess.OwningProcess -Force -ErrorAction SilentlyContinue
}
Stop-Process -Name "cloudflared" -Force -ErrorAction SilentlyContinue

Write-Host "Starting Django on $PORT..."
Start-Process python -ArgumentList "manage.py runserver 0.0.0.0:$PORT" -WindowStyle Minimized
Start-Sleep -Seconds 5

$TunnelLog = "$PSScriptRoot\cloudflare_temp_log.txt"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }

Write-Host "Opening Tunnel..."
$CloudflaredExe = "$PSScriptRoot\cloudflare_tunnel\cloudflared.exe"
Start-Process $CloudflaredExe -ArgumentList "tunnel --url http://localhost:$PORT" -RedirectStandardError $TunnelLog -WindowStyle Minimized

Write-Host "Waiting for URL..."
$NewURL = ""
$Counter = 0
while ($Counter -lt 30) {
    if (Test-Path $TunnelLog) {
        $Content = Get-Content $TunnelLog
        $Line = $Content | Select-String -Pattern "https://[a-zA-Z0-9-]+\.trycloudflare\.com"
        if ($Line) {
            $NewURL = [regex]::Match($Line, "https://[a-zA-Z0-9-]+\.trycloudflare\.com").Value
            break
        }
    }
    Start-Sleep -Seconds 1
    $Counter++
}

if (-not $NewURL) {
    Write-Host "Failed to get URL."
    pause
    exit
}

Write-Host "New URL: $NewURL"

Write-Host "Updating files..."
$FilesToUpdate = @("index.html", "track.html", "live.html", "archive_system\settings.py")
foreach ($File in $FilesToUpdate) {
    if (Test-Path $File) {
        $Content = Get-Content $File -Raw
        $Content = [regex]::Replace($Content, "https://[a-zA-Z0-9-]+\.trycloudflare\.com", $NewURL)
        $Content = $Content -replace "V5.5", "V6.5"
        Set-Content -Path $File -Value $Content -Encoding UTF8
        Write-Host "Updated: $File"
    }
}

Write-Host "Pushing to GitHub..."
git add .
git commit -m "Update V6.5 - Port $PORT"
git push origin main

Write-Host "System is LIVE at: $NewURL"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }
Read-Host "Press Enter to stop..."
Stop-Process -Name "cloudflared" -Force
