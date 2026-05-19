$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PORT = 8002

Write-Host "--- SYSTEM STARTUP ---" -ForegroundColor Cyan

Write-Host "Cleaning up..."
Stop-Process -Name cloudflared -Force
$Existing = Get-NetTCPConnection -LocalPort $PORT
if ($Existing) { Stop-Process -Id $Existing.OwningProcess -Force }

Write-Host "Starting Django..."
$IP = "192.168.1.37"
$ActiveIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
if ($ActiveIP) { $IP = $ActiveIP }

Start-Process python -ArgumentList "manage.py runserver $IP`:$PORT" -WindowStyle Normal

Start-Sleep -Seconds 5

$TunnelLog = "$PSScriptRoot\cloudflare_temp_log.txt"
if (Test-Path $TunnelLog) { Remove-Item $TunnelLog }

Write-Host "Connecting..."
$Exe = "$PSScriptRoot\cloudflare_tunnel\cloudflared.exe"
Start-Process $Exe -ArgumentList "tunnel --url http://$IP`:$PORT" -RedirectStandardError $TunnelLog -WindowStyle Minimized

$NewURL = ""
for ($i=0; $i -lt 30; $i++) {
    if (Test-Path $TunnelLog) {
        $Line = Get-Content $TunnelLog | Select-String "https://[a-zA-Z0-9-]+\.trycloudflare\.com"
        if ($Line) { $NewURL = [regex]::Match($Line, "https://[a-zA-Z0-9-]+\.trycloudflare\.com").Value; break }
    }
    Start-Sleep 1
}

if (-not $NewURL) { Write-Host "Error connecting to tunnel"; pause; exit }
Write-Host "Link: $NewURL" -ForegroundColor Green

# Update URL using Python to preserve Arabic UTF-8
python update_url.py $NewURL

# ✅ لم نعد بحاجة لرفع التحديثات لـ GitHub في كل تشغيل للنظام بفضل التوجيه الديناميكي المبتكر (Dynamic Query URL Routing)
# هذا يحل مشكلة توقف/بطء التشغيل بسبب حظر جدار الحماية المحلي لـ GitHub ويجعل النظام يفتح فوراً!
# Write-Host "Pushing to GitHub..."
# git add .
# git commit -m "V12.1 FINAL: Safe deployment using $NewURL"
# git push origin main --force
# git push origin main:gh-pages --force

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "✅ SYSTEM IS NOW FULLY OPERATIONAL" -ForegroundColor Green
Write-Host "🌐 PUBLIC LINK: $NewURL" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Keep this window and the Django window open."
Read-Host "Press Enter to SHUT DOWN everything..."

Stop-Process -Name cloudflared -Force
$Existing = Get-NetTCPConnection -LocalPort $PORT
if ($Existing) { Stop-Process -Id $Existing.OwningProcess -Force }
