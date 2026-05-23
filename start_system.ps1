$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PORT = 8002

# ══════════════════════════════════════════════════════════════
# ✅ الدومين الثابت - لا يتغير أبداً
# ══════════════════════════════════════════════════════════════
$FIXED_DOMAIN = "https://goldfish-banked-valley.ngrok-free.dev"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     نظام الأرشيف - نقابة المحامين بالفيوم       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══ إيقاف أي نفق أو سيرفر سابق ═══
Write-Host "جاري إيقاف العمليات السابقة..." -ForegroundColor Yellow
Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
Stop-Process -Name cloudflared -Force -ErrorAction SilentlyContinue
$Existing = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
if ($Existing) { Stop-Process -Id ($Existing | Select-Object -ExpandProperty OwningProcess -First 1) -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 1

# ═══ تحديد IP الخادم ═══
$IP = "127.0.0.1"
$ActiveIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress
if ($ActiveIP) { $IP = $ActiveIP }

# ═══ تشغيل Django ═══
Write-Host "تشغيل النظام على $IP`:$PORT ..." -ForegroundColor Yellow
Start-Process python -ArgumentList "manage.py runserver $IP`:$PORT" -WindowStyle Normal

Start-Sleep -Seconds 4

# ═══ تشغيل Ngrok بالدومين الثابت ═══
Write-Host "تشغيل النفق الثابت..." -ForegroundColor Yellow
$NgrokExe = "$PSScriptRoot\ngrok.exe"
Start-Process $NgrokExe -ArgumentList "http --url=$FIXED_DOMAIN http://$IP`:$PORT" -WindowStyle Minimized

Start-Sleep -Seconds 4

# ═══ التحقق من أن النفق يعمل ═══
$TunnelWorking = $false
try {
    $Response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 5 -ErrorAction Stop
    if ($Response.tunnels.Count -gt 0) {
        $TunnelWorking = $true
    }
} catch {
    Write-Host "تحذير: لم يتم التحقق من النفق عبر API." -ForegroundColor Yellow
}

# ═══ تحديث Keyval.org ليكون متاحاً دائماً ═══
Write-Host "تحديث عنوان النفق..." -ForegroundColor Yellow
python update_url.py $FIXED_DOMAIN

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host " ✅ النظام يعمل بالكامل!" -ForegroundColor Green
Write-Host " 🌐 الرابط الثابت: $FIXED_DOMAIN" -ForegroundColor Cyan
Write-Host " 📱 هذا الرابط لا يتغير أبداً!" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  لا تُغلق هذه النافذة أثناء عمل النظام!" -ForegroundColor Red
Write-Host ""
Read-Host "اضغط Enter لإيقاف النظام..."

Stop-Process -Name ngrok -Force -ErrorAction SilentlyContinue
Stop-Process -Name cloudflared -Force -ErrorAction SilentlyContinue
$Existing = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue
if ($Existing) { Stop-Process -Id ($Existing | Select-Object -ExpandProperty OwningProcess -First 1) -Force -ErrorAction SilentlyContinue }

Write-Host "تم إيقاف النظام." -ForegroundColor Yellow
