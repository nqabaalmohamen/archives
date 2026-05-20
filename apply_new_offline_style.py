import os
import re

new_catch = """} catch (err) {
        console.warn("Offline Mode - Showing Cache");
        
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
                renderTransaction(parsed.transaction);
                
                const banner = document.getElementById('offline-banner');
                if (banner) {
                    banner.innerHTML = '<i class="fas fa-exclamation-triangle" style="margin-left:8px;"></i> تنبيه: النظام غير متصل حالياً ( قم بتحديث المتصفح او تأكيد بأنك متصل بالانترنت لتتابع معاملة مباشر اذا انتا متأكيد انك قمت بتحديث المتصفح و انك متصل بالانترنت فهذا يعني ان النقابة قد تكون خارج مواعيد العمل الرسمية من 9 ص إلى 2 م و الاجازات مثل الجمعة و الاجازات الرسمية )';
                    banner.style.background = "rgba(245,158,11,0.15)";
                    banner.style.color = "#fcd34d";
                    banner.style.borderColor = "rgba(245,158,11,0.4)";
                    banner.classList.add('active');
                    banner.style.display = 'flex';
                }
                
                const liveText = document.querySelector('.live-text');
                if (liveText) {
                    liveText.textContent = "عرض آخر حالة مؤرشفة";
                    liveText.style.color = "#f59e0b";
                }
                const liveDot = document.querySelector('.live-dot');
                if (liveDot) {
                    liveDot.style.background = "#f59e0b";
                    liveDot.style.boxShadow = "0 0 10px #f59e0b";
                    liveDot.style.animation = "livePulse 2s infinite";
                }
            } catch(e) {}
        } else {
            if (!isSilent) show('maintenance-card');
        }
    }"""

files = ['index.html', 'track.html', 'live.html', 'test_live.html']

# Regex pattern matching the old catch block structure
pattern = re.compile(
    r'\}\s*catch\s*\(err\)\s*\{[\s\S]+?console\.warn\("Offline Mode - Showing Cache"\);[\s\S]+?if\s*\(cachedData\)\s*\{[\s\S]+?\}\s*else\s*\{\s*if\s*\(\!isSilent\)\s*show\(\'maintenance-card\'\);\s*\}\s*\}'
)

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if pattern.search(content):
            content = pattern.sub(new_catch, content)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Updated offline styles in {f}")
        else:
            print(f"Pattern not found in {f}")
