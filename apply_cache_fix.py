import os
import re

cache_js = """
let lastStatus = null;
let lastUpdate = null;
let lastDesc   = null;
let lastTitle  = null;
let lastMissingInfo = null;

async function loadTracking(isSilent = false) {
    const params = new URLSearchParams(window.location.search);
    const tr = params.get('tr');

    if (!tr) { show('welcome-card'); return; }

    // Check cache first to prevent flickering
    const cacheKey = "cache_" + tr;
    const cachedData = localStorage.getItem(cacheKey);
    
    if (cachedData && !isSilent && !lastStatus) {
        try {
            const parsed = JSON.parse(cachedData);
            renderTransaction(parsed.transaction);
        } catch(e) {}
    } else if (!isSilent && !lastStatus) {
        show('loading-card');
    }

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const res = await fetch(API_BASE + "/api/track/?tr=" + encodeURIComponent(tr) + "&v=" + Date.now() + "&cf-skip-browser-warning=1", {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!res.ok) throw new Error("Offline");

        const data = await res.json();
        if (data.success) {
            const t = data.transaction;
            
            localStorage.setItem(cacheKey, JSON.stringify({
                transaction: t,
                timestamp: new Date().toLocaleString('ar-EG')
            }));

            const hasChanged = t.current_status !== lastStatus || t.updated_at !== lastUpdate || t.description !== lastDesc || t.title !== lastTitle || t.missing_info !== lastMissingInfo;
            if (hasChanged) {
                lastStatus = t.current_status;
                lastUpdate = t.updated_at;
                lastDesc   = t.description;
                lastTitle  = t.title;
                lastMissingInfo = t.missing_info;
                renderTransaction(t);
            }
            
            const banner = document.getElementById('offline-banner');
            if (banner) {
                banner.classList.remove('active');
                banner.style.background = ""; banner.style.color = ""; banner.style.borderColor = "";
                banner.innerHTML = '<div class="m-dot"></div> النظام متصل الآن (بث مباشر)';
            }
            const liveText = document.querySelector('.live-text');
            if (liveText) { liveText.textContent = "متابعة مباشرة الآن"; liveText.style.color = "#10b981"; }
            const liveDot = document.querySelector('.live-dot');
            if (liveDot) { liveDot.style.background = "#10b981"; liveDot.style.boxShadow = "0 0 10px #10b981"; liveDot.style.animation = "livePulse 1.5s infinite"; }

        } else {
            if (!isSilent) showError(data.error || 'لم يتم العثور على هذه المعاملة.');
        }
    } catch (err) {
        console.warn("Offline Mode - Showing Cache");
        
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
                renderTransaction(parsed.transaction);
                
                const banner = document.getElementById('offline-banner');
                if (banner) {
                    banner.innerHTML = '<i class="fas fa-wifi-slash"></i> عرض آخر بيانات مسجلة (النظام غير متصل حالياً)';
                    banner.classList.add('active');
                    banner.style.background = "rgba(239, 68, 68, 0.15)";
                    banner.style.color = "#fca5a5";
                    banner.style.borderColor = "rgba(239, 68, 68, 0.4)";
                }
                
                const liveText = document.querySelector('.live-text');
                if (liveText) {
                    liveText.textContent = "بيانات مؤرشفة - " + parsed.timestamp;
                    liveText.style.color = "#94a3b8";
                }
                const liveDot = document.querySelector('.live-dot');
                if (liveDot) {
                    liveDot.style.background = "#94a3b8";
                    liveDot.style.boxShadow = "none";
                    liveDot.style.animation = "none";
                }
            } catch(e) {}
        } else {
            if (!isSilent) show('maintenance-card');
        }
    }
}
loadTracking();
setInterval(() => { loadTracking(true); }, 10000);
"""

files = ['track.html', 'index.html', 'live.html']

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace the loadTracking block
        pattern = re.compile(r'let lastStatus = null;[\s\S]+?setInterval\(\(\) => \{\s*loadTracking\(true\);\s*\}, 5000\);')
        if pattern.search(content):
            content = pattern.sub(cache_js, content)
            
            # Make sure to update the V5.0 -> V12.0 FINAL
            content = content.replace("V5.0", "V12.0 FINAL")
            
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated {f}")
        else:
            print(f"Pattern not found in {f}")
