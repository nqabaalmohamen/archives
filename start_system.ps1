# Standard Start Script
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Cleaning up..."
Stop-Process -Name "cloudflared" -Force

Write-Host "Starting Django..."
Start-Process python -ArgumentList "manage.py runserver 0.0.0.0:8000" -WindowStyle Minimized
Start-Sleep -Seconds 3

$TunnelLog = "$PSScriptRoot\cloudflare_temp_log.txt"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }

Write-Host "Opening Tunnel..."
$CloudflaredExe = "$PSScriptRoot\cloudflare_tunnel\cloudflared.exe"
Start-Process $CloudflaredExe -ArgumentList "tunnel --url http://localhost:8000" -RedirectStandardError $TunnelLog -WindowStyle Minimized

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
        $UpdatedContent = [regex]::Replace($Content, "https://[a-zA-Z0-9-]+\.trycloudflare\.com", $NewURL)
        Set-Content -Path $File -Value $UpdatedContent -Encoding UTF8
        Write-Host "Updated: $File"
    }
}

Write-Host "Pushing to GitHub..."
git add .
git commit -m "Auto-update tunnel URL to $NewURL"
git push origin main

Write-Host "System is LIVE at: $NewURL"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }
Read-Host "Press Enter to stop..."
Stop-Process -Name "cloudflared" -Force
