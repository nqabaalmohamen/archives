# ════════════════════════════════════════════════════════════
#  🚇 إعداد Cloudflare Tunnel تلقائياً - نظام الأرشيف
#  يُشغَّل هذا الملف لجعل صفحة المتابعة متاحة على الإنترنت
# ════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚇  Cloudflare Tunnel - نظام الأرشيف          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ═══ تحديد المسار ═══
$TunnelDir  = "$PSScriptRoot\cloudflare_tunnel"
$CloudflaredExe = "$TunnelDir\cloudflared.exe"
$DownloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

# ═══ إنشاء المجلد إن لم يكن موجوداً ═══
if (-not (Test-Path $TunnelDir)) {
    New-Item -ItemType Directory -Path $TunnelDir | Out-Null
}

# ═══ تنزيل cloudflared إن لم يكن موجوداً ═══
if (-not (Test-Path $CloudflaredExe)) {
    Write-Host "📥 جاري تنزيل cloudflared..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $CloudflaredExe -UseBasicParsing
        Write-Host "✅ تم التنزيل بنجاح!" -ForegroundColor Green
    } catch {
        Write-Host "❌ فشل التنزيل. تحقق من الإنترنت وأعد التشغيل." -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "✅ cloudflared موجود بالفعل." -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host " 🌐 جاري فتح النفق... انتظر ظهور الرابط أدناه" -ForegroundColor White
Write-Host " 📋 انسخ الرابط الذي يبدأ بـ  https://" -ForegroundColor Yellow
Write-Host " 📝 ثم ضعه في ملف: hosting_files\track.html" -ForegroundColor Yellow
Write-Host "    في المتغير:  const API_BASE = ""رابطك هنا"";" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
Write-Host "⚠️  لا تُغلق هذه النافذة أثناء عمل النظام!" -ForegroundColor Red
Write-Host ""

# ═══ تشغيل النفق ═══
# يشير إلى النظام الذي يعمل على البورت 8000
& $CloudflaredExe tunnel --url http://localhost:8000
